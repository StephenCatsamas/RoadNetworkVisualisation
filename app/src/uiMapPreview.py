import math
import requests
import pyvips
import itertools
import threading
import os
from queue import Queue,LifoQueue
import time
import random

from .mapUtil import *

def row_major(tile):
    zoom,x,y = tile
    return x,y
    
def col_major(tile):
    zoom,x,y = tile
    return y,x

class TileCache():
    def __init__(self, parent, cache_path):
        self.tiles = {}
        self.fetcher = Fetcher(parent, cache_path)
        self.tile_queue = []
        ##maybe in we need more performance we will also cache the sitch
        # self.stich_tiles = None
        # self.stich = None
        self.max_cache_size = 2048
        
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, '../ico/loadingtile.png')
        self.loading_tile = pyvips.Image.new_from_file(fp)
    
    def add_tile(self,tile,tilecont):
        if tile not in self.tile_queue:
            self.tile_queue.append(tile)
        self.tiles[tile] = tilecont
        if len(self.tile_queue) >= self.max_cache_size:
            remove = self.tile_queue.pop(0)
            self.tiles.pop(remove)
            
    def badtile(self,tile):
        z,x,y = tile
        numtiles = 2**z
        if (0 <= x < numtiles) and (0 <= y < numtiles):
            return False
        else:
            return True
   
    def tilemod(self,tile):
        z,x,y = tile
        
        x = x % 2**z
        return (z,x,y)
   
    def get_tile(self,tile):
        tile = self.tilemod(tile)
    
        if self.recieved(tile):
            return self.tiles[tile][1]
        if self.badtile(tile):
            return self.loading_tile
        if not self.requesting(tile):
            self.request(tile)
        return self.loading_tile
    
    def request(self,tile):
        self.fetcher.inbox.put(tile)
        if not self.fetcher.thread.is_alive():
            self.fetcher.thread.start()
        self.add_tile(tile, ('requested', None))

    def requesting(self, tile):
        if tile in self.tiles:
            status = self.tiles[tile][0]
            return True if status == 'requested' else False
        return False
    
    def recieved(self, tile):
        while(not self.fetcher.outbox.empty()):
            tilecont = self.fetcher.outbox.get_nowait()
            self.add_tile(tilecont[0],('recieved',tilecont[1]))
    
        if tile in self.tiles:
            status = self.tiles[tile][0]
            if status == 'recieved':
                return True          
        return False
            
    def uncached_tiles(self, tiles):
        return [tile for tile in tiles if tile not in self.tiles]  

class Fetcher():
    def __init__(self, parent, cache_path):
        self.inbox = LifoQueue()#issue the bottom will fill up with very old tiles which we no longer need
        self.outbox = Queue()
        self.thread = threading.Thread(target=self.fetch, daemon = True)
        self.map = parent
        self.cache_path = cache_path
        self.num_cached_files = len([f for f in os.listdir(self.cache_path) if os.path.isfile(os.path.join(self.cache_path, f))])
        self.max_num_cached_files = 0x8000

        self.prune_disk_cache()
    
    def fetch(self):
        while True:
            tile = self.inbox.get()
            tile_fp = self.cache_path + "/_z%d_x%d_y%d.png" % tile
            if os.path.isfile(tile_fp):
                tile_data = pyvips.Image.new_from_file(tile_fp)
            else:
                url_string = "https://tile.openstreetmap.org/%d/%d/%d.png" % tile 
                headers = {"User-Agent": "RoadNetworkVisualisation/0.dev"}
                print(url_string)
                img_data = requests.get(url_string, headers = headers).content

                if self.num_cached_files > self.max_num_cached_files:
                    self.prune_disk_cache()

                with open(tile_fp, "wb") as tilef:
                    tilef.write(img_data)
                    self.num_cached_files += 1

                tile_data = pyvips.Image.new_from_buffer(img_data, "")
                
            self.outbox.put((tile,tile_data))
            self.map.Refresh()

    def prune_disk_cache(self):

        files = [f for f in os.listdir(self.cache_path) if os.path.isfile(os.path.join(self.cache_path, f))]

        for file in files:
            file_path = os.path.join(self.cache_path, file)
            if os.path.exists(file_path):
                file_age = time.time() - os.path.getctime(file_path)
                if file_age > 7 * 24 * 60 * 60:  # 7 days in seconds
                    os.remove(file_path)

        files = [f for f in os.listdir(self.cache_path) if os.path.isfile(os.path.join(self.cache_path, f))]

        if(len(files) > self.max_num_cached_files//2):
            print(len(files))
            random.shuffle(files)
            for file in files[0:len(files)//2]:
                file_path = os.path.join(self.cache_path, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            




class SlippyMap():
    def __init__(self, parent, cache_path):
        self.tileCache = TileCache(parent, cache_path)
        self.rezoom = True
        
        #server thread
        # self.zoom
        # self.screen_size
        # self.screen_bounds
        # self.selection_bounds
        # self.autozoom()
        # self.map
        # self.map_bounds
        # self.tiles = []
        
        self.tilesize = 256
    
    #finds lat and lon from screen space pixel
    def pix2deg(self, pix, ref = None):
        if ref is None:
            ref = (self.screen_bounds[0],self.screen_bounds[3])
        return pix2deg(pix, ref, self.zoom) 
    
    #find screen space pixel from lat and lon
    def deg2pix(self, deg, ref = None):
        if ref is None:
            ref = (self.screen_bounds[0], self.screen_bounds[3])
        return deg2pix(deg, ref, self.zoom)    
            
    def zoomlimit(self):
        if self.zoom > 12:
            self.zoom = 12
            return True
        if self.zoom < 0:
            self.zoom = 0
            return True
        return False
    
    def zoomupdate(self, dir, pos):
        
        ref = self.pix2deg(pos)
    
        width,height = self.screen_size
        
        self.zoom += dir
        if not self.zoomlimit():
            sNc,sWc = self.pix2deg((0,0)-pos, ref)
            sSc,sEc = self.pix2deg((width,height)-pos, ref)
            candidate_bounds = (sNc,sSc, sEc, sWc)

            if(self.validbounds(candidate_bounds)):
                self.screen_bounds = candidate_bounds
            else:
                self.zoom -= dir
                print("zoom locked")
            
        
    
    def validbounds(self, bounds):
        N,S,E,W = bounds
        
        maxlat = math.degrees(math.atan(math.sinh(math.pi)))
        
        if N > maxlat:
            return False
        if S < -maxlat:
            return False
        return True
    
    def getselectionpix(self):
        slN,slS,slE,slW = self.selection_bounds
        
        slWp,slNp = self.deg2pix((slN,slW))
        slEp,slSp = self.deg2pix((slS,slE))
        
        return (slNp,slSp, slEp, slWp)
            
    def setselectionpix(self, pos, corner):
        x,y = pos
        
        slNc, slSc, slEc, slWc = self.selection_bounds
        
        if corner == 'NW':
            slNc,slWc = self.pix2deg((x,y))
        elif corner == 'SE':
            slSc,slEc = self.pix2deg((x,y))
                
        if slWc < -180:
            slWc += 360
            slEc += 360
        if slWc > 180:
            slWc -= 360
            slEc -= 360
                
        candidate_bounds = (slNc,slSc, slEc, slWc)

        if(self.validbounds(candidate_bounds)):
            self.selection_bounds = candidate_bounds
        else:
            print("drag locked")
    
    def drag(self,pxmove : tuple[int,int]):

        sN,sS,sE,sW = self.screen_bounds
        
        NWp = self.deg2pix((sN,sW))
        SEp = self.deg2pix((sS,sE))
        
        NWpn = (NWp[0]-pxmove[0], NWp[1]-pxmove[1])
        SEpn = (SEp[0]-pxmove[0], SEp[1]-pxmove[1])
        
        sNc,sWc = self.pix2deg(NWpn)
        sSc,sEc = self.pix2deg(SEpn)
                
        if sWc < -180:
            sWc += 360
            sEc += 360
        if sWc > 180:
            sWc -= 360
            sEc -= 360
                
        candidate_bounds = (sNc,sSc, sEc, sWc)

        if(self.validbounds(candidate_bounds)):
            self.screen_bounds = candidate_bounds
        else:
            print("scroll locked")
        
    def make_preview(self, size):
        self.screen_size = size
    
        if self.rezoom:
            self.autozoom()
        
        tiles,grid = self.find_needed_tiles()
        
        self.render_basemap(tiles,grid)
        
        self.crop()
        self.draw_bounding_box()
        
        return self.map
    
    def draw_bounding_box(self):
        N,S,E,W = self.selection_bounds
        
        Wpix,Npix = self.deg2pix((N,W))
        Epix,Spix = self.deg2pix((S,E))
        
        svg = '<svg width="%d" height="%d">' % (self.map.width, self.map.height)
        svg += '<path d="M0,0  h%d v%d h-%d z ' % (self.map.width, self.map.height, self.map.width)
        svg +='M%d,%d v%d h%d v-%d z" ' % (Wpix,Npix,Spix-Npix, Epix-Wpix, Spix-Npix)
        svg += 'stroke="black" fill="grey" fill-opacity="0.3"   />' 
        svg += '</svg>'
        # print(svg)
        overlay = pyvips.Image.svgload_buffer(bytes(svg, 'utf-8'))
       
        self.map = self.map.composite2(overlay, 'over')
    
    def render_basemap(self,tiles,grid):
        xTiles,yTiles = grid
   
        tiles.sort(key = col_major)
        image_tiles = [self.tileCache.get_tile(tile) for tile in tiles]
        
        self.map = pyvips.Image.arrayjoin(image_tiles, across = xTiles)
        
        zoom,x,y = tiles[0]
        N,W = num2deg(x,y,zoom)
        zoom,x,y = tiles[-1]
        S,E = num2deg(x+1, y+1, zoom)
        
        self.map_bounds = (N,S,E,W)
       
        # tileCache.stich.write_to_file("stich.png")
    
    def find_needed_tiles(self):
        xSize,ySize = self.screen_size
        jump = self.tilesize
        
        tiles = []
        
        xords = itertools.chain(range(0, xSize, jump),[xSize])
        yords = itertools.chain(range(0, ySize,jump), [ySize])
        
        coords = itertools.product(xords,yords)
        
        for x,y in coords:                
            N,W = self.pix2deg((x,y))
           
            xtile,ytile = deg2num(N,W,self.zoom)
            
            newtile = (self.zoom,xtile,ytile)
            if newtile not in tiles:
                tiles.append(newtile) 
        
        xs = {x for z,x,y in tiles}
        ys = {y for z,x,y in tiles}
        
        grid = (len(xs),len(ys))
        return tiles,grid
    
    def crop(self):        
        width,height = self.screen_size
        mN,mS,mE,mW = self.map_bounds
        sN,sS,sE,sW = self.screen_bounds
        slN,slS,slE,slW = self.selection_bounds
        
        
        xofst,yofst = self.deg2pix((mN,mW))
        xofst = round(xofst)
        yofst = round(yofst)
        
        pN,pW = self.deg2pix((slN,slW))
        pS,pE = self.deg2pix((slS,slE))
        

        self.map = self.map.crop(-xofst, -yofst, width, height)
    
    #find zoom level for selection automatically
    def autozoom(self):
        xSize,ySize = self.screen_size
        N,S,E,W = self.selection_bounds
        ##determine zoom
        zx = math.log2((360/256) * (xSize / (E - W)))
        zy = math.log2((360/256) * (ySize / math.degrees(secint(S,N))))
        
        zoom = min(zx,zy)
        zoom = math.floor(zoom-0.2)
        
        self.zoom = zoom
        self.zoomlimit()
        ##############
        ##get screen bounds
        width,height = self.screen_size

        Wp,Np = self.deg2pix((N,W),(N,W))
        Ep,Sp = self.deg2pix((S,E),(N,W))
        
        sNp = (Np + Sp - height)/2
        sSp = (Np + Sp + height)/2
        sEp = (Ep + Wp + width)/2
        sWp = (Ep + Wp - width)/2

        
        sN,sW = self.pix2deg((sWp, sNp),(N,W))
        sS,sE = self.pix2deg((sEp, sSp),(N,W))
        

        #############
        self.screen_bounds = (sN,sS,sE,sW)


    # def fetch_tile(self, tile):
        # self.fetcher.inbox.put(tile)
        
        # ##return waiting data
        # tile_data = pyvips.Image.new_from_file('test.png')
        # text = pyvips.Image.text("z:%d\nx:%d\ny:%d" % tile, width = 256, height = 256, dpi = 100)[0]
        # tile_data = tile_data.composite2(text, 'over')
        # tile_data = tile_data.draw_rect([127], 0,0,256,256)

        # return tile_data



if __name__ == "__main__":
    pass
    

def sec_integrals_unit_test():
    for b in range(-89, 89):
        for a in range(-89,89):
            v = secint(a,b)
            ia = iisecint(v,b)
            ib = ifsecint(v,a)
            # print(math.isclose(ib,b))
            if not math.isclose(ia,a, abs_tol = 1E-12):
                print(ia,a,"error")
            if not math.isclose(ib,b, abs_tol = 1E-12):
                print(ib,b,"error")