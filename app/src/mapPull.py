import os
import math
import requests
import time


import itertools

from .args import * 
from .mapUtil import * 

ZOOM = 11
def tiles_to_draw(args : ArgsContainer) -> list[Tile]:
    nwcorner = (args.Nf, args.Wf, ZOOM)
    secorner = (args.Sf, args.Ef, ZOOM)

    xa, ya = deg2num(*nwcorner)
    xb, yb = deg2num(*secorner)

    tiles = [Tile(ZOOM, x, y) for x in range(xa, xb + 1) for y in range(ya, yb + 1)]

    return tiles

def request_tile(mapPullOutPath : str, tile : Tile):
    north,west  = num2deg(tile)
    swtile = Tile(tile.z, tile.x+1, tile.y+1)
    south,east = num2deg(swtile)

    get = False
            
    Ostr = mapPullOutPath + "\map_z%d_x%d_y%d.osm" % tuple(tile)
    if (not (os.path.isfile(Ostr))):
        while(get == False):
            
            
            Qstr = "https://overpass-api.de/api/interpreter?data=[bbox:%f,%f,%f,%f];" % (south, west, north, east)
            Qstr += '('
            Qstr += 'way[highway];'
            # Qstr += 'way[highway = motorway];'
            # Qstr += 'way[highway = trunk];'
            # Qstr += 'way[highway = primary];'
            # Qstr += 'way[highway = secondary];'
            # Qstr += 'way[highway = tertiary];'
            Qstr += ');(._;>;);out;'

            try:
                rs = requests.get("http://overpass-api.de/api/status")
                status_string = str(rs.content)
                    
                t_wait_end = status_string.find("seconds") -1 
                t_wait_start = status_string.find("in",t_wait_end-10,t_wait_end) +3 
                try:
                    t_wait = int(status_string[t_wait_start:t_wait_end])
                except ValueError:
                    t_wait = 0
                    
                if (t_wait > 0):
                    print("Rate Limited:", str(t_wait), "s Pause")
                    time.sleep(t_wait)
            except requests.exceptions.ConnectionError:
                time.sleep(20)
            
            print("URL:", Qstr)
            
            try:
                query_time = time.time()
                r = requests.get(Qstr, allow_redirects=True)
            
                with open(Ostr, 'wb') as f:
                    f.write(r.content)
            except requests.exceptions.ConnectionError:
                time.sleep(20)        
            
            try:
                statinfo = os.stat(Ostr)
                print("Tile Size:", statinfo.st_size, "Bytes")           
                if(not(statinfo.st_size in range(700,725))):
                    get = True
                elif(statinfo.st_size == 711):
                        print('Rate Limited: 25s Pause')
                        time.sleep(25)
                        print('Continuing')
            except OSError:
                pass

def pull_tiles(args : ArgsContainer):
    tiles = tiles_to_draw(args)

    num_tiles = len(tiles)
    for i,tile in enumerate(tiles):
        print("Fetching Tile: ", str(i), "of", str(num_tiles))
        request_tile(args.mapPullOutPath, tile)