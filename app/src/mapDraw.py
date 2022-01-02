import os
import pyvips
import csv
import math
import time

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
    

def draw(file, args):
        
        fcur = args.mapDrawInPath+'\\'+file
        fname = file[:-4]
        fout = args.mapDrawOutPath+'\\'+ fname + '\\'
        # make output directory
        if not os.path.exists(fout):
            os.makedirs(fout)

        Cia = file.find("_")
        Cib = file.find("_", Cia+1)
        Cic = file.find(".", Cib)
        
        flat = int(file[Cia+1:Cib])/args.blk
        flon = int(file[Cib+1:Cic])/args.blk
        
        linecolls = list()

        with open(fcur, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            n_rows = sum(1 for row in reader)       
            
        with open(fcur, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            # seg = np.zeros((0,2,2))
            # ln = np.zeros((2,2))
            # colours = np.zeros((0,3))

            lines = []

            i = 0

            for row in reader:
                i += 1
                lon = eval(row[0])
                lat = eval(row[1])
                col = eval(row[2])
                
               

                p1 = (lat[0],lon[0])
                p2 = (lat[1],lon[1])
                
                l = Line(p1,p2,args.seg_width, col)
                
                lines.append(l)
                
                if (i % 6000 == 0):
                    print("Drawing:", str(os.getpid()).zfill(6), "||", i, "of", n_rows)        


        print(flat,flon)
        view = View((flat,flat-(args.stp/args.blk),flon+(args.stp/args.blk),flon),args.res)
        tik = time.perf_counter()
        maptoolslib.drawlines(lines,view,fout)
        tok = time.perf_counter()
        rust_draw_concat(view,fout,fname)
        tuk = time.perf_counter()
        print("Time to draw: ", tok - tik)
        print("Time to concat: ", tuk - tok)
        print("Total: ", tuk - tik)


def rust_draw_concat(view,fout,fname):
    print("Joining")
    
    for root,dirs,files in os.walk(fout):
        
        files.sort(key = row_major)
        print(files)
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


def get_xtiles(files):
    ords = [get_tile(file) for file in files]
    xords = [x for x,y in ords]
    return max(xords)-min(xords)+1

def get_tile(file): 
    Cia = file.find("[")
    Cib = file.find(",", Cia+1)
    Cic = file.find("]", Cib)
    
    xtile = float(file[Cia+1:Cib])
    ytile = float(file[Cib+1:Cic])
    return(xtile,ytile)

def row_major(file):
    x,y = get_tile(file)
    return (-y,x)

