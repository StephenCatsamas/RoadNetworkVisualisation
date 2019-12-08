import math

Nf =  49.10
Sf =  48.60
Ef =  2.70
Wf =  1.90

blk = 100
stp = 10

res = 1200

mapPullOutPath = "maps"

mapStreetInPath = "maps"
mapStreetOutPath = "mapStreet"

mapSegInPath = "mapStreet"
mapSegOutPath = "mapSeg"

mapDrawInPath = "mapSeg"
mapDrawOutPath = "mapIm"

mapGreyPath = "mapIm"
mapGrayMaskPath = "mapMask"

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
folders.append(mapGrayMaskPath)
folders.append(mapConcatInPath)


N = int(math.floor(blk*Nf))
S = int(math.floor(blk*Sf))
E = int(math.floor(blk*Ef))
W = int(math.floor(blk*Wf))