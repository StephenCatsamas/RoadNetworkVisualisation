import math
import requests
import pyvips

def sec_integral(a,b):
    a = math.radians(a)
    b = math.radians(b)
    up = (1/math.cos(b)) + math.tan(b)
    down = (1/math.cos(a)) + math.tan(a)
    return (math.log(abs(up)) - math.log(abs(down)))

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


def get_tile_ords(size,bounds):
    xSize,ySize = size
    N,S,E,W = bounds
    
    xTiles = xSize//256 +1
    yTiles = ySize//256 +1
    ##we want to find 4 tiles which cover out range

    zx = math.log2(xSize / (E - W))
    zy = math.log2(ySize / (math.sin(math.radians(N)) - math.sin(math.radians(S)) )    )
    
    zoom = min(zx,zy)
    zoom = math.floor(zoom)
    
    print(zx,zy)

    x,y = deg2num(N,W,zoom)
    
    Nc, Wc = num2deg(x,y,zoom)
    Sc, Ec = num2deg(x+xTiles,y+yTiles,zoom)
            
    tiles = []
    for j in range(y-1,y+yTiles+1):
        for i in range(x-1,x+xTiles+1):
            if (j < 2**zoom):
                tiles.append((zoom, i%(2**zoom),j))
            else: 
                tiles.append((zoom,i%(2**zoom),'OOB'))
            
    grid = (xTiles+2, yTiles+2)

    return tiles,grid

def fetch_tile(tile):
    if tile[2] == 'OOB':
        url_string = "https://tile.openstreetmap.org/3/2/7.png"
    else:
        url_string = "https://tile.openstreetmap.org/%d/%d/%d.png" % tile 
    print(url_string)
    img_data = requests.get(url_string).content
    tile_data = pyvips.Image.pngload_buffer(img_data)
    
    ###debug
    tile_data = tile_data.draw_rect([0,0,0], 0,0,256,256)
    ###
    return tile_data

def draw_bounding_box(tile, bounds, image_bounds):
    N,S,E,W = bounds
    iN,iS,iE,iW = image_bounds

    zl = tile.height / sec_integral(iN,iS)
    Npix = sec_integral(iN, N) * zl
    Spix = sec_integral(iN, S) * zl
    Epix = tile.width*((E - iW)/(iE - iW)) 
    Wpix = tile.width*((W - iW)/(iE - iW)) 

    
    svg = '<svg width="%d" height="%d">' % (tile.width, tile.height)
    svg += '<path d="M0,0  h%d v%d h-%d z ' % (tile.width, tile.height, tile.width)
    svg +='M%d,%d v%d h%d v-%d z" ' % (Wpix,Npix,Spix-Npix, Epix-Wpix, Spix-Npix)
    svg += 'stroke="black" fill="grey" fill-opacity="0.3"   />' 
    svg += '</svg>'
    # print(svg)
    overlay = pyvips.Image.svgload_buffer(bytes(svg, 'utf-8'))
   
    preview_tile = tile.composite2(overlay, 'over')
    preview_tile.write_to_file('cover.png')
    selection_bounds = (Npix,Spix,Epix,Wpix) #pixels of selction boundary on image
    
    return preview_tile, selection_bounds

def row_major(tile):
    zoom,x,y = tile
    return x,y
    

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
        

tileCache = TileCache()

def make_preview(size,bounds):
        
    tiles,grid = get_tile_ords(size,bounds)
    
    xTiles,yTiles = grid
    
    needed_tiles = not_cached_tiles(tiles)
    
    for tile in needed_tiles:
        tileCache.add_tile(tile,fetch_tile(tile))
    if tileCache.stich_tiles != tiles:
        images_tiles = [tileCache.tiles[tile] for tile in tiles]
        images_tiles.sort(key = row_major)
        tileCache.stich = pyvips.Image.arrayjoin(images_tiles, across = xTiles)
        tileCache.stich_tiles = tiles
    # tileCache.stich.write_to_file("stich.png")
    
    z,x,y = tiles[0]
    iN,iW = num2deg(x,y,z)
    iS,iE = num2deg(x+xTiles,y+yTiles,z)
    
    stich,selection_bounds = draw_bounding_box(tileCache.stich, bounds, (iN,iS,iE,iW))
    return stich,selection_bounds
    
    
def not_cached_tiles(tiles):
    return [tile for tile in tiles if tile not in tileCache.tiles]


if __name__ == "__main__":
    print(sec_integral(-30,0))
    # make_preview(-37,-38,144,146)