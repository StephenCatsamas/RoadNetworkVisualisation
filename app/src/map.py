from . import mapPull
from . import mapStreet
from . import mapSeg
from . import mapDraw
from . import mapBitmap
from functools import partial

import os
import sys
from multiprocessing import Pool


def run(args): 

    if args.flush_map_cache:
        for folder in args.folders:
            for root,dirs,files in os.walk(folder):
                for file in files:
                    print("Removing: ", root + '\\' + file)
                    os.remove(root + '\\' + file)
        
    for folder in args.folders:
        if not os.path.exists(folder):
            print()
            os.makedirs(folder)

    mapPull.pull(args)
    
    if args.do_cull:
        for root,dirs,files in os.walk(args.mapStreetInPath):
            with Pool(args.threads) as p:
                p.map(partial(mapStreet.cull_streets, args = args), files,1)
        
        p.close()
        p.join()
        

    for root,dirs,files in os.walk(args.mapSegInPath):
        with Pool(args.threads) as p:
            p.map(partial(mapSeg.seg_thread, args = args), files,1)
    p.close()
    p.join()
 
    for root,dirs,files in os.walk(args.mapDrawInPath):
        with Pool(args.threads) as p:
            p.map(partial(mapDraw.draw, args = args), files,1)

    p.close()
    p.join()
     
    mapBitmap.concat(args)
    print('Finished')
 
if __name__ == '__main__':
    run()
    
    
    
    