import args
import os
import numpy as np
import pyvips

def order_key(file):
    Cia = file.find("_")
    Cib = file.find("_", Cia+1)
    Cic = file.find(".", Cib)
    
    flat = int(file[Cia+1:Cib])/args.blk
    flon = int(file[Cib+1:Cic])/args.blk

    return -(flat+90)*1000000+(flon+180)

def concat():
    rowlist = list()

    ny = len(range(args.S,args.N,args.stp))
    nx = len(range(args.W,args.E,args.stp))

    for root,dirs,files in os.walk(args.mapConcatInPath):
       
       files.sort(key = order_key)
       
    images = [pyvips.Image.new_from_file(args.mapConcatInPath+'\\'+file) for file in files]
    
    outimg = pyvips.Image.arrayjoin(images, across = nx)
    
    outimg.write_to_file(args.mapConcatOutPath)
