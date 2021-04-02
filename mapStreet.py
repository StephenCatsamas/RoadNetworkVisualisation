import args
import os
import lxml.etree as ET


def cullStreets(file):
    fcur = args.mapStreetInPath+'\\'+file
    fout = args.mapStreetOutPath+'\\'+file

    if (not (os.path.isfile(fout))):

        print("Culling: ", str(os.getpid()).zfill(6), "||", fcur)

        myMap = ET.parse(fcur)

        #root = myMap.getroot()

        # nodeIndx = 0
        # nodeMap = list()

        # for child in root:
            # if child.tag == 'node':
                # child.set("id", str(nodeIndx))
                # nodeIndx += 1
            
            # if child.tag == 'way':
                # child.set("id", str(wayIndx))
                # wayIndx += 1

        myMap.write(fout)



        