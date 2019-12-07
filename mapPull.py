import args
import os
import math
import requests


def pull():

    for lat in range(args.S,args.N,args.stp):
        for lon in range(args.W,args.E,args.stp):
            get = False
            while(get == False):
                print('asd')
            
                Qstr = "https://overpass-api.de/api/interpreter?data=[bbox:"
                Qstr += str(lat/args.blk)
                Qstr += ','
                Qstr += str(lon/args.blk)
                Qstr += ','
                Qstr += str((lat+args.stp)/args.blk)
                Qstr += ','
                Qstr += str((lon+args.stp)/args.blk)
                Qstr += '];way[highway];(._;>;);out;'

                print(Qstr)

                r = requests.get(Qstr, allow_redirects=True)

                pdf_url = r.url
                
                Ostr = args.mapPullOutPath
                Ostr += "\map_"
                Ostr += str(lat)
                Ostr += '_'
                Ostr += str(lon)
                Ostr += '.osm'
                
                with open(Ostr, 'wb') as f:
                    f.write(r.content)
                    
                statinfo = os.stat(Ostr)
                print(statinfo.st_size)           
                if(not(statinfo.st_size in range(700,750))):
                    get = True
                
        