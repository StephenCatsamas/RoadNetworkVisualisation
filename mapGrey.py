import args
import os
import numpy as np
import matplotlib.pyplot as plt
import pyvips

# def makeGrey(file):
    # fcur = args.mapGreyPath+'\\'+file
    # fout = args.mapGrayMaskPath + '\\' + 'Grey.png'
        
    # imcur = Image.open(fcur)
      
    # outimg = Image.new('RGBA', imcur.size, (25,25,25))
    # outimg.save(fout)

def grey(file):
    fcur = args.mapGreyInPath+'\\'+file
    fout = args.mapGreyOutPath+'\\'+file
    fgry = args.mapGrayMaskPath + '\\' + 'Grey.png'
       
    print("Greying: ", str(os.getpid()).zfill(6), "||", fcur)
    
    im_forground  = pyvips.Image.new_from_file(fcur)
    im_background = im_forground.new_from_image( [25,25,25])
    
    im_grey = im_background.composite2(im_forground, 'over')
    im_grey.write_to_file(fout)
    # imcur = Image.open(fcur)
    # imgry = Image.open(fgry)
    
    
    # imgry.alpha_composite(imcur)
    # imgry.save(fcur)
 