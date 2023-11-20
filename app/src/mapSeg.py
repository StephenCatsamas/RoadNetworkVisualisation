import os
import math
import colorsys
import lxml.etree as ET
from array import array
import time

from . import maptoolslib


def idSort(enum):
    return(int(enum[1]))

def angle_colour(minilon,minilat):

    Dlon = minilon[0] - minilon[1]
    Dlat = minilat[0] - minilat[1]
    
    X = math.cos(math.radians(minilat[1])) * Dlon
    Y = Dlat
    
    ang = math.atan2(X,Y)
    
    H = (4*ang/(2*math.pi)) % 1
    S = .6
    V = 1
    return H,S,V
    
def width_colour(width):

    colour_map = {
    'motorway': (180,1,1),
    'trunk': (20,.9,1),
    'primary': (50,.9,.6),
    'secondary': (48,.9,.5),
    'tertiary': (57,.9,.4),
    'unclassified': (0,0,.3),
    'residential': (179,.9,.2),
    #
    'motorway_link': (26,1,1),
    'trunk_link': (33,.9,.86),
    'primary_link': (39,.9,.71),
    'secondary_link': (48,.9,.56),
    'tertiary_link': (57,.9,.45)
    }#
    # 'living_street': ,
    # 'service':,
    # 'pedestrian':,
    # 'track':,
    # 'raceway':,
    # #
    # 'footway':,
    # 'bridleway':,
    # 'steps':,
    # 'corridor':,
    # 'path':,
    # #
    # 'cycleway':,
    # #
    # 'proposed':,
    # 'construction':,
    # 'disused':,
    # #
    # 'bus_stop':,
    # 'elevator':
    # 'platform':,
    # 'services':,
    # 'traffic_island':,
    # #
    # }
    
    try:
        H,S,V = colour_map[width]
    except KeyError:
        H,S,V = (271,.9,.23)
    
    return (H/360),S,V
    
def colour(args,minilon,minilat,width):
    
    if args.colour_mode == 'angle':
        H,S,V = angle_colour(minilon,minilat)
    elif args.colour_mode == 'width':
        H,S,V = width_colour(width)
    else:
        raise ValueError("Invalid Colour Mode")
        
    return colorsys.hsv_to_rgb(H,S,V)

def seg_plot(args,lonlst,latlst,width, outfile):
    for i,lat in enumerate(latlst):
        if i < len(latlst)-1:
        
            minilat = latlst[i:i+2]
            minilon = lonlst[i:i+2]
            
            col = colour(args,minilon,minilat,width)

            to = (minilat[0],minilon[0])
            fm = (minilat[1],minilon[1])

            fbin = array('f', to+fm+col)
            fbin.tofile(outfile)

def seg(file, args):
    fin = args.mapSegInPath+'\\'+file
    fout = args.mapSegOutPath+'\\' +file[:-4] + '.seg'
    
    # implement caching
    if (not (os.path.isfile(fout)) or args.force_seg):
        tik = time.time()
        maptoolslib.segfile(fin,fout)
        tok = time.time()
        print("Time to seg: ", tok - tik)
