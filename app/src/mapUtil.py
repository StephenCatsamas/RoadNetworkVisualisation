import math

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

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = math.floor((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)



_LOG2TILESIZE = 8 

#finds lat and lon from screen space pixel
def pix2deg(pix, ref, zoom):
    x,y = pix
    
    zl = 2**(-(zoom+_LOG2TILESIZE))*360
    slat,slon = ref
        
    lon = slon + x*zl
    lat = ifsecint(math.radians(-y*zl),slat)
    
    return (lat,lon)

#find screen space pixel from lat and lon
def deg2pix(deg, ref, zoom):
    lat,lon = deg
    
    zl = 2**((zoom+_LOG2TILESIZE))/360
    slat,slon = ref
        
    y = math.degrees(secint(lat, slat)) * zl
    x = (lon-slon) *zl
    return(x,y)
