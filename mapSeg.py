import args
import os
import math
import colorsys
import lxml.etree as ET
import csv

def idSort(enum):
    return(int(enum[1]))

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
    fcur = args.mapSegInPath+'\\'+file
    fout = args.mapSegOutPath+'\\' +file[:-4] + '.csv'
    
    # if (not (os.path.isfile(fout))):
    
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
            if (i % 1000 == 0):
                print("Proscessor: ", os.getpid(), "||", i, "out of" , len(root))
        
            if child.tag == 'way':
            
                latlst = list()
                lonlst = list()
                
                for tag in child:
                    if tag.get("ref") != None:
                        id = tag.get("ref")
                        
                        coord = nodeDict[id]


                        latlst.append(float(coord[0]))
                        lonlst.append(float(coord[1]))
                
                
                segPlot(lonlst,latlst, writer)
                
                
                
                
            # for child in root:
         
                
                    
                # cidx = 1
                # nodeList = list()
                
                # if (child.tag == "way"):
                    # for tag in child:
                        # if (tag.get('k') == 'highway'):
                            # for tog in child:
                               # if(tog.get("ref") != None):
                                # NextId = tog.get("ref")
                                
                                # nodeList.append(NextId)
                                
                            # idxNodeList = list(enumerate(nodeList)) 
                                
                            # idxNodeList.sort(key = idSort)
                            
                            # lnth = len(idxNodeList)

                            # latlst = [None] * lnth
                            # lonlst = [None] * lnth
                            
                            # for key, NextId in idxNodeList:

                                # for idx, chold in enumerate(root[cidx-1:]): 
                                    # ats = chold.attrib
                                    # id = ats.get("id")
                                    # if (id == NextId):
                                        # lat = ats.get("lat")
                                        # lon = ats.get("lon")
                                        # cidx += idx
                                        
                                        # try:
                                            # latlst[key] = float(lat)
                                            # lonlst[key] = float(lon)
                                          
                                        # except TypeError:
                                            # pass
                                        # break
                            # break        
                    
         
        