import args as ag
import os
import math
import requests
import time


def pull():
    args = ag.ArgsContainer()
    
    if (args.S > args.N) or (args.W > args.E):
        print('###############')
        print("Bounds Inverted")
        print('###############')

    dlat = args.N - args.S
    dlon = args.E - args.W

    tiles = int(math.ceil(dlat/args.stp) * math.ceil(dlon/args.stp))

    for lat in range(args.S,args.N,args.stp):
        for lon in range(args.W,args.E,args.stp):
            get = False
            
            Ostr = args.mapPullOutPath
            Ostr += "\map_"
            Ostr += str(lat)
            Ostr += '_'
            Ostr += str(lon)
            Ostr += '.osm'
            if (not (os.path.isfile(Ostr))):
                while(get == False):
                    
                    
                    Qstr = "https://overpass-api.de/api/interpreter?data=[bbox:"
                    Qstr += str(lat/args.blk)
                    Qstr += ','
                    Qstr += str(lon/args.blk)
                    Qstr += ','
                    Qstr += str((lat+args.stp)/args.blk)
                    Qstr += ','
                    Qstr += str((lon+args.stp)/args.blk)
                    Qstr += '];('
                    #Qstr += 'way[highway];'
                    Qstr += 'way[highway = motorway];'
                    Qstr += 'way[highway = trunk];'
                    Qstr += 'way[highway = primary];'
                    Qstr += 'way[highway = secondary];'
                    Qstr += ');(._;>;);out;'
                    
                    
                    tile_num = int(((lat-args.S)/args.stp) * math.ceil(dlon/args.stp) + ((lon-args.W)/args.stp))+1
                    
                    
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
                    
                    
                    print("Fetching Tile: ", str(tile_num), "of", str(tiles))
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
                
                    