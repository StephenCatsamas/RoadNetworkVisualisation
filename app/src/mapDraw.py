import os
import math
import csv
import numpy as np
import time

from . import maptoolslib

class Line():
    def __init__(self, to = None, fm = None, width = None, colour = None):
        self.to = (0.0, 0.0) if to == None else to
        self.fm = (0.0, 1.0) if fm == None else fm
        self.width = 0.1 if width == None else width
        self.colour = (1.0,1.0,1.0) if colour == None else colour


    # lines = [Line((i/20,0.8), (0,0), 0.01, (i/20,0,1-(i/20))) for i in range(20)]

    # maptoolslib.drawlines(lines, "1.png")

def compatify(p,view):
    lat,lon,range = view

    x = (2*(p[0]-lon))/range -1
    y = (2*(p[1]-lat))/range -1
    # print(x,y)
    return (x, y)
    

def draw(file, args):
        
        fcur = args.mapDrawInPath+'\\'+file
        fout = args.mapDrawOutPath+'\\'+file[:-4] + '.png'

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
                
                view = (flat,flon,args.stp/args.blk)

                p1 = compatify((lon[0],lat[0]),view)
                p2 = compatify((lon[1],lat[1]),view)
                
                l = Line(p1,p2,args.seg_width, col)
                
                lines.append(l)
                
                if (i % 6000 == 0):
                    print("Drawing:", str(os.getpid()).zfill(6), "||", i, "of", n_rows)        
                    
                # if (i % 12000 == 0):
                    # linecolls.append(LineCollection(seg, linewidths= args.seg_width ,linestyle='solid', colors = colours))
                    
                    # seg = np.zeros((0,2,2))
                    # ln = np.zeros((2,2))
                    # colours = np.zeros((0,3))
            
           
            # linecolls.append(LineCollection(seg, linewidths= args.seg_width ,linestyle='solid', colors = colours))
    
        # ax.set_aspect(1/(math.cos(math.radians(args.Nf))))
            
        maptoolslib.drawlines(lines,fout)


