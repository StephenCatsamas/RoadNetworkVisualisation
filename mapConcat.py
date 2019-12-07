import args
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


fp = "mapIm"
op = "final.png"

first = True

lats = list()
lons = list()

for root,dirs,files in os.walk(fp):
    for file in files:
        fcur = fp+'\\'+file
        fout = op+'\\'+file[:-4] + '.png'

        Cia = file.find("_")
        Cib = file.find("_", Cia+1)
        Cic = file.find(".", Cib)
        
        flat = int(file[Cia+1:Cib])/args.blk
        flon = int(file[Cib+1:Cic])/args.blk
        
        if (first):
            first = False
            
            Metaimg = mpimg.imread(fcur)
            y = Metaimg.shape[0]
            x = Metaimg.shape[1]             
        
        if(not (flat in lats)):
            lats.append(flat)
        if(not (flon in lons)):
            lons.append(flon)
            
    ny = len(lats)
    nx = len(lons)

    dx = nx*x
    dy = ny*y
    
    outimg = np.full((dy,dx,4), 0.1)
    
    outimg[:,:,3] = 1
    
    print(outimg.shape)
    print(ny, " ", nx)
    idx = 0
    ni = 0
    nj = 0
    
    for file in files:
        fcur = fp+'\\'+file
        
        imcur = mpimg.imread(fcur)
        
        ni = idx // nx
        nj = idx % nx
        
        iost = ni * y
        jost = nj * x
        
        print(ni, " ", nj)
        
        for i in range(y):
            for j in range(x):
                for k in range(3):
                    outimg[i+iost,j+jost,k] = imcur[i,j,k]*imcur[i,j,3] + .1*(1-imcur[i,j,3])
                
                

        idx += 1
    plt.imsave(op, outimg)