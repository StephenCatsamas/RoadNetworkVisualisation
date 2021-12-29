from src import ui,maptoolslib

class Line():
    def __init__(self, to = None, fm = None, width = None, colour = None):
        self.to = (0.0, 0.0) if to == None else to
        self.fm = (0.0, 1.0) if fm == None else fm
        self.width = 0.1 if width == None else width
        self.colour = (1.0,1.0,1.0) if colour == None else colour

if __name__ == "__main__":
    print('Initiating road network visualisation')
    print(maptoolslib.__doc__)
    
    l1 = Line((-0.2,0.3), (0.4,-0.6), 0.2, (0.6,0.4,0.2))
    
    print(maptoolslib.drawlines(l1))
    # print(maptoolslib.drawlines(l1))
    # ui.begin()

