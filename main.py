import wx
import wx.xrc
import csv
import os
import subprocess
import map
import uiMapPreview
import threading
import math
import pyvips

# https://tile.openstreetmap.org/7/11/36.png



class SpinCtrlDoubleAdpt(wx.SpinCtrlDouble):
    
    def __init__(self, *args, **kwargs):
        wx.SpinCtrl.__init__(self, *args, **kwargs)
        self.increment = self.GetIncrement()
        self.previous = self.GetValue()
        self.Bind(wx.EVT_MOUSEWHEEL, self.spinbox_scroll)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.checkIncrement)

    def spinbox_increment(self, dir):
        val = self.GetValue()
        val += dir*self.GetIncrement()
        self.SetValue(val)
        wx.PostEvent(self.GetEventHandler(), wx.PyCommandEvent(wx.EVT_SPINCTRLDOUBLE.typeId, self.GetId()))
    
    def spinbox_scroll(self,event):
        if(event.GetWheelRotation() > 0):
            self.spinbox_increment(1)
        if(event.GetWheelRotation() < 0):
            self.spinbox_increment(-1)


    def checkIncrement(self, event):
        print('aa')
        val = self.GetValue()
        inc_p = get10pow(self.increment)
        val_p = get10pow(val)
        pre_p = get10pow(self.previous)
        
        if(pre_p != inc_p and val_p != inc_p):
            self.increment(10**inc_p)
            self.SetIncrement(self.increment)
        self.previous = val
        event.Skip()
        
        
    def get10pow(self, a):
        p = round(math.log10(a)+1)
        while(math.modf(a*(10**(-p)))[0] != 0):
            p -= 1;
        return p

class MainForm ( wx.Frame ):

    def __init__( self, parent ):    
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Road Network Visualisation", pos = wx.DefaultPosition, size = wx.Size( 800,450 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, "figs/icon.ico")
        self.SetIcon(wx.Icon(fp))
        self.SetSizeHints( wx.Size( 800,450 ), wx.DefaultSize )
        self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
        
        bSizermain = wx.BoxSizer( wx.HORIZONTAL )         
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer2.SetMinSize( wx.Size( 400,-1 ) )
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

        self.draw_width = SpinCtrlDoubleAdpt( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0.000000, 0.01 )
        self.draw_width.SetDigits( 2 )
        paramSizer.Add( self.draw_width, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


        bSizer2.Add( paramSizer, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer2.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        optionSizer = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )

        self.flush_cache_widg = wx.CheckBox( self, wx.ID_ANY, u"Flush Cache", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.flush_cache_widg.SetToolTip( u"Flushes stores cache data and fetches new map data" )

        optionSizer.Add( self.flush_cache_widg, 1, wx.ALL, 5 )

        self.do_cull_widg = wx.CheckBox( self, wx.ID_ANY, u"Do Cull", wx.DefaultPosition, wx.DefaultSize, 0 )
        optionSizer.Add( self.do_cull_widg, 1, wx.ALL, 5 )

        self.force_set_widg = wx.CheckBox( self, wx.ID_ANY, u"Force Segmentation", wx.DefaultPosition, wx.DefaultSize, 0 )
        optionSizer.Add( self.force_set_widg, 1, wx.ALL, 5 )


        bSizer2.Add( optionSizer, 0, 0, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer2.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

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


        bSizer2.Add( self.infoSizer, 0, wx.EXPAND, 5 )

        self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer2.Add( self.m_staticline11, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )

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


        bSizer2.Add( confSizer, 0, wx.EXPAND, 5 )
        bSizermain.Add( bSizer2, 0, wx.EXPAND, 5 )

        self.map_view = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 400,400 ), wx.TAB_TRAVERSAL)
        self.map_view.SetMinSize( wx.Size( 400,400 ) )
        self.map_view.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        bSizermain.Add( self.map_view, 1, wx.EXPAND | wx.ALL, 5 )


        # self.SetSizer( bSizer2 )
        self.SetSizer( bSizermain )
        self.Layout()

        self.Centre( wx.BOTH )



        # Connect Events
        self.north.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.north) )
        self.south.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.south) )
        self.west.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.west) )
        self.east.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.east) )
        self.tile_res.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.tile_res) )
        self.image_res.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.image_res) )
        self.draw_width.Bind( wx.EVT_SPINCTRLDOUBLE, lambda a : self.update_args(self.draw_width) )
        self.flush_cache_widg.Bind( wx.EVT_CHECKBOX, lambda a : self.update_args(self.flush_cache_widg) )
        self.do_cull_widg.Bind( wx.EVT_CHECKBOX, lambda a : self.update_args(self.do_cull_widg) )
        self.force_set_widg.Bind( wx.EVT_CHECKBOX, lambda a : self.update_args(self.force_set_widg) )
        self.ok_button.Bind( wx.EVT_BUTTON, lambda a : self.make_map() )
        self.cancel_button.Bind( wx.EVT_BUTTON, lambda a : exit() )
        self.restore_button.Bind( wx.EVT_BUTTON, lambda a : self.restore_options() )
        
        self.map_view.Bind( wx.EVT_PAINT, self.paint_map )
        self.map_view.Bind( wx.EVT_SIZE , self.map_resize)

        
        #list of widgets
        self.widgets = {self.north,self.south,self.west,self.east,self.tile_res,self.image_res,self.draw_width,self.flush_cache_widg,self.do_cull_widg,self.force_set_widg}
        
        #widget confic name dictionary
        self.widgets_dict = {
        'colour_mode': id(0),
        'Nf': id(self.north),
        'Sf': id(self.south),
        'Ef': id(self.east),
        'Wf': id(self.west),
        'tile_size': id(self.tile_res),
        'res': id(self.image_res),
        'sef_width': id(self.draw_width),
        'flush_map_cache': id(self.flush_cache_widg),
        'do_cull': id(self.do_cull_widg),
        'force_seg': id(self.force_set_widg),
        'seg_width': id(1),
        'threads': id(2),
        'mapPullOutPath' : id(3),
        'mapStreetInPath': id(4),
        'mapStreetOutPath': id(5),
        'mapSegInPath': id(6),
        'mapSegOutPath': id(7),
        'mapDrawInPath': id(8),
        'mapDrawOutPath': id(9),
        'mapGreyInPath': id(10),
        'mapGreyOutPath': id(11),
        'mapGrayMaskPath': id(12),
        'mapConcatInPath': id(13),
        'mapConcatOutPath': id(14)}

        #load current values
        self.load_options()
    
    def spinbox_increment(self, spinbox, dir):
        val = spinbox.GetValue()
        val += dir*spinbox.GetIncrement()
        spinbox.SetValue(val)
        self.update_args()
    
    def spinbox_scroll(self,event, spinbox):
        if(event.GetWheelRotation() > 0):
            self.spinbox_increment(spinbox, 1)
        if(event.GetWheelRotation() < 0):
            self.spinbox_increment(spinbox, -1)  

    def __del__( self ):
        pass
    
    def read_options_file(self, fp):
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, fp)
        with open(fp, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            self.arg_lines = {}
            self.args_dict = {}
            for i,row in enumerate(reader):
                if row == []:
                    continue
                if row[0][0] == '#':
                    continue
                self.arg_lines[i] = row[0].strip()
                try:
                    self.args_dict[self.widgets_dict[row[0].strip()]] = row[1].strip()
                except KeyError:
                    pass
                
        self.update_widgets()       
        
    def load_options(self):
        self.read_options_file('args_def.txt')

    def restore_options(self):
        self.read_options_file('args_lst.txt')
    
    def make_map(self):
        self.save_options()
        work_thread = threading.Thread(target=map.run, args=[])
        work_thread.start()        
    
    def save_options(self):
        csv_rows = []
        write_lines = {}
        
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, 'args_lst.txt')
        with open(fp, 'r', newline='') as csvfile:
            row = csv.reader(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_rows.extend(row)

        inv_widget_dict = {v: k for k, v in self.widgets_dict.items()}
        for key,value in self.arg_lines.items():
            print("value: " + value)
            print("key: " + str(key))
            print()
            print(self.args_dict)
            print()
            print(self.widgets_dict)
            print()
            print(inv_widget_dict)
            print()
            write_lines[key] = [value, self.args_dict[self.widgets_dict[value]]]
        
        dirname = os.path.dirname(__file__)
        fp = os.path.join(dirname, 'args_lst.txt')
        with open('args_lst.txt', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for line, row in enumerate(csv_rows):
                 data = write_lines.get(line, row)

                 writer.writerow(data)
    
    def update_args(self,widget = None):
        if widget == None:
            for widget in self.widgets:
                try:
                    self.args_dict[id(widget)] = widget.GetValue()
                except KeyError:
                    pass
        else:
            try:
                self.args_dict[id(widget)] = widget.GetValue()
            except KeyError:
                pass
        self.update_widgets('info')
        event.Skip()
     
    def map_resize(self,event):
        self.map_view.Refresh()
        
    def paint_map(self, event):
        bitmap = self.preview_map()
        dc = wx.PaintDC(self.map_view)
        dc.DrawBitmap(bitmap, 0,0)

    def preview_map(self):    
        size = self.map_view.GetSize()
        bounds = (float(self.args_dict[id(self.north)]), 
            float(self.args_dict[id(self.south)]), 
            float(self.args_dict[id(self.east)]), 
            float(self.args_dict[id(self.west)]))
        map_img,selection_bounds = uiMapPreview.make_preview(size, bounds)
        
        map_img.write_to_file("fullmap.png")
        
        xSize,ySize = size
        selection_bounds = [round(x) for x in selection_bounds]
        Npos,Spos,Epos,Wpos = selection_bounds
        xCrop = 0.5*(Epos+Wpos - xSize)
        yCrop = 0.5*(Spos+Npos - ySize)
        
        print("aaaaaaa")
        print(selection_bounds)
        print(xCrop, yCrop, xSize, ySize)
        
        map_img = map_img.crop(xCrop, yCrop, xSize, ySize)
        
        dat = map_img.write_to_memory()
        bitmap = wx.Bitmap.FromBufferRGBA(map_img.width,map_img.height,dat)
        return bitmap
        # self.map_view.SetBitmap(bitmap)

    def update_widgets(self,widget = None):

        self.map_view.Refresh()
        
        if widget == None:
            for widget in self.widgets:
                try:
                    try:
                        widget.SetValue(float(self.args_dict[id(widget)]))
                    except ValueError:
                        widget.SetValue(bool(self.args_dict[id(widget)]))
                except KeyError:
                    pass
        elif widget == 'info':
            try:
                delta_lat_str = str(round(float(self.args_dict[id(self.north)])-float(self.args_dict[id(self.south)]),3))
                self.lat_delta_label.SetLabel("Latitude Delta: " + delta_lat_str + " deg")
            except TypeError:
                pass
            try:
                delta_lon_str = str(round(float(self.args_dict[id(self.east)])-float(self.args_dict[id(self.west)]),3))
                self.lon_delta_label.SetLabel("Longitude Delta: " + delta_lon_str + " deg")
            except TypeError:
                pass
            try:
                n_tiles_str = str(int(math.ceil((float(self.args_dict[id(self.north)])-float(self.args_dict[id(self.south)]))/float(self.args_dict[id(self.tile_res)])) * math.ceil((float(self.args_dict[id(self.east)])-float(self.args_dict[id(self.west)]))/float(self.args_dict[id(self.tile_res)]))))
                self.n_tiles_label.SetLabel("Tiles: " + n_tiles_str)
            except (ZeroDivisionError,TypeError):
                pass
            self.infoSizer.Layout()
            
        else:
            try:
                self.widget.SetLabel(self.args_dict[id(widget)])
            except KeyError:
                pass

if __name__ == "__main__":
    app = wx.App()
    frame =  MainForm(None)
    frame.Show()
    app.MainLoop()


