import math

##colour mode 'angle', 'width'
colour_mode = 'width'

##if true deletes old files when run
flush_map_cache = False
do_cull = False
force_seg = False

##coordinate bounging boxes in lat long degrees #max resolution 0.001 degree
Nf =  -37.500
Sf =  -38.500
Ef =  145.500
Wf =  144.500

##download block size | units deg
tile_size = 0.5

##decimal scale factor | have as many zeros as decimal places in bounding box coordinates
blk = 1000
stp = int(round(tile_size,3)*blk)

##final image reslution aritbrary units
res = 8000
##plot sement width
seg_width = 0.04

##muliprocessing threads
threads = 4

mapPullOutPath = "maps"

mapStreetInPath = "maps"
mapStreetOutPath = "mapStreet"

mapSegInPath = "mapStreet"
mapSegOutPath = "mapSeg"

mapDrawInPath = "mapSeg"
mapDrawOutPath = "mapIm"

mapGreyInPath = "mapIm"
mapGreyOutPath = "mapGrey"
mapGrayMaskPath = "mapMask"

mapConcatInPath = "mapGrey"
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
folders.append(mapGreyInPath)
folders.append(mapGreyOutPath)
folders.append(mapGrayMaskPath)
folders.append(mapConcatInPath)

if not do_cull:
    mapSegInPath = mapStreetInPath


N = int(math.floor(blk*round(Nf,3)))
S = int(math.floor(blk*round(Sf,3)))
E = int(math.floor(blk*round(Ef,3)))
W = int(math.floor(blk*round(Wf,3)))
