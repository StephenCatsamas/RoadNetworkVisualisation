import os
import pyvips


def row_major(file):
    Cia = file.find("_")
    Cib = file.find("_", Cia+1)
    Cic = file.find(".", Cib)
    
    flat = float(file[Cia+1:Cib])
    flon = float(file[Cib+1:Cic])

    return -flat,flon

def grey(file, args):
    fcur = args.mapGreyInPath+'\\'+file
    fout = args.mapGreyOutPath+'\\'+file
    fgry = args.mapGrayMaskPath + '\\' + 'Grey.png'
       
    print("Greying:", str(os.getpid()).zfill(6), "||", fcur)
    
    im_forground  = pyvips.Image.new_from_file(fcur)
    im_background = im_forground.new_from_image( [25,25,25])
    
    im_grey = im_background.composite2(im_forground, 'over')
    im_grey.write_to_file(fout)

def concat(args):
    rowlist = list()

    ny = len(range(args.S,args.N,args.stp))
    nx = len(range(args.W,args.E,args.stp))

    print("Concatinating")
    
    for root,dirs,files in os.walk(args.mapConcatInPath):
       
       files.sort(key = row_major)
       
    images = [pyvips.Image.new_from_file(args.mapConcatInPath+'\\'+file) for file in files]
    
    outimg = pyvips.Image.arrayjoin(images, across = nx)
    
    outimg.write_to_file(args.mapConcatOutPath)
