import args
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def OrderKey(file):
    Cia = file.find("_")
    Cib = file.find("_", Cia+1)
    Cic = file.find(".", Cib)
    
    flat = int(file[Cia+1:Cib])/args.blk
    flon = int(file[Cib+1:Cic])/args.blk

    return -(flat+90)*1000000+(flon+180)

def concat():
    outimg = np.zeros((4,4,4))
    rowlist = list()

    ny = len(range(args.S,args.N,args.stp))
    nx = len(range(args.W,args.E,args.stp))

    for root,dirs,files in os.walk(args.mapConcatInPath):
       
       files.sort(key = OrderKey)
       
       for i,file in enumerate(files):

            fcur = args.mapConcatInPath+'\\'+file
                       
            imcur = mpimg.imread(fcur)
            
            ri = i % nx
            
            if ri != 0:
                rowimg = np.concatenate((rowimg,imcur), axis = 1)
            if ri == 0:
                rowimg = imcur
            
            if(ri == nx-1):
                rowlist.append(rowimg)
            
            print('Concatinating: ', rowimg.shape)
             
    for i, rowimg in enumerate(rowlist):

        if i != 0:
            outimg = np.concatenate((outimg,rowimg), axis = 0)
            
        if i == 0:
            outimg = rowimg

    plt.imsave(args.mapConcatOutPath, outimg)
