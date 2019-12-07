import os
import math
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import csv
import numpy as np

fp = "mapSeg"
op = "mapIm"

if not os.path.exists(op):
    os.makedirs(op)

blk = 100
stp = 10

first = True


for root,dirs,files in os.walk(fp):
    for file in files:
        fcur = fp+'\\'+file
        fout = op+'\\'+file[:-4] + '.png'

        Cia = file.find("_")
        Cib = file.find("_", Cia+1)
        Cic = file.find(".", Cib)
        
        flat = int(file[Cia+1:Cib])/blk
        flon = int(file[Cib+1:Cic])/blk

        if(first):
            first = False
            latscl = flat

        with open(fcur, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            seg = np.zeros((0,2,2))
            ln = np.zeros((2,2))
            colours = np.zeros((0,3))




            i = 0
            for row in reader:
                i += 1
                lon = eval(row[0])
                lat = eval(row[1])
                col = eval(row[2])

                p1 = [lon[0],lat[0]]
                p2 = [lon[1],lat[1]]

                ln[0,:] = p1
                ln[1,:] = p2
                
                seg = np.append(seg, [ln], axis = 0)
                colours = np.append(colours, [col], axis = 0)
              

                if (i % 500 == 0):
                    print("Proscessor: ", os.getpid(), "||", i)
                   

        fig, ax = plt.subplots(frameon=False)

        ax.set_ylim(flat, flat+(stp/blk))
        ax.set_xlim(flon, flon+(stp/blk))
        
 
        
        ax.set_axis_off()
        
        fig.set_size_inches(1, 1)

        

        coll = LineCollection(seg, linewidths= .1 ,linestyle='solid', colors = colours)

        ax.add_collection(coll)
        ax.set_aspect(1/(math.cos(math.radians(latscl))))
        plt.savefig(fout, dpi = 1200, bbox_inches = 'tight', pad_inches=0, transparent=True)
        plt.close()


