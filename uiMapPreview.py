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
        if(Sc < S and Ec > E):
            break
    print(zoom)
    print(Nc, Sc, Ec, Wc)
    
    return [(x,y,zoom),(x,y+1,zoom),(x+1,y,zoom),(x+1,y+1,zoom)]

def fetch_tile(tile):
    img_data = requests.get("https://tile.openstreetmap.org/7/11/36.png").content
    tile = pyvips.Image.pngload_buffer(img_data)
    
    tile = tile.draw_line([255,0,0],23,25,140,100)
    return tile
    
def make_preview(N,S,E,W):
    print(N)
    print(S)
    print(E)
    print(W)
    
    tiles = get_tile_ords(N,S,E,W)
    return fetch_tile(tiles[0])
    
    
    


if __name__ == "__main__":
    make_preview(-37,-38,144,146)