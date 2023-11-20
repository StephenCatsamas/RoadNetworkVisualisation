import math
import os
import csv

class ArgsContainer():

    def __init__(self,file = 'lstarg.cfg'):
        self.load_args(file = file) 
    
    def load_args(self,file = 'lstarg.cfg'):
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, file)
        with open(fp, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            self.filedict = {}
            for row in reader:
                if row == []:
                    continue
                if row[0][0] == '#':
                    continue
                self.filedict[row[0].strip()] = row[1].strip()
        self.dict2name()       
        
        ##############################################################################

        self.render_folders = list()

        self.render_folders.append(self.mapPullOutPath)
        self.render_folders.append(self.mapStreetInPath)
        self.render_folders.append(self.mapStreetOutPath)
        self.render_folders.append(self.mapSegInPath)
        self.render_folders.append(self.mapSegOutPath)
        self.render_folders.append(self.mapDrawInPath)
        self.render_folders.append(self.mapDrawOutPath)
        self.render_folders.append(self.mapGreyInPath)
        self.render_folders.append(self.mapGreyOutPath)
        self.render_folders.append(self.mapGrayMaskPath)
        self.render_folders.append(self.mapConcatInPath)

        self.slippy_folders = list()
        self.slippy_folders.append(self.mapTileCachePath)

        if not self.do_cull:
            self.mapSegInPath = self.mapStreetInPath

        
        
    
    def save_args(self,file = 'lstarg.cfg'):
        self.name2dict()
    
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, file)
        with open(fp, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for key in self.filedict.keys():
                writer.writerow([key,self.filedict[key]])
        
    def dict2name(self):
        self.colour_mode = str(self.filedict['colour_mode']).strip('"')

        self.flush_map_cache = bool(self.filedict['flush_map_cache'] == 'True')
        self.do_cull = bool(self.filedict['do_cull'] == 'True')
        self.force_seg = bool(self.filedict['force_seg'] == 'True')

        self.Nf =  float(self.filedict['Nf'])
        self.Sf =  float(self.filedict['Sf'])
        self.Ef =  float(self.filedict['Ef'])
        self.Wf =  float(self.filedict['Wf'])

        self.res = float(self.filedict['res'])

        self.seg_width = float(self.filedict['seg_width'])

        self.threads = int(self.filedict['threads'])

        self.mapPullOutPath = str(self.filedict['mapPullOutPath']).strip('"')

        self.mapStreetInPath = str(self.filedict['mapStreetInPath']).strip('"')
        self.mapStreetOutPath = str(self.filedict['mapStreetOutPath']).strip('"')

        self.mapSegInPath = str(self.filedict['mapSegInPath']).strip('"')
        self.mapSegOutPath = str(self.filedict['mapSegOutPath']).strip('"')

        self.mapDrawInPath = str(self.filedict['mapDrawInPath']).strip('"')
        self.mapDrawOutPath = str(self.filedict['mapDrawOutPath']).strip('"')

        self.mapGreyInPath = str(self.filedict['mapGreyInPath']).strip('"')
        self.mapGreyOutPath = str(self.filedict['mapGreyOutPath']).strip('"')
        self.mapGrayMaskPath = str(self.filedict['mapGrayMaskPath']).strip('"')

        self.mapConcatInPath = str(self.filedict['mapConcatInPath']).strip('"')
        self.mapConcatOutPath = str(self.filedict['mapConcatOutPath']).strip('"')

        self.mapTileCachePath = str(self.filedict['mapTileCachePath']).strip('"')

    def name2dict(self):
        self.filedict['colour_mode'] = '"' + self.colour_mode + '"'
        self.filedict['flush_map_cache'] = str(self.flush_map_cache)
        self.filedict['do_cull'] = str(self.do_cull)
        self.filedict['force_seg'] = str(self.force_seg)

        self.filedict['Nf'] = str(self.Nf)
        self.filedict['Sf'] = str(self.Sf)
        self.filedict['Ef'] = str(self.Ef)
        self.filedict['Wf'] = str(self.Wf)
        
        
        self.filedict['res'] = str(self.res)
        self.filedict['seg_width'] = str(self.seg_width)
        self.filedict['threads'] = str(self.threads)

        self.filedict['mapPullOutPath'] = '"' + self.mapPullOutPath + '"'
        
        self.filedict['mapStreetInPath'] = '"' + self.mapStreetInPath + '"'
        self.filedict['mapStreetOutPath'] = '"' + self.mapStreetOutPath + '"'
        
        self.filedict['mapSegInPath'] = '"' + self.mapSegInPath + '"'
        self.filedict['mapSegOutPath'] = '"' + self.mapSegOutPath + '"'

        self.filedict['mapDrawInPath'] = '"' + self.mapDrawInPath + '"'
        self.filedict['mapDrawOutPath'] = '"' + self.mapDrawOutPath + '"'
        
        self.filedict['mapGreyInPath'] = '"' + self.mapGreyInPath + '"'
        self.filedict['mapGreyOutPath'] = '"' + self.mapGreyOutPath + '"'
        self.filedict['mapGrayMaskPath'] = '"' + self.mapGrayMaskPath + '"'
        
        self.filedict['mapConcatInPath'] = '"' + self.mapConcatInPath + '"'
        self.filedict['mapConcatOutPath'] = '"' + self.mapConcatOutPath + '"'

        self.filedict['mapTileCachePath'] = '"' + self.mapTileCachePath + '"'

