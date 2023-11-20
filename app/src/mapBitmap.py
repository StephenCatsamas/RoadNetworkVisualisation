import os
import re

import pyvips

from .args import *
from .mapUtil import *

def row_major(file: str):
    zoom,xtile,ytile = [int(num) for num in re.findall(r'\d+', file)]

    return ytile,xtile

def grey(file : str, args: ArgsContainer):
    fcur = args.mapGreyInPath+'\\'+file
    fout = args.mapGreyOutPath+'\\'+file
       
    print("Greying:", str(os.getpid()).zfill(6), "||", fcur)
    
    im_forground  = pyvips.Image.new_from_file(fcur)
    im_background = im_forground.new_from_image( [25,25,25])
    
    im_grey = im_background.composite2(im_forground, 'over')
    im_grey.write_to_file(fout)

def concat(args : ArgsContainer):

    xs = []
    for file in os.listdir(args.mapConcatInPath):
        zoom,xtile,ytile = [int(num) for num in re.findall(r'\d+', file)]
        xs.append(xtile)

    nx = max(xs) - min(xs) + 1

    print("Concatinating")
    
    files = os.listdir(args.mapConcatInPath)
    files.sort(key = row_major)
       
    #flush cache to reload images from file
    cs = pyvips.voperation.cache_get_max()
    pyvips.voperation.cache_set_max(0)
    pyvips.voperation.cache_set_max(cs)

    images = [pyvips.Image.new_from_file(args.mapConcatInPath+'\\'+file) for file in files]

    #the reason we join rows first is because arrayjoin requires equally sized images but our tiles are not due to perspective.
    image_rows = [pyvips.Image.arrayjoin(images[i:i+nx], across = nx) 
            for i in range(0,len(images),nx)]

    #join rows
    outimg = image_rows[0]
    for image_row in image_rows[1:]:
        outimg = outimg.join(image_row, 'vertical')
    
    outimg.write_to_file(args.mapConcatOutPath)


def crop(args : ArgsContainer):

    tiles = []
    for file in os.listdir(args.mapConcatInPath):
        zoom,xtile,ytile = [int(num) for num in re.findall(r'\d+', file)]
        tiles.append(Tile(zoom,xtile,ytile))

    xs = [t.x for t in tiles]
    ys = [t.x for t in tiles]



    ref = num2deg(Tile(zoom,min(xs),min(ys)))

    nwcorner = (args.Nf, args.Wf)
    secorner = (args.Sf, args.Ef)

    top, left = deg2pix(nwcorner, ref, ZOOM) 
    bottom, right = deg2pix(secorner, ref, ZOOM) 

    map = pyvips.Image.new_from_file(args.mapConcatOutPath)

    map = map.crop(left, top, right-left, top-bottom)

    map.write_to_file(args.mapConcatOutPath)

