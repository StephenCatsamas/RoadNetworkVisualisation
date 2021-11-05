import math
import requests
import pyvips

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

def get_tile_ords(N,S,E,W):
    ##we want to find 4 tiles which cover out range
    
    for zoom in reversed(range(12)):
        x,y = deg2num(N,W,zoom)
        Nc, Wc = num2deg(x,y,zoom)
        if(Nc < N or Wc > W):
            continue
        Sc, Ec = num2deg(x+1+1,y+1+1,zoom)
        print("==")
        print(Sc)
        print(Ec)
        if(Sc < S and Ec > E):
            break
    print(zoom)
    print(Nc, Sc, Ec, Wc)
    
    return ((zoom,x,y),(zoom,x+1,y),(zoom,x,y+1),(zoom,x+1,y+1))

def fetch_tile(tile):
    url_string = "https://tile.openstreetmap.org/%d/%d/%d.png" % tile 
    print(url_string)
    img_data = requests.get(url_string).content
    tile = pyvips.Image.pngload_buffer(img_data)
      
    return tile

def sec_integral(a,b):
    a = math.radians(a)
    b = math.radians(b)
    up = (1/math.cos(b)) + math.tan(b)
    down = (1/math.cos(a)) + math.tan(a)
    return (math.log(abs(up)) - math.log(abs(down)))

def draw_bounding_box(tile, bounds, image_bounds):
    N,S,E,W = bounds
    iN,iS,iE,iW = image_bounds
    print(iS)
    print(iN)
    print(sec_integral(iS,iN))
    zl = tile.height / sec_integral(iN,iS)
    Npix = sec_integral(iN, N) * zl
    Spix = sec_integral(iN, S) * zl
    Epix = tile.width*((E - iW)/(iE - iW)) 
    Wpix = tile.width*((W - iW)/(iE - iW)) 
    
    tile = tile.draw_line([255,0,0], Wpix,Npix,Wpix,Spix)
    tile = tile.draw_line([255,0,0], Wpix,Spix,Epix,Spix)
    tile = tile.draw_line([255,0,0], Epix,Spix,Epix,Npix)
    tile = tile.draw_line([255,0,0], Epix,Npix,Wpix,Npix)
    
    center = tile.extract_area(Wpix, Npix, (Epix - Wpix), (Spix - Npix))
    grey = pyvips.Image.black(tile.width, tile.height)
    # grey = grey.draw_rect([255,255,255], 0,0, grey.width,grey.height)
    tile = tile.composite2(grey, 'over')
    # tile = tile.composite2(center, 'over')
    return tile

    
    
def make_preview(N,S,E,W):
    print(N)
    print(S)
    print(E)
    print(W)
    
    tiles = get_tile_ords(N,S,E,W)
    images_tiles = [fetch_tile(tile) for tile in tiles]
    stich = pyvips.Image.arrayjoin(images_tiles, across = 2)
    stich.write_to_file("stich.png")
    
    z,x,y = tiles[0]
    iN,iW = num2deg(x,y,z)
    iS,iE = num2deg(x+2,y+2,z)
    
    stich = draw_bounding_box(stich, (N,S,E,W), (iN,iS,iE,iW))
    
    return stich
    
    


if __name__ == "__main__":
    print(sec_integral(-30,0))
    # make_preview(-37,-38,144,146)