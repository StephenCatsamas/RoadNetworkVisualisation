import os
import sys
import time
from functools import partial
from multiprocessing import Pool


from .args import *
from . import mapPull
from . import mapStreet
from . import mapSeg
from . import mapDraw
from . import mapBitmap



def run(args: ArgsContainer): 
    if args.flush_map_cache:
        for folder in args.render_folders:
            for root,dirs,files in os.walk(folder):
                for file in files:
                    print("Removing: ", root + '\\' + file)
                    os.remove(root + '\\' + file)
        
    for folder in args.render_folders:
        if not os.path.exists(folder):
            print()
            os.makedirs(folder)

    # mapPull.pull(args)
    mapPull.pull_tiles(args)
    
    if args.do_cull:
        for root,dirs,files in os.walk(args.mapStreetInPath):
            with Pool(args.threads) as p:
                p.map(partial(mapStreet.cull_streets, args = args), files,1)
        
        p.close()
        p.join()

    if args.force_seg:##note that this makes it a do seg rather than force
        for root,dirs,files in os.walk(args.mapSegInPath):
            with Pool(args.threads) as p:
                p.map(partial(mapSeg.seg, args = args), files,1)
        p.close()
        p.join()

    mapDraw.init()
    for root,dirs,files in os.walk(args.mapDrawInPath):
        for file in files:
            mapDraw.draw(file,args)
        # with Pool(args.threads) as p:
        #     p.map(partial(mapDraw.draw, args = args), files,1)
    p.close()
    p.join()
     
    mapBitmap.concat(args)

    mapBitmap.crop(args)
    print('Finished')
 
if __name__ == '__main__':
    run()
    
    
    
    