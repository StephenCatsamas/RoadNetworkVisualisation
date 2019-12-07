import args
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def grey(file):
    fcur = args.mapGreyPath+'\\'+file
        
    imcur = mpimg.imread(fcur)
    
    y = imcur.shape[0]
    x = imcur.shape[1]  
    
    print("Proscessor: ", os.getpid(), "||", fcur)
    
    for i in range(y):
        for j in range(x):
            for k in range(3):
                imcur[i,j,k] = imcur[i,j,k]*imcur[i,j,3] + .1*(1-imcur[i,j,3])
                
            imcur[i,j,3] = 1
            
    plt.imsave(fcur, imcur)
    
    