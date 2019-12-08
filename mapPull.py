import args
import os
import math
import requests
import time


def pull():

    if (args.S > args.N) or (args.W > args.E):
        print('###############')
        print("Bounds Inverted")
        print('###############')

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
                    Qstr += '];way[highway];(._;>;);out;'

                    print(Qstr)
                    try:
                        r = requests.get(Qstr, allow_redirects=True)
                        
                        
                    
                        with open(Ostr, 'wb') as f:
                            f.write(r.content)
                    except requests.exceptions.ConnectionError:
                        time.sleep(20)
                                       
                    
                    try:
                        statinfo = os.stat(Ostr)
                        print(statinfo.st_size)           
                        if(not(statinfo.st_size in range(700,725))):
                            get = True
                    except OSError:
                        pass
                
        