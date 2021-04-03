import args as ag
import mapPull
import mapStreet
import mapSeg
import mapDraw
import mapBitmap

import os
import sys
from multiprocessing import Pool

args = ag.ArgsContainer()
def update_args():
    global args
    args.update_args()

def run(): 
    update_args_all()
        
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

    mapPull.pull()
    
    if args.do_cull:
        for root,dirs,files in os.walk(args.mapStreetInPath):
            with Pool(args.threads) as p:
                p.map(mapStreet.cull_streets, files,1)
        
        p.close()
        p.join()
        

    for root,dirs,files in os.walk(args.mapSegInPath):
        with Pool(args.threads) as p:
            p.map(mapSeg.seg_thread, files,1)
    p.close()
    p.join()
 
    for root,dirs,files in os.walk(args.mapDrawInPath):
        with Pool(args.threads) as p:
            p.map(mapDraw.draw, files,1)

    p.close()
    p.join()
    
    for root,dirs,files in os.walk(args.mapGreyInPath):
        
        with Pool(args.threads) as p:
            p.map(mapBitmap.grey, files)
    
    p.close()
    p.join()
     
    mapBitmap.concat()
    print('Finished')
 
def update_args_all():
    update_args()
    modules = [mapPull, mapStreet, mapSeg, mapDraw, mapBitmap]
    for modules in modules:
        modules.update_args()
 
if __name__ == '__main__':
    run()
    
    
    
    