import args
import os
import pyvips

def order_key(file):
    Cia = file.find("_")
    Cib = file.find("_", Cia+1)
    Cic = file.find(".", Cib)
    
    flat = int(file[Cia+1:Cib])/args.blk
    flon = int(file[Cib+1:Cic])/args.blk

    return -(flat+90)*1000000+(flon+180)

def grey(file):
    fcur = args.mapGreyInPath+'\\'+file
    fout = args.mapGreyOutPath+'\\'+file
    fgry = args.mapGrayMaskPath + '\\' + 'Grey.png'
       
    print("Greying:", str(os.getpid()).zfill(6), "||", fcur)
    
    im_forground  = pyvips.Image.new_from_file(fcur)
    im_background = im_forground.new_from_image( [25,25,25])
    
    im_grey = im_background.composite2(im_forground, 'over')
    im_grey.write_to_file(fout)

def concat():
    rowlist = list()

    ny = len(range(args.S,args.N,args.stp))
    nx = len(range(args.W,args.E,args.stp))

    print("Concatinating")
    
    for root,dirs,files in os.walk(args.mapConcatInPath):
       
       files.sort(key = order_key)
       
    images = [pyvips.Image.new_from_file(args.mapConcatInPath+'\\'+file) for file in files]
    
    outimg = pyvips.Image.arrayjoin(images, across = nx)
    
    outimg.write_to_file(args.mapConcatOutPath)
