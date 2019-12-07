import args
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def concat():
    outimg = np.zeros((4,4,4))
    rowlist = list()

    ny = len(range(args.S,args.N,args.stp))
    nx = len(range(args.W,args.E,args.stp))

    for root,dirs,files in os.walk(args.mapConcatInPath):
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
            
            print(rowimg.shape)
             
    for i, rowimg in enumerate(rowlist):

        if i != 0:
            outimg = np.concatenate((outimg,rowimg), axis = 0)
            
        if i == 0:
            outimg = rowimg

    plt.imsave(args.mapConcatOutPath, outimg)
