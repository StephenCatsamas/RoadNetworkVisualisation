import math
import requests
import pyvips
import itertools

def sectan(z):
    v = (1/math.cos(z)) + math.tan(z)
    # if v < 0:
        # raise ValueError
    return v

#only for a,b in (-pi/2 to pi/2)
def secint(a,b):
    a = math.radians(a)
    b = math.radians(b)
    up = sectan(b)
    down = sectan(a)
    return (math.log(up) - math.log(down))

#only for b in (-pi/2 to pi/2)
#find inverse for given initial point    
def ifsecint(v,a):
    a = math.radians(a)

    z = math.exp(v)*sectan(a)
    b = math.asin((z*z -1)/(1 + z*z))
    b = math.degrees(b)
    return b

#only for b in (-pi/2 to pi/2)
#find inverse for given end point    
def iisecint(v,b):
    b = math.radians(b)

    z = math.exp(-v)*sectan(b)
    a = math.asin((z*z - 1)/(1 + z*z))
    a = math.degrees(a)
    return a  

def row_major(tile):
    zoom,x,y = tile
    return x,y
    
def col_major(tile):
    zoom,x,y = tile
    return y,x

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

class TileCache():
    def __init__(self):
        self.tiles = {}
        self.tile_queue = []
        self.stich_tiles = None
        self.stich = None
        self.max_cache_size = 256
    
    def add_tile(self,tile,tile_data):
        self.tile_queue.append(tile)
        self.tiles[tile] = tile_data
        if len(self.tile_queue) >= self.max_cache_size:
            remove = self.tile_queue.pop(0)
            self.tiles.pop(remove)
            
    def not_cached_tiles(self, tiles):
        return [tile for tile in tiles if tile not in self.tiles]
        
def make_preview(size,bounds):
       
    z,x,y = tiles[0]
    iN,iW = num2deg(x,y,z)
    iS,iE = num2deg(x+xTiles,y+yTiles,z)
    
    stich,selection_bounds = draw_bounding_box(tileCache.stich, bounds, (iN,iS,iE,iW))
    return stich,selection_bounds
    




class SlippyMap():
    def __init__(self):
        self.tileCache = TileCache()
        # self.zoom
        # self.screen_size
        # self.screen_bounds
        # self.selection_bounds
        # self.map
        # self.map_bounds
        # self.tiles = []
        
        self.tilesize = 256
    
    #finds lat and lon from screen space pixel
    def pix2deg(self, pix, ref = None):
        x,y = pix
        
        zl = 2**(-(self.zoom+8))*360
        if ref == None:
            slat = self.screen_bounds[0]
            slon = self.screen_bounds[3]
        else:
            slat,slon = ref
            
        lon = slon + x*zl
        lat = ifsecint(math.radians(-y*zl),slat)
        
        return (lat,lon)
    
    #find screen space pixel from lat and lon
    def deg2pix(self, deg, ref = None):
        lat,lon = deg
        
        zl = 2**((self.zoom+8))/360
        if ref == None:
            slat = self.screen_bounds[0]
            slon = self.screen_bounds[3]
        else:
            slat,slon = ref
            
        y = math.degrees(secint(lat, slat)) * zl
        x = (lon-slon) *zl
        return(x,y)
    
    def make_preview(self, size, bounds):
        self.screen_size = size
        self.selection_bounds = bounds
    
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
        needed_tiles = self.tileCache.not_cached_tiles(tiles)
        for tile in needed_tiles:
            self.tileCache.add_tile(tile,self.fetch_tile(tile))
        if self.tileCache.stich_tiles != tiles:
            tiles.sort(key = col_major)
            images_tiles = [self.tileCache.tiles[tile] for tile in tiles]

            self.tileCache.stich = pyvips.Image.arrayjoin(images_tiles, across = xTiles)
            self.tileCache.stich_tiles = tiles
            
        self.map = self.tileCache.stich
        
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
        
        
        xofst,yofst = self.deg2pix((mS,mW))
        xofst = round(xofst)
        yofst = 0
        
        pN,pW = self.deg2pix((slN,slW))
        pS,pE = self.deg2pix((slS,slE))
        

        self.map = self.map.crop(-xofst, -yofst, width, height)
    
    #find zoom level for selection automatically
    def autozoom(self):
        xSize,ySize = self.screen_size
        N,S,E,W = self.selection_bounds
        ##determine zoom
        zx = math.log2(xSize / (E - W))
        zy = math.log2(ySize / (math.sin(math.radians(N)) - math.sin(math.radians(S))))
        
        zoom = min(zx,zy)
        zoom = math.floor(zoom-0.2)
        
        self.zoom = zoom
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


    def fetch_tile(self, tile):
        # if tile[2] == 'OOB':
            # url_string = "https://tile.openstreetmap.org/3/2/7.png"
        # else:
            # url_string = "https://tile.openstreetmap.org/%d/%d/%d.png" % tile 
        # print(url_string)
        # img_data = requests.get(url_string).content
        # tile_data = pyvips.Image.pngload_buffer(img_data)
        
        ###debug
        tile_data = pyvips.Image.new_from_file('test.png')
        text = pyvips.Image.text("z:%d\nx:%d\ny:%d" % tile, width = 256, height = 256, dpi = 100)[0]
        tile_data = tile_data.composite2(text, 'over')
        tile_data = tile_data.draw_rect([127], 0,0,256,256)
        # tile_data.write_to_file('a.png')
        ###
        return tile_data



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