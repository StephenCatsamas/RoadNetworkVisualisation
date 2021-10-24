import tkinter as tk
import csv
import os
import subprocess
import map
import threading
import math

# https://tile.openstreetmap.org/7/11/36.png

class app(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Road Network Visualiser")
        self.iconbitmap('figs/icon.ico')

        self.load_options()
       
        self.make_widgets()

        self.mainloop()
        
        
        
    def load_options(self):
        with open('args_lst.txt', 'r', newline='') as csvfile:
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
                self.args_dict[row[0].strip()] = row[1].strip()
                
    def restore_options(self):
        with open('args_def.txt', 'r', newline='') as csvfile:
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
                self.args_dict[row[0].strip()] = row[1].strip()
                
        for key,value in self.args_dict.items():
            try:
                self.widget_dict[key].set(value)
            except KeyError:
                pass
    
    def make_map(self):
        self.save_options()
        work_thread = threading.Thread(target=map.run, args=[])
        work_thread.start()        
    
    def save_options(self):
        csv_rows = []
        write_lines = {}
        
        with open('args_lst.txt', 'r', newline='') as csvfile:
            row = csv.reader(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_rows.extend(row)

        for key,value in self.arg_lines.items():
            write_lines[key] = [value, self.args_dict[value]]

        with open('args_lst.txt', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='=',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for line, row in enumerate(csv_rows):
                 data = write_lines.get(line, row)

                 writer.writerow(data)
    
    def update_args(self,key = None):
        if key == None:
            for key in self.widget_dict:
                try:
                    self.args_dict[key] = self.widget_dict[key].get()
                except tk._tkinter.TclError:
                    pass
        else:
            try:
                self.args_dict[key] = self.widget_dict[key].get()
            except tk._tkinter.TclError:
                pass
                
        self.update_widgets('info')
                
    def update_widgets(self,key = None):
        if key == None:
            for key in self.args_dict:
                try:
                    self.widget_dict[key].set(self.args_dict[key])
                except KeyError:
                    pass
        elif key == 'info':
            try:
                delta_lat_str = str(round(self.args_dict['Nf']-self.args_dict['Sf'],3))
                self.widget_dict['delta_lat'].set("Latitude Delta: " + delta_lat_str + " deg")
            except TypeError:
                pass
            try:
                delta_lon_str = str(round(self.args_dict['Ef']-self.args_dict['Wf'],3))
                self.widget_dict['delta_lon'].set("Longitude Delta: " + delta_lon_str + " deg")
            except TypeError:
                pass
            try:
                n_tiles_str = str(int(math.ceil((self.args_dict['Nf']-self.args_dict['Sf'])/self.args_dict['tile_size']) * math.ceil((self.args_dict['Ef']-self.args_dict['Wf'])/self.args_dict['tile_size'])))
                self.widget_dict['n_tiles'].set("Tiles: " + n_tiles_str)
            except (ZeroDivisionError,TypeError):
                pass
        else:
            try:
                self.args_dict[key].set(self.args_dict[key])
            except KeyError:
                pass

    
    def make_widgets(self):
        self.widget_dict = {}
    
        self.param_frame = tk.Frame(self,relief='raised', borderwidth=1)
        self.param_frame.pack(side = "top", fill = 'x')
        self.param_frame.grid_columnconfigure(0, weight=1)

        self.option_frame = tk.Frame(self,relief='raised', borderwidth=1)
        self.option_frame.pack( side = "top", fill = 'x')

        self.info_frame = tk.Frame(self,relief='raised', borderwidth=1)
        self.info_frame.pack(side = "top", fill = 'x')
        self.info_frame.grid_columnconfigure(0, weight=1)

        self.conf_frame = tk.Frame(self,relief='raised', borderwidth=1)
        self.conf_frame.pack(padx=5, side = "bottom", fill = 'x')

        self.north_label = tk.Label(self.param_frame, text = "North Limit (deg):")
        self.north_label.grid(padx=5,pady=5,row=0, column=0, sticky  = "W")
        north_init = tk.DoubleVar(value = 0)
        self.north =  tk.Spinbox(self.param_frame, from_ = -90, to = 90, textvariable = north_init, width = 25, increment = 0.001)
        self.north.grid(padx=5,pady=5,row=0, column=1, sticky="NSEW")
        north_init.trace_add('write',lambda a,b,c : self.update_args('Nf'))
        self.widget_dict['Nf'] = north_init

        self.south_label = tk.Label(self.param_frame, text = "South Limit (deg):")
        self.south_label.grid(padx=5,pady=5,row=1, column=0, sticky  = "W")
        south_init = tk.DoubleVar(value = 0)
        self.south =  tk.Spinbox(self.param_frame, from_ = -90, to = 90, textvariable = south_init, width = 25, increment = 0.001)
        south_init.trace_add('write',lambda a,b,c : self.update_args('Sf'))
        self.south.grid(padx=5,pady=5,row=1, column=1)
        self.widget_dict['Sf'] = south_init
        
        self.west_label = tk.Label(self.param_frame, text = "West Limit (deg):")
        self.west_label.grid(padx=5,pady=5,row=2, column=0, sticky  = "W")
        west_init = tk.DoubleVar(value = 0)
        self.west =  tk.Spinbox(self.param_frame, from_ = -180, to = 180, textvariable = west_init, width = 25, increment = 0.001)
        west_init.trace_add('write',lambda a,b,c : self.update_args('Wf'))
        self.west.grid(padx=5,pady=5,row=2, column=1)
        self.widget_dict['Wf'] = west_init

        self.east_label = tk.Label(self.param_frame, text = "East Limit (deg):")
        self.east_label.grid(padx=5,pady=5,row=3, column=0, sticky  = "W")
        east_init = tk.DoubleVar(value = 0)
        self.east = tk.Spinbox(self.param_frame, from_ = -180, to = 180, textvariable = east_init, width = 25, increment = 0.001)
        east_init.trace_add('write',lambda a,b,c : self.update_args('Ef'))
        self.east.grid(padx=5,pady=5,row=3, column=1)
        self.widget_dict['Ef'] = east_init

        self.tile_res_label = tk.Label(self.param_frame, text = "Tile Width (deg):")
        self.tile_res_label.grid(padx=5,pady=5,row=4, column=0, sticky  = "W")
        tile_init = tk.DoubleVar(value = 0)
        self.tile_res = tk.Spinbox(self.param_frame, from_ = 0, to = 5, textvariable = tile_init, width = 25, increment = 0.001)
        tile_init.trace_add('write',lambda a,b,c : self.update_args('tile_size'))
        self.tile_res.grid(padx=5,pady=5,row=4, column=1)
        self.widget_dict['tile_size'] = tile_init

        self.image_res_label = tk.Label(self.param_frame, text = "Resolution:")
        self.image_res_label.grid(padx=5,pady=5,row=5, column=0, sticky  = "W")
        res_init = tk.DoubleVar(value = 0)
        self.image_res = tk.Spinbox(self.param_frame, from_ = 0, to = 1E6, textvariable = res_init, width = 25, increment = 10)
        res_init.trace_add('write',lambda a,b,c : self.update_args('res'))
        self.image_res.grid(padx=5,pady=5,row=5, column=1)
        self.widget_dict['res'] = res_init

        self.draw_width_label = tk.Label(self.param_frame, text = "Line Width:")
        self.draw_width_label.grid(padx=5,pady=5,row=6, column=0, sticky  = "W")
        seg_init = tk.DoubleVar(value = 0)
        self.draw_width = tk.Spinbox(self.param_frame, from_ = 0, to = 10, textvariable = seg_init, width = 25, increment = 0.01)
        seg_init.trace_add('write',lambda a,b,c : self.update_args('seg_width'))
        self.draw_width.grid(padx=5,pady=5,row=6, column=1)
        self.widget_dict['seg_width'] = seg_init

        flush_init = tk.BooleanVar(value = False)
        self.fluch_cache_widg = tk.Checkbutton(self.option_frame, text='Flush Cache', variable = flush_init, command = lambda : self.update_args('flush_map_cache'))
        self.fluch_cache_widg.grid(padx=5,pady=5,row=0, column=0)
        self.widget_dict['flush_map_cache'] = flush_init

        cull_init = tk.BooleanVar(value = False)
        self.do_cull_widg = tk.Checkbutton(self.option_frame, text='Do Cull', variable = cull_init, command = lambda : self.update_args('do_cull'))
        self.do_cull_widg.grid(padx=5,pady=5,row=0, column=1)
        self.widget_dict['do_cull'] = cull_init

        force_seg_init = tk.BooleanVar(value = False)
        self.force_seg_widg = tk.Checkbutton(self.option_frame, text='Force Segmentation', variable = force_seg_init, command = lambda : self.update_args('force_seg'))
        self.force_seg_widg.grid(padx=5,pady=5,row=0, column=2)
        self.widget_dict['force_seg'] = force_seg_init

        delta_lat = tk.StringVar(value = '--')
        self.lat_delta_label = tk.Label(self.info_frame, textvariable = delta_lat)
        self.lat_delta_label.grid(padx=5,pady=5,row=0, column=0, sticky  = "W")
        self.widget_dict['delta_lat'] = delta_lat
        
        delta_lon = tk.StringVar(value = '--')
        self.lon_delta_label = tk.Label(self.info_frame, textvariable = delta_lon)
        self.lon_delta_label.grid(padx=5,pady=5,row=0, column=1, sticky  = "W")
        self.widget_dict['delta_lon'] = delta_lon
        
        n_tiles = tk.StringVar(value = '--')
        self.n_tiles_label = tk.Label(self.info_frame, textvariable = n_tiles)
        self.n_tiles_label.grid(padx=5,pady=5,row=0, column=2, sticky  = "W")
        self.widget_dict['n_tiles'] = n_tiles

        self.ok_button = tk.Button(self.conf_frame, text = 'OK', padx = '30', command = self.make_map)
        self.ok_button.pack(padx=5,pady=5, side = 'left')
        
        self.restore_button = tk.Button(self.conf_frame, text = 'Restore Defaults', padx = '30', command = self.restore_options)
        self.restore_button.pack(padx=5,pady=5, side = 'right')
        
        self.update_widgets()
        
if __name__ == '__main__':   
    root = app()
