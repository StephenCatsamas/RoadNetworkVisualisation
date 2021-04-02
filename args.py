import math

##colour mode 'angle', 'width'
colour_mode = 'width'

##if true deletes old files when run
new = False
force_seg = False

##coordinate bounging boxes in lat long degrees
Nf =  -10.0
Sf =  -45.0
Ef =  155.0
Wf =  112.0

##decimal scale factor | have as many zeros as decimal places in bounding box coordinates
blk = 100
##download block size | units (deg/blk)
stp = 500

##final image reslution aritbrary units
res = 2000

##vips path
##vipsPath = "C:\Program Files\vips\vips-dev-8.10\bin"

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
