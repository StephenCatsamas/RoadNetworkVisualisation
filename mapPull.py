import os
import math
import requests

Nf = -34.8
Sf = -35.1
Ef =  138.8
Wf =  138.4

blk = 100
stp = 10

N = int(math.floor(blk*Nf))
S = int(math.floor(blk*Sf))
E = int(math.floor(blk*Ef))
W = int(math.floor(blk*Wf))

for lat in range(S,N,stp):
    for lon in range(W,E,stp):
        get = False
        while(get == False):
            Qstr = "https://overpass-api.de/api/interpreter?data=[bbox:"
            Qstr += str(lat/blk)
            Qstr += ','
            Qstr += str(lon/blk)
            Qstr += ','
            Qstr += str((lat+stp)/blk)
            Qstr += ','
            Qstr += str((lon+stp)/blk)
            Qstr += '];way[highway];(._;>;);out;'

            print(Qstr)

            r = requests.get(Qstr, allow_redirects=True)

            pdf_url = r.url
            
            Ostr = "maps\map_"
            Ostr += str(lat)
            Ostr += '_'
            Ostr += str(lon)
            Ostr += '.osm'
            
            with open(Ostr, 'wb') as f:
                f.write(r.content)
                
            statinfo = os.stat(Ostr)
            print(statinfo.st_size)           
            if(statinfo.st_size > 2000 or statinfo.st_size < 1500):
                if(not(statinfo.st_size in range(700,750))):
                    get = True
                
        