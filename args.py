import math

Nf =  51.70
Sf =  51.25
Ef =  0.30
Wf =  -0.55

blk = 100
stp = 3

res = 300

mapPullOutPath = "maps"

mapStreetInPath = "maps"
mapStreetOutPath = "mapStreet"

mapSegInPath = "maps"
mapSegOutPath = "mapSeg"

mapDrawInPath = "mapSeg"
mapDrawOutPath = "mapIm"

mapGreyPath = "mapIm"

mapConcatInPath = "mapIm"
mapConcatOutPath = "afinal.png"

#################################################################################
folders = list()

folders.append(mapPullOutPath)
folders.append(mapStreetInPath)
folders.append(mapStreetOutPath)
folders.append(mapSegInPath)
folders.append(mapSegOutPath)
folders.append(mapDrawInPath)
folders.append(mapDrawOutPath)
folders.append(mapGreyPath)
folders.append(mapConcatInPath)


N = int(math.floor(blk*Nf))
S = int(math.floor(blk*Sf))
E = int(math.floor(blk*Ef))
W = int(math.floor(blk*Wf))