import args
import mapPull
import mapStreet
import mapSeg
import mapDraw
import mapGrey
import mapConcat

import os
from multiprocessing import Pool


for folder in args.folders:
    if not os.path.exists(folder):
        os.makedirs(folder)


if __name__ == '__main__':

  #  mapPull.pull()
        
    for root,dirs,files in os.walk(args.mapStreetInPath):
        with Pool(4) as p:
            p.map(mapStreet.cullStreets, files)
    p.join()
    p.close()

    for root,dirs,files in os.walk(args.mapSegInPath):
        with Pool(4) as p:
            p.map(mapSeg.segThread, files)
    p.join()
    p.close()

    for root,dirs,files in os.walk(args.mapDrawInPath):
        with Pool(4) as p:
            p.map(mapDraw.draw, files)

    p.join()
    p.close()

    for root,dirs,files in os.walk(args.mapGreyPath):
        with Pool(4) as p:
            p.map(mapGrey.grey, files)
    
    p.join()
    p.close()
     
    mapConcat.concat()
    
    
    