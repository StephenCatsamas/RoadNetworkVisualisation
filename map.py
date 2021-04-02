import args
import mapPull
import mapStreet
import mapSeg
import mapDraw
import mapBitmap

import os
from multiprocessing import Pool


if __name__ == '__main__':

    if args.new:
        for folder in args.folders:
            for root,dirs,files in os.walk(folder):
                for file in files:
                    print("Removing: ", root + '\\' + file)
                    os.remove(root + '\\' + file)
        
    for folder in args.folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    mapPull.pull()

    for root,dirs,files in os.walk(args.mapStreetInPath):
        with Pool(4) as p:
            p.map(mapStreet.cullStreets, files,1)
    
    p.close()
    p.join()

    for root,dirs,files in os.walk(args.mapSegInPath):
        with Pool(4) as p:
            p.map(mapSeg.segThread, files,1)
    p.close()
    p.join()
 
    for root,dirs,files in os.walk(args.mapDrawInPath):
        with Pool(4) as p:
            p.map(mapDraw.draw, files,1)

    p.close()
    p.join()
    
    for root,dirs,files in os.walk(args.mapGreyInPath):
        
        with Pool(4) as p:
            p.map(mapBitmap.grey, files)
    
    p.close()
    p.join()
     
    mapBitmap.concat()
    
    
    