# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainForm
###########################################################################

class MainForm ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Road Network Visualisation", pos = wx.DefaultPosition, size = wx.Size( 400,400 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 400,400 ), wx.DefaultSize )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		paramSizer = wx.GridSizer( 0, 2, 0, 0 )

		self.north_label = wx.StaticText( self, wx.ID_ANY, u"North Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.north_label.Wrap( -1 )

		paramSizer.Add( self.north_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.north = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -90, 90, 0, 0.001 )
		self.north.SetDigits( 3 )
		paramSizer.Add( self.north, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

		self.south_label = wx.StaticText( self, wx.ID_ANY, u"South Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.south_label.Wrap( -1 )

		paramSizer.Add( self.south_label, 0, wx.ALL, 5 )

		self.south = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -90, 90, 0, 0.001 )
		self.south.SetDigits( 3 )
		paramSizer.Add( self.south, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.west_label = wx.StaticText( self, wx.ID_ANY, u"West Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.west_label.Wrap( -1 )

		paramSizer.Add( self.west_label, 0, wx.ALL, 5 )

		self.west = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -180, 180, 0, 0.001 )
		self.west.SetDigits( 3 )
		paramSizer.Add( self.west, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.east_label = wx.StaticText( self, wx.ID_ANY, u"East Limit (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.east_label.Wrap( -1 )

		paramSizer.Add( self.east_label, 0, wx.ALL, 5 )

		self.east = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, -180, 180, 0, 0.001 )
		self.east.SetDigits( 3 )
		paramSizer.Add( self.east, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.tile_res_label = wx.StaticText( self, wx.ID_ANY, u"Tile Width (deg):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.tile_res_label.Wrap( -1 )

		paramSizer.Add( self.tile_res_label, 0, wx.ALL, 5 )

		self.tile_res = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 20, 0, 0.001 )
		self.tile_res.SetDigits( 3 )
		paramSizer.Add( self.tile_res, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.image_res_label = wx.StaticText( self, wx.ID_ANY, u"Resolution:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.image_res_label.Wrap( -1 )

		paramSizer.Add( self.image_res_label, 0, wx.ALL, 5 )

		self.image_res = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 1e+06, 0, 10 )
		self.image_res.SetDigits( 0 )
		paramSizer.Add( self.image_res, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.draw_width_label = wx.StaticText( self, wx.ID_ANY, u"Line Width:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.draw_width_label.Wrap( -1 )

		paramSizer.Add( self.draw_width_label, 0, wx.ALL, 5 )

		self.draw_width = wx.SpinCtrlDouble( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 128,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0.000000, 0.01 )
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

		infoSizer = wx.WrapSizer( wx.HORIZONTAL, 0 )

		self.lat_delta_label = wx.StaticText( self, wx.ID_ANY, u"Latitude Delta: 30.0 deg", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lat_delta_label.SetLabelMarkup( u"Latitude Delta: 30.0 deg" )
		self.lat_delta_label.Wrap( -1 )

		infoSizer.Add( self.lat_delta_label, 1, wx.ALL|wx.ALIGN_BOTTOM, 5 )

		self.lon_delta_label = wx.StaticText( self, wx.ID_ANY, u"Longitude Delta: 150.0 deg", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lon_delta_label.Wrap( -1 )

		infoSizer.Add( self.lon_delta_label, 1, wx.ALL|wx.ALIGN_BOTTOM, 5 )

		self.n_tiles_label = wx.StaticText( self, wx.ID_ANY, u"Tiles: 420", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.n_tiles_label.Wrap( -1 )

		infoSizer.Add( self.n_tiles_label, 1, wx.ALIGN_BOTTOM|wx.ALL, 5 )


		bSizer2.Add( infoSizer, 0, wx.EXPAND, 5 )

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


		self.SetSizer( bSizer2 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.north.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('Nf') )
		self.south.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('Sf') )
		self.west.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('Wf') )
		self.east.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('Ef') )
		self.tile_res.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('tile_size') )
		self.image_res.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('res') )
		self.draw_width.Bind( wx.EVT_SPINCTRLDOUBLE, self.lambda a,b,c : self.update_args('seg_width') )
		self.flush_cache_widg.Bind( wx.EVT_CHECKBOX, self.lambda : self.update_args('flush_map_cache') )
		self.do_cull_widg.Bind( wx.EVT_CHECKBOX, self.lambda : self.update_args('do_cull') )
		self.force_set_widg.Bind( wx.EVT_CHECKBOX, self.lambda : self.update_args('force_seg') )
		self.ok_button.Bind( wx.EVT_BUTTON, self.make_map )
		self.cancel_button.Bind( wx.EVT_BUTTON, self.exit() )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def lambda a,b,c : self.update_args('Nf')( self, event ):
		event.Skip()

	def lambda a,b,c : self.update_args('Sf')( self, event ):
		event.Skip()

	def lambda a,b,c : self.update_args('Wf')( self, event ):
		event.Skip()

	def lambda a,b,c : self.update_args('Ef')( self, event ):
		event.Skip()

	def lambda a,b,c : self.update_args('tile_size')( self, event ):
		event.Skip()

	def lambda a,b,c : self.update_args('res')( self, event ):
		event.Skip()

	def lambda a,b,c : self.update_args('seg_width')( self, event ):
		event.Skip()

	def lambda : self.update_args('flush_map_cache')( self, event ):
		event.Skip()

	def lambda : self.update_args('do_cull')( self, event ):
		event.Skip()

	def lambda : self.update_args('force_seg')( self, event ):
		event.Skip()

	def make_map( self, event ):
		event.Skip()

	def exit()( self, event ):
		event.Skip()


