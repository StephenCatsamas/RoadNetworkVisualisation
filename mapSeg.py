import os
import math
import colorsys
import lxml.etree as ET
import matplotlib.pyplot as plt
import csv
from multiprocessing import Pool

fp = "mapStreet"
op = "mapSeg"

def colour(minilon,minilat):
    Dlon = minilon[0] - minilon[1]
    Dlat = minilat[0] - minilat[1]
    
    X = math.cos(math.radians(minilat[1])) * Dlon
    Y = Dlat
    
    ang = math.atan2(X,Y)
    
    H = (4*ang/(2*math.pi)) % 1
    S = .6
    V = 1
    
    return colorsys.hsv_to_rgb(H,S,V)

def segPlot(lonlst,latlst, writer):
    for i,lat in enumerate(latlst):
        if i < len(latlst)-1:
        
            minilat = latlst[i:i+2]
            minilon = lonlst[i:i+2]
            
            col = colour(minilon,minilat)

            writer.writerow([minilon,minilat,col])

def segThread(file):
    fcur = fp+'\\'+file
    fout = op+'\\'+file[:-4] + '.csv'
    
    with open(fout, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        myMap = ET.parse(fcur)

        root = myMap.getroot()

        plt.figure()
        ax = plt.axes()

        ax.set_facecolor((0.1,0.1,0.1))

        i=0
        latlst = list()
        lonlst = list()
        highset = set()
            

        for child in root:
            
            i += 1
            if (i % 200 == 0):
                print("Proscessor: ", os.getpid(), "||", i, "out of" , len(root))
            
            if (child.tag == "way"):
                for tag in child:
                    if (tag.get('k') == 'highway'):
                        for tog in child:
                           if(tog.get("ref") != None):
                            NextId = tog.get("ref")
                                                        
                            for chold in root:
                                ats = chold.attrib
                                id = ats.get("id")
                                if (id == NextId):
                                    lat = ats.get("lat")
                                    lon = ats.get("lon")
                                    try:
                                        latlst.append(float(lat))
                                        lonlst.append(float(lon))
                                    except TypeError:
                                        pass
                                
                segPlot(lonlst,latlst, writer)
                latlst = list()
                lonlst = list()

if __name__ == '__main__':

    for root,dirs,files in os.walk(fp):
        with Pool(4) as p:
            p.map(segThread, files)
        