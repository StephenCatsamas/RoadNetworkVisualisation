import math
import os
import csv

class ArgsContainer():
    def __init__(self,file = 'args_lst.txt'):
        self.update_args(file = file)
        
    def update_args(self,file = 'args_lst.txt'):
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, file)
        with open(fp, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            args_dict = {}
            for row in reader:
                if row == []:
                    continue
                if row[0][0] == '#':
                    continue
                args_dict[row[0].strip()] = row[1].strip()

        self.colour_mode = str(args_dict['colour_mode']).strip('"')

        self.flush_map_cache = bool(args_dict['flush_map_cache'] == 'True')
        self.do_cull = bool(args_dict['do_cull'] == 'True')
        self.force_seg = bool(args_dict['force_seg'] == 'True')

        self.Nf =  float(args_dict['Nf'])
        self.Sf =  float(args_dict['Sf'])
        self.Ef =  float(args_dict['Ef'])
        self.Wf =  float(args_dict['Wf'])

        self.tile_size = float(args_dict['tile_size'])

        self.res = float(args_dict['res'])

        self.seg_width = float(args_dict['seg_width'])

        self.threads = int(args_dict['threads'])

        self.mapPullOutPath = str(args_dict['mapPullOutPath']).strip('"')

        self.mapStreetInPath = str(args_dict['mapStreetInPath']).strip('"')
        self.mapStreetOutPath = str(args_dict['mapStreetOutPath']).strip('"')

        self.mapSegInPath = str(args_dict['mapSegInPath']).strip('"')
        self.mapSegOutPath = str(args_dict['mapSegOutPath']).strip('"')

        self.mapDrawInPath = str(args_dict['mapDrawInPath']).strip('"')
        self.mapDrawOutPath = str(args_dict['mapDrawOutPath']).strip('"')

        self.mapGreyInPath = str(args_dict['mapGreyInPath']).strip('"')
        self.mapGreyOutPath = str(args_dict['mapGreyOutPath']).strip('"')
        self.mapGrayMaskPath = str(args_dict['mapGrayMaskPath']).strip('"')

        self.mapConcatInPath = str(args_dict['mapConcatInPath']).strip('"')

        self.mapConcatOutPath = str(args_dict['mapConcatOutPath']).strip('"')

        #################################################################################
        self.blk = 1000

        self.folders = list()

        self.folders.append(self.mapPullOutPath)
        self.folders.append(self.mapStreetInPath)
        self.folders.append(self.mapStreetOutPath)
        self.folders.append(self.mapSegInPath)
        self.folders.append(self.mapSegOutPath)
        self.folders.append(self.mapDrawInPath)
        self.folders.append(self.mapDrawOutPath)
        self.folders.append(self.mapGreyInPath)
        self.folders.append(self.mapGreyOutPath)
        self.folders.append(self.mapGrayMaskPath)
        self.folders.append(self.mapConcatInPath)

        if not self.do_cull:
            self.mapSegInPath = self.mapStreetInPath

        self.stp = int(round(self.tile_size,3)*self.blk)

        self.N = int(math.floor(self.blk*round(self.Nf,3)))
        self.S = int(math.floor(self.blk*round(self.Sf,3)))
        self.E = int(math.floor(self.blk*round(self.Ef,3)))
        self.W = int(math.floor(self.blk*round(self.Wf,3)))

