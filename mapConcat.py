import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


fp = "mapIm"
op = "final.png"

N = 0
S = 0
E = 0
W = 0


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
        
        flat = int(file[Cia+1:Cib])/10
        flon = int(file[Cib+1:Cic])/10
        
        if (first):
            first = False
            N = flat
            S = flat
            E = flon
            W = flon
            
            Metaimg = mpimg.imread(fcur)
            y = Metaimg.shape[0]
            x = Metaimg.shape[1]
        
        if (N < flat):
            N = flat
        if (S > flat):
            S = flat
        if (E < flon):
            E = flon 
        if (W > flon):
            W = flat               
        
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
    print(nx, " ", ny)
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
                    outimg[i+iost,j+jost,k] = imcur[i,j,k]*imcur[i,j,3] + outimg[i+iost,j+jost,k]*(1-imcur[i,j,3])
                
                

        idx += 1
    plt.imsave(op, outimg)