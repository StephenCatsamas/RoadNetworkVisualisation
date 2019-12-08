import args
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def makeGrey(file):
    print("Grey Mask")
    fcur = args.mapGreyPath+'\\'+file
    fout = args.mapGrayMaskPath + '\\' + 'Grey.png'
        
    imcur = Image.open(fcur)
      
    outimg = Image.new('RGBA', imcur.size, (25,25,25))
    outimg.save(fout)

def grey(file):
    fcur = args.mapGreyPath+'\\'+file
    fgry = args.mapGrayMaskPath + '\\' + 'Grey.png'
       
    print("Proscessor: ", os.getpid(), "||", fcur)
    
    imcur = Image.open(fcur)
    imgry = Image.open(fgry)
    
    imgry.paste(imcur, (0,0), imcur)
    imgry.save(fcur)
 