import os
import math
import requests

Nf = -37.8
Sf = -37.9
Ef =  145.0
Wf =  144.9

N = int(math.floor(10*Nf))
S = int(math.floor(10*Sf))
E = int(math.floor(10*Ef))
W = int(math.floor(10*Wf))

for lat in range(S,N,2):
    for lon in range(W,E,2):
        get = False
        while(get == False):
            Qstr = "https://overpass-api.de/api/interpreter?data=[bbox:"
            Qstr += str(lat/10)
            Qstr += ','
            Qstr += str(lon/10)
            Qstr += ','
            Qstr += str(lat/10 + 0.2)
            Qstr += ','
            Qstr += str(lon/10 + 0.2)
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
            if(statinfo.st_size > 2000):
                get = True
                
        