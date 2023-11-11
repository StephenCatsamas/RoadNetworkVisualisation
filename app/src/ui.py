import wx
import wx.xrc
import wx.stc
import wx.lib.agw.hyperlink
import csv
import os
import subprocess
from . import map
from . import uiMapPreview
import threading
import math
import pyvips
from .args import ArgsContainer


class SpinCtrlDoubleAdpt(wx.SpinCtrlDouble):
    
    def __init__(self, *args, **kwargs):
        wx.SpinCtrl.__init__(self, *args, **kwargs)
        # self.increment = self.GetIncrement()
        # self.previous = self.GetValue()
        self.Bind(wx.EVT_CHAR_HOOK, self.enter)
        

    def enter(self,event):
        if event.GetKeyCode() in (wx.stc.STC_KEY_RETURN,370):#370 for numpad enter
            self.GetParent().SetFocus()
            self.SetFocus()
        else:
            event.Skip()
        

    def spinbox_increment(self, dir):
        self.checkIncrement()
    
        val = self.GetValue()
        val += dir*self.GetIncrement()
        self.SetValue(val)
        
    
    def spinbox_scroll(self,event):
        if(event.GetWheelRotation() > 0):
            self.spinbox_increment(1)
        if(event.GetWheelRotation() < 0):
            self.spinbox_increment(-1)
        event.Skip()


    def checkIncrement(self):
        val = self.GetValue()
        inc_p = self.get10pow(self.increment)
        val_p = self.get10pow(val)
        pre_p = self.get10pow(self.previous)
        if(pre_p != inc_p and val_p != inc_p):
            self.increment = 10**inc_p
            self.SetIncrement(self.increment)
        self.previous = val
        
        
    def get10pow(self, a):
        a = abs(a)
        if a != 0:
            p = round(math.log10(a)+1)
        else:
            p = self.increment
        while(math.modf(a*(10**(-p)))[0] != 0):
            p -= 1;
        return p

class MapSelectionDraggable(wx.Panel):
    def __init__(self, bitmap, corner, *args, **kwargs):
        wx.Panel.__init__(self)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Create(*args, **kwargs)
        
        self.bitmap = bitmap
        self.corner = corner
        
        self.Bind( wx.EVT_LEFT_DOWN, self.dragstart)
        self.Bind( wx.EVT_LEFT_UP, self.dragend)
        self.Bind( wx.EVT_MOTION, self.drag)    
        self.Bind( wx.EVT_PAINT, self.paint)        
        self.cursor = (0,0)
    
    def paint(self, event):
        dc = wx.BufferedPaintDC(self)   
        dc.DrawBitmap(self.bitmap, 0,0)
    
    def dragstart(self, event):
        self.cursor = event.GetPosition()
        wx.Window.CaptureMouse(self)
    def dragend(self, event):
        wx.Window.ReleaseMouse(self)
    
    def checkpos(self,newpos):
        if self.corner == 'NW':
            posNW = newpos
            posSE = self.GetParent().dragSE.GetPosition()
        if self.corner == 'SE':
            posSE = newpos
            posNW = self.GetParent().dragNW.GetPosition()    
        
        xW,yN = posNW
        xE,yS = posSE
        if(xE <= xW):
            return False
        if(yS <= yN):
            return False
        return True
        
     
    def drag(self, event):
        if event.Dragging():
            oldpos = self.GetPosition()
            pos = event.GetPosition()
            
            newpos = pos+oldpos-self.cursor
            
            if(self.checkpos(newpos)):
            
                self.SetPosition(newpos)
                self.GetParent().slippy.setselectionpix(newpos, self.corner)
                self.GetParent().GetParent().mapupdate()
                self.GetParent().slippy.rezoom = False
                self.GetParent().Refresh()
            
            
    
class MapPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.mousepos = (0,0)
        
        self.slippy = uiMapPreview.SlippyMap(self)
        self.Bind( wx.EVT_PAINT, self.paint_map)
        self.Bind( wx.EVT_SIZE , self.map_resize)
        self.Bind( wx.EVT_MOUSEWHEEL, self.zoom)
        self.Bind( wx.EVT_LEFT_DOWN, self.dragstart)
        self.Bind( wx.EVT_MOTION, self.drag)

        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, '../ico/button.png')
        self.buttonbmp = wx.Bitmap(fp, wx.BITMAP_TYPE_PNG)

        self.dragNW = MapSelectionDraggable(self.buttonbmp, 'NW', self, wx.ID_ANY, size = self.buttonbmp.GetSize())
        self.dragSE = MapSelectionDraggable(self.buttonbmp, 'SE', self, wx.ID_ANY, size = self.buttonbmp.GetSize())
                
    def dragstart(self, event):
        self.mousepos = event.GetPosition()
        
    def drag(self, event):
        if event.Dragging():
            newpos = event.GetPosition()
            move = newpos - self.mousepos
            self.mousepos = newpos
            
            self.slippy.drag(move)
            self.slippy.rezoom = False
            self.Refresh()
    
    def zoom(self,event):
        pos = event.GetPosition()
        if(event.GetWheelRotation() > 0):
            self.slippy.zoomupdate(1, pos)
        if(event.GetWheelRotation() < 0):
            self.slippy.zoomupdate(-1,pos)
        self.slippy.rezoom = False
        self.Refresh()
      
    def map_resize(self,event):
        self.slippy.rezoom = True
        self.Refresh()
        
    def paint_map(self, event):
        bitmap = self.preview_map()
        dc = wx.PaintDC(self)
        dc.DrawBitmap(bitmap, 0,0)
        
        Np,Sp,Ep,Wp = self.slippy.getselectionpix()
        
        NWp = (round(Wp-4),round(Np-4))
        SEp = (round(Ep-4),round(Sp-4))
        self.dragNW.SetPosition(NWp)
        self.dragSE.SetPosition(SEp)
        

    def preview_map(self):    
        size = self.GetSize()
        parent = self.GetParent()
        
        map_img = self.slippy.make_preview(size)
        dat = map_img.write_to_memory()

        bitmap = wx.Bitmap.FromBufferRGBA(map_img.width,map_img.height,dat)
        return bitmap

    

class MainForm ( wx.Frame ):

    def __init__( self, parent ):    
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Road Network Visualisation", pos = wx.DefaultPosition, size = wx.Size( 800,450 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, "../ico/icon.ico")
        self.SetIcon(wx.Icon(fp))
        self.SetSizeHints( wx.Size( 800,450 ), wx.DefaultSize )
        self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
        
        b_sizer_main = wx.BoxSizer( wx.HORIZONTAL )         
        
        b_sizer_control = wx.BoxSizer( wx.VERTICAL )
        b_sizer_map     = wx.BoxSizer( wx.VERTICAL )

        
        b_sizer_control.SetMinSize( wx.Size( 400,-1 ) )
        paramSizer = wx.GridSizer( 0, 2, 0, 0 )

        self.north_label = wx.StaticText( self, wx.ID_ANY, u"North Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.north_label.Wrap( -1 )

        paramSizer.Add( self.north_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.north = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -90, 90, 0, 0.001 )
        self.north.SetDigits( 3 )
        paramSizer.Add( self.north, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

        self.south_label = wx.StaticText( self, wx.ID_ANY, u"South Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.south_label.Wrap( -1 )

        paramSizer.Add( self.south_label, 0, wx.ALL, 5 )

        self.south = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -90, 90, 0, 0.001 )
        self.south.SetDigits( 3 )
        paramSizer.Add( self.south, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.west_label = wx.StaticText( self, wx.ID_ANY, u"West Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.west_label.Wrap( -1 )

        paramSizer.Add( self.west_label, 0, wx.ALL, 5 )

        self.west = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -180, 180, 0, 0.001 )
        self.west.SetDigits( 3 )
        paramSizer.Add( self.west, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.east_label = wx.StaticText( self, wx.ID_ANY, u"East Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.east_label.Wrap( -1 )

        paramSizer.Add( self.east_label, 0, wx.ALL, 5 )

        self.east = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -180, 180, 0, 0.001 )
        self.east.SetDigits( 3 )
        paramSizer.Add( self.east, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.tile_res_label = wx.StaticText( self, wx.ID_ANY, u"Tile Width (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tile_res_label.Wrap( -1 )

        paramSizer.Add( self.tile_res_label, 0, wx.ALL, 5 )

        self.tile_res = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 20, 0, 0.001 )
        self.tile_res.SetDigits( 3 )
        paramSizer.Add( self.tile_res, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.image_res_label = wx.StaticText( self, wx.ID_ANY, u"Resolution:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.image_res_label.Wrap( -1 )

        paramSizer.Add( self.image_res_label, 0, wx.ALL, 5 )

        self.image_res = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 1e+06, 0, 10 )
        self.image_res.SetDigits( 0 )
        paramSizer.Add( self.image_res, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.draw_width_label = wx.StaticText( self, wx.ID_ANY, u"Line Width:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.draw_width_label.Wrap( -1 )

        paramSizer.Add( self.draw_width_label, 0, wx.ALL, 5 )

        self.draw_width = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0.000000, 0.001 )
        self.draw_width.SetDigits( 3 )
        paramSizer.Add( self.draw_width, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


        b_sizer_control.Add( paramSizer, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        b_sizer_control.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        optionSizer = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )

        self.flush_cache_widg = wx.CheckBox( self, wx.ID_ANY, u"Flush Cache", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.flush_cache_widg.SetToolTip( u"Flushes stores cache data and fetches new map data" )

        optionSizer.Add( self.flush_cache_widg, 1, wx.ALL, 5 )

        self.do_cull_widg = wx.CheckBox( self, wx.ID_ANY, u"Do Cull", wx.DefaultPosition, wx.DefaultSize, 0 )
        optionSizer.Add( self.do_cull_widg, 1, wx.ALL, 5 )

        self.force_set_widg = wx.CheckBox( self, wx.ID_ANY, u"Force Segmentation", wx.DefaultPosition, wx.DefaultSize, 0 )
        optionSizer.Add( self.force_set_widg, 1, wx.ALL, 5 )


        b_sizer_control.Add( optionSizer, 0, 0, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        b_sizer_control.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )


        b_sizer_control.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.infoSizer = wx.WrapSizer( wx.HORIZONTAL, 0 )

        self.lat_delta_label = wx.StaticText( self, wx.ID_ANY, u"Latitude Δ:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lat_delta_label.SetLabelMarkup( u"Latitude Δ:" )
        self.lat_delta_label.Wrap( -1 )

        self.infoSizer.Add( self.lat_delta_label, 1, wx.ALL|wx.ALIGN_BOTTOM, 5 )

        self.lon_delta_label = wx.StaticText( self, wx.ID_ANY, u"Longitude Δ:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lon_delta_label.Wrap( -1 )

        self.infoSizer.Add( self.lon_delta_label, 1, wx.ALL|wx.ALIGN_BOTTOM, 5 )

        self.n_tiles_label = wx.StaticText( self, wx.ID_ANY, u"Tiles:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.n_tiles_label.Wrap( -1 )

        self.infoSizer.Add( self.n_tiles_label, 1, wx.ALIGN_BOTTOM|wx.ALL, 5 )


        b_sizer_control.Add( self.infoSizer, 0, wx.EXPAND, 5 )

        self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        b_sizer_control.Add( self.m_staticline11, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )

        confSizer = wx.FlexGridSizer( 0, 3, 0, 0 )
        confSizer.AddGrowableCol( 0 )
        confSizer.SetFlexibleDirection( wx.BOTH )
        confSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.restore_button = wx.Button( self, wx.ID_ANY, u"Restore Defaults", wx.DefaultPosition, wx.DefaultSize, 0 )
        confSizer.Add( self.restore_button, 0, wx.ALL, 5 )

        self.ok_button = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
        confSizer.Add( self.ok_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.cancel_button = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        confSizer.Add( self.cancel_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


        b_sizer_control.Add( confSizer, 0, wx.EXPAND, 5 )
        b_sizer_main.Add( b_sizer_control, 0, wx.EXPAND, 5 )

        self.map_view = MapPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 400,400 ), wx.TAB_TRAVERSAL)
        self.map_view.SetMinSize( wx.Size( 400,400 ) )
        self.map_view.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        self.map_link = wx.lib.agw.hyperlink.HyperLinkCtrl(self, 
                                                           wx.ID_ANY, 
                                                           u"OpenStreetMap", 
                                                           wx.DefaultPosition, 
                                                           wx.DefaultSize, 
                                                           0,
                                                           URL="openstreetmap.org/copyright" )


        b_sizer_map.Add( self.map_view, 1, wx.ALL, 5 )
        b_sizer_map.Add( self.map_link, 0, wx.ALL | wx.ALIGN_RIGHT, 5 )

        b_sizer_main.Add( b_sizer_map, 1, wx.EXPAND | wx.ALL, 5 )
                
       
        self.SetSizer( b_sizer_main )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.north.Bind( wx.EVT_SPINCTRLDOUBLE, self.controlupdate)
        self.south.Bind( wx.EVT_SPINCTRLDOUBLE, self.controlupdate)
        self.east.Bind( wx.EVT_SPINCTRLDOUBLE,  self.controlupdate)
        self.west.Bind( wx.EVT_SPINCTRLDOUBLE,  self.controlupdate)
        self.tile_res.Bind( wx.EVT_SPINCTRLDOUBLE, self.controlupdate)
        self.image_res.Bind( wx.EVT_SPINCTRLDOUBLE, self.controlupdate)
        self.draw_width.Bind( wx.EVT_SPINCTRLDOUBLE, self.controlupdate)
        self.flush_cache_widg.Bind( wx.EVT_CHECKBOX, self.controlupdate)
        self.do_cull_widg.Bind( wx.EVT_CHECKBOX, self.controlupdate)
        self.force_set_widg.Bind( wx.EVT_CHECKBOX, self.controlupdate)
        self.ok_button.Bind( wx.EVT_BUTTON, lambda a : self.make_map() )
        self.cancel_button.Bind( wx.EVT_BUTTON, lambda a : exit() )
        self.restore_button.Bind( wx.EVT_BUTTON, lambda a : self.restore_options() )
        
        #load defaults
        self.initargs()
        self.updatewidgets()
        

    def __del__( self ):
        pass
    
    def make_map(self):
        self.args.save_args()
        work_thread = threading.Thread(target=map.run, args=[self.args])
        work_thread.start()    

    def updatewidgets(self):
        self.north.SetValue(self.args.Nf)
        self.south.SetValue(self.args.Sf)
        self.east.SetValue(self.args.Ef)
        self.west.SetValue(self.args.Wf)
        self.tile_res.SetValue(self.args.tile_size)
        self.image_res.SetValue(self.args.res)
        self.draw_width.SetValue(self.args.seg_width)
        self.flush_cache_widg.SetValue(self.args.flush_map_cache)
        self.do_cull_widg.SetValue(self.args.do_cull)
        self.force_set_widg.SetValue(self.args.force_seg)
        
        
        delta_lat_str = str(round(self.args.Nf - self.args.Sf,3))
        self.lat_delta_label.SetLabelMarkup( u"Latitude Δ: " + delta_lat_str + " deg")
        
        delta_lon_str = str(round(self.args.Ef - self.args.Wf,3))
        self.lon_delta_label.SetLabelMarkup("Longitude Δ: " + delta_lon_str + " deg")
        
        n_tiles_str = str(int(math.ceil((self.args.Nf-self.args.Sf)/self.args.tile_size * math.ceil(self.args.Ef-self.args.Wf)/self.args.tile_size)))
        self.n_tiles_label.SetLabel("Tiles: " + n_tiles_str)
        
        self.map_view.slippy.selection_bounds = (self.args.Nf,self.args.Sf,self.args.Ef,self.args.Wf)
        
        self.map_view.Refresh()

    def mapupdate(self):
        self.args.Nf,self.args.Sf,self.args.Ef,self.args.Wf = self.map_view.slippy.selection_bounds
        
        self.updatewidgets()
        

    def controlupdate(self,event):
        self.args.Nf = self.north.GetValue()
        self.args.Sf = self.south.GetValue()
        self.args.Ef = self.east.GetValue()
        self.args.Wf = self.west.GetValue()
        self.args.tile_size = self.tile_res.GetValue()
        self.args.res = self.image_res.GetValue()
        self.args.seg_width = self.draw_width.GetValue()
        self.args.flush_map_cache = self.flush_cache_widg.GetValue()
        self.args.do_cull = self.do_cull_widg.GetValue()
        self.args.force_seg = self.force_set_widg.GetValue()
        
        self.map_view.slippy.rezoom = True
        self.updatewidgets()
        
        
    def initargs(self):
        self.args = ArgsContainer()  
        
    def restore_options(self):
        print('implement restoring options')

def begin():
    app = wx.App()
    frame =  MainForm(None)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    begin()


