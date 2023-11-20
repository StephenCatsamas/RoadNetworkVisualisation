import os
import pyvips
import csv
import math
import time
import re


from .args import *
from .mapUtil import *
from . import maptoolslib

class Line():
    def __init__(self, to = None, fm = None, width = None, colour = None):
        self.to = (0.0, 0.0) if to == None else to
        self.fm = (0.0, 1.0) if fm == None else fm
        self.width = 0.1 if width == None else width
        self.colour = (1.0,1.0,1.0) if colour == None else colour

class View():
    def __init__(self, bounds = None, res = None):
        self.bounds = (1.0,-1.0,1.0,-1.0) if bounds == None else bounds
        self.res = 512.0 if res == None else res

def compatify(p,view):
    lat,lon,range = view

    x = (2*(p[0]-lon))/range -1
    y = (2*(p[1]-lat))/range -1
    # print(x,y)
    return (x, y)

def init():
    maptoolslib.graphics_init()

def draw(file, args : ArgsContainer):
        
        fcur = args.mapDrawInPath+'\\'+file
        fname = file[:-4]
        fout = args.mapDrawOutPath+'\\'+ fname + '\\'
         # make output directory
        if not os.path.exists(fout):
            os.makedirs(fout)

        zoom,xtile,ytile = [int(num) for num in re.findall(r'\d+', file)]

        
        north,west = num2deg(Tile(zoom,xtile,ytile))    
        south,east = num2deg(Tile(zoom,xtile+1,ytile+1))    

        view = View((north,south,east,west),args.res)
        tik = time.time()
        maptoolslib.drawfile(fcur,view,fout, args.seg_width)
        tok = time.time()
        rust_draw_concat(view,fout,fname)
        tuk = time.time()
        print("Time to draw: ", tok - tik)
        print("Time to concat: ", tuk - tok)
        print("Total: ", tuk - tik)


def rust_draw_concat(view,fout,fname):
    print("Joining")
    
    for root,dirs,files in os.walk(fout):
        
        files.sort(key = row_major)
        nx = get_xtiles(files)

    images = [pyvips.Image.new_from_file(fout+file) for file in files]
    
    outimg = pyvips.Image.arrayjoin(images, across = nx)
    #crop image
    (N,S,E,W) = view.bounds
    (width,height) = deg2pix((S,E),view)
    outimg = outimg.crop(0,0,width,height)
    #save image
    outimg.write_to_file(fout+'/../'+fname+'.tiff')

    for root,dirs,files in os.walk(fout):
        for file in files:
            os.remove(root+file)
    os.rmdir(fout)

def deg2pix(deg, view):
    (lat, lon) = deg
    (slat, _elat, _elon, slon) = view.bounds
    zl = view.res

    y = math.degrees(secint(lat, slat)) * zl

    x = (lon - slon) * zl

    return (x, y)

def sectan(z):
    v = (1/math.cos(z)) + math.tan(z)
    # if v < 0:
        # raise ValueError
    return v

#only for a,b in (-pi/2 to pi/2)
def secint(a,b):
    a = math.radians(a)
    b = math.radians(b)
    up = sectan(b)
    down = sectan(a)
    return (math.log(up) - math.log(down))


def get_xtiles(files : [str]) -> int:
    xs = [[int(num) for num in re.findall(r'\d+', file)][1] for file in files]
    return max(xs)-min(xs)+1

def get_surface(file : str) -> (int,int): 
    xtile,ytile = [int(num) for num in re.findall(r'\d+', file)]
    
    return (xtile,ytile)

def row_major(file : str) -> (int,int):
    x,y = get_surface(file)
    return (y,x)

