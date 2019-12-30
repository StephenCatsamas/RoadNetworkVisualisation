import math

##if true deletes old files when run
new = True

##coordinate bounging boxes in lat long degrees
Nf =  45.8
Sf =  45.2
Ef =  -72.8
Wf =  -74.2

##decimal scale factor | have as many zeros as decimal places in bounding box coordinates
blk = 100
##download block size | units (deg/blk)
stp = 20

##final image reslution aritbrary units
res = 2000

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
##final image output
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
