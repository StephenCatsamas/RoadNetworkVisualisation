import args as ag
import os
import math
import colorsys
import lxml.etree as ET
import csv

args = ag.ArgsContainer()
def update_args():
    global args
    args.update_args()

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

def seg_plot(args,lonlst,latlst,width, writer):
    for i,lat in enumerate(latlst):
        if i < len(latlst)-1:
        
            minilat = latlst[i:i+2]
            minilon = lonlst[i:i+2]
            
            col = colour(args,minilon,minilat,width)

            writer.writerow([minilon,minilat,col])




def seg_thread(file):

    fcur = args.mapSegInPath+'\\'+file
    fout = args.mapSegOutPath+'\\' +file[:-4] + '.csv'
    
    if (not (os.path.isfile(fout)) or args.force_seg):
    
        with open(fout, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            myMap = ET.parse(fcur)
            root = myMap.getroot()

            nodeKeys = list()
            
            for child in root:
                if child.tag == 'node':
                    nodeKeys.append(child.get('id'))

            nodeDict = dict.fromkeys(nodeKeys)
            
            for child in root:
                if child.tag == 'node':
                    nodeDict[child.get('id')] = (child.get('lat'), child.get('lon'))
            
            i=0
            
            for child in root:
            
                i += 1
                if (i % 5000 == 0):
                    print("Segmenting:", str(os.getpid()).zfill(6), "||", i, "of" , len(root))
            
                if child.tag == 'way':
                
                    latlst = list()
                    lonlst = list()
                    
                    for tag in child:
                        if tag.get("ref") != None:
                            id = tag.get("ref")
                            
                            coord = nodeDict[id]


                            latlst.append(float(coord[0]))
                            lonlst.append(float(coord[1]))
                            continue
                        if tag.get('k') == 'highway':
                            width = tag.get('v')
                    
                    seg_plot(args,lonlst,latlst,width, writer)
