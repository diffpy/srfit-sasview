
################################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation. 
#
#See the license text in license.txt
#
#copyright 2008, University of Tennessee
################################################################################


import wx
import wx.aui
import os
import sys
import xml

try:
    # Try to find a local config
    import imp
    path = os.getcwd()
    if(os.path.isfile("%s/%s.py" % (path, 'local_config'))) or \
        (os.path.isfile("%s/%s.pyc" % (path, 'local_config'))):
        fObj, path, descr = imp.find_module('local_config', [path])
        config = imp.load_module('local_config', fObj, path, descr)  
    else:
        # Try simply importing local_config
        import local_config as config
except:
    # Didn't find local config, load the default 
    import config
    
import warnings
warnings.simplefilter("ignore")

import logging

from sans.guiframe.events import EVT_STATUS
from sans.guiframe.events import EVT_APPEND_BOOKMARK
from sans.guiframe.events import EVT_PANEL_ON_FOCUS
from sans.guiframe.events import StatusEvent
from sans.guiframe.events import NewPlotEvent
from sans.guiframe.gui_style import GUIFRAME
from sans.guiframe.gui_style import GUIFRAME_ID
from sans.guiframe.events import NewLoadedDataEvent
from sans.guiframe.data_panel import DataPanel
from sans.guiframe.panel_base import PanelBase
from sans.guiframe.gui_toolbar import GUIToolBar
from DataLoader.loader import Loader


PLOPANEL_WIDTH = 400
PLOPANEL_HEIGTH = 400
GUIFRAME_WIDTH = 1000
GUIFRAME_HEIGHT = 800
PROG_SPLASH_SCREEN = "images/danse_logo.png" 
EXTENSIONS =  ['.inv', '.fitv', '.prv', '.svs']

class ViewerFrame(wx.Frame):
    """
    Main application frame
    """
    
    def __init__(self, parent, title, 
                 size=(GUIFRAME_WIDTH, GUIFRAME_HEIGHT),
                 gui_style=GUIFRAME.DEFAULT_STYLE, 
                 pos=wx.DefaultPosition):
        """
        Initialize the Frame object
        """
        
        wx.Frame.__init__(self, parent=parent, title=title, pos=pos,size=size)
        # Preferred window size
        self._window_width, self._window_height = size
        self.__gui_style = gui_style
        
        # Logging info
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='sans_app.log',
                    filemode='w')        
        path = os.path.dirname(__file__)
        temp_path = os.path.join(path,'images')
        ico_file = os.path.join(temp_path,'ball.ico')
        if os.path.isfile(ico_file):
            self.SetIcon(wx.Icon(ico_file, wx.BITMAP_TYPE_ICO))
        else:
            temp_path = os.path.join(os.getcwd(),'images')
            ico_file = os.path.join(temp_path,'ball.ico')
            if os.path.isfile(ico_file):
                self.SetIcon(wx.Icon(ico_file, wx.BITMAP_TYPE_ICO))
        
        ## Application manager
        self.app_manager = None
        self._mgr = None
        #add current perpsective
        self._current_perspective = None
        self._plotting_plugin = None
        self._data_plugin = None
        #Menu bar and item
        self._menubar = None
        self._file_menu = None
        self._data_menu = None
        self._window_menu = None
        self._window_menu = None
        self._help_menu = None
        self._tool_menu = None
        self._applications_menu_pos = -1
        self._applications_menu = None
        self._edit_menu = None
        self._toolbar_menu = None
        self._save_appl_menu = None
        #tool bar
        self._toolbar = None
        ## Find plug-ins
        # Modify this so that we can specify the directory to look into
        self.plugins = []
        #add local plugin
        self.plugins += self._get_local_plugins()
        self.plugins += self._find_plugins()
        ## List of panels
        self.panels = {}

        # Default locations
        self._default_save_location = os.getcwd()        
        
        # Welcome panel
        self.defaultPanel = None
        #panel on focus
        self.panel_on_focus = None
        self.loader = Loader()   
         #data manager
        from data_manager import DataManager
        self._data_manager = DataManager()
        self._data_panel = DataPanel(parent=self)
        if self.panel_on_focus is not None:
            self._data_panel.set_panel_on_focus(self.panel_on_focus.window_caption)
        # Check for update
        #self._check_update(None)
        # Register the close event so it calls our own method
        wx.EVT_CLOSE(self, self.Close)
        # Register to status events
        self.Bind(EVT_STATUS, self._on_status_event)
        #Register add extra data on the same panel event on load
        self.Bind(EVT_PANEL_ON_FOCUS, self.set_panel_on_focus)
        self.Bind(EVT_APPEND_BOOKMARK, self.append_bookmark)
    
    def get_toolbar(self):
        """
        """
        return self._toolbar
    
    def set_panel_on_focus(self, event):
        """
        Store reference to the last panel on focus
        update the toolbar if available
        update edit menu if available
        """
        self.panel_on_focus = event.panel
        panel_name = 'No panel on focus'
        application_name = 'No Selected Application'
        if self.panel_on_focus is not None and self._data_panel is not None:
            panel_name = self.panel_on_focus.window_caption
            self._data_panel.set_panel_on_focus(panel_name)
            #update toolbar
            self._update_toolbar_helper()
            #update edit menu
            self.enable_edit_menu()
       
    def build_gui(self):
        """
        """
        # Set up the layout
        self._setup_layout()
        # Set up the menu
        self._setup_menus()
        # set tool bar
        self._setup_tool_bar()
        #self.Fit()
        #self._check_update(None)
             
    def _setup_layout(self):
        """
        Set up the layout
        """
        # Status bar
        from gui_statusbar import StatusBar
        self.sb = StatusBar(self, wx.ID_ANY)
        self.SetStatusBar(self.sb)
        # Add panel
        default_flag = wx.aui.AUI_MGR_DEFAULT#| wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE
        self._mgr = wx.aui.AuiManager(self, flags=default_flag)
   
        # Load panels
        self._load_panels()
        self.set_default_perspective()
        self._mgr.Update()
        
    def SetStatusText(self, *args, **kwds):
        """
        """
        number = self.sb.get_msg_position()
        wx.Frame.SetStatusText(number=number, *args, **kwds)
        
    def PopStatusText(self, *args, **kwds):
        """
        """
        field = self.sb.get_msg_position()
        wx.Frame.PopStatusText(field=field)
        
    def PushStatusText(self, *args, **kwds):
        """
        """
        field = self.sb.get_msg_position()
        wx.Frame.PushStatusText(self, field=field, string=string)

    def add_perspective(self, plugin):
        """
        Add a perspective if it doesn't already
        exist.
        """
        is_loaded = False
        for item in self.plugins:
            if plugin.__class__ == item.__class__:
                msg = "Plugin %s already loaded" % plugin.__class__.__name__
                logging.info(msg)
                is_loaded = True    
        if not is_loaded:
            self.plugins.append(plugin)
      
    def _get_local_plugins(self):
        """
        get plugins local to guiframe and others 
        """
        plugins = []
        #import guiframe local plugins
        #check if the style contain guiframe.dataloader
        style1 = self.__gui_style & GUIFRAME.DATALOADER_ON
        style2 = self.__gui_style & GUIFRAME.PLOTTING_ON
        if style1 == GUIFRAME.DATALOADER_ON:
            try:
                from sans.guiframe.local_perspectives.data_loader import data_loader
                self._data_plugin = data_loader.Plugin()
                plugins.append(self._data_plugin)
            except:
                msg = "ViewerFrame._get_local_plugins:"
                msg += "cannot import dataloader plugin.\n %s" % sys.exc_value
                logging.error(msg)
        if style2 == GUIFRAME.PLOTTING_ON:
            try:
                from sans.guiframe.local_perspectives.plotting import plotting
                self._plotting_plugin = plotting.Plugin()
                plugins.append(self._plotting_plugin)
            except:
                msg = "ViewerFrame._get_local_plugins:"
                msg += "cannot import plotting plugin.\n %s" % sys.exc_value
                logging.error(msg)
     
        return plugins
    
    def _find_plugins(self, dir="perspectives"):
        """
        Find available perspective plug-ins
        
        :param dir: directory in which to look for plug-ins
        
        :return: list of plug-ins
        
        """
        import imp
        plugins = []
        # Go through files in panels directory
        try:
            list = os.listdir(dir)
            ## the default panel is the panel is the last plugin added
            for item in list:
                toks = os.path.splitext(os.path.basename(item))
                name = None
                if not toks[0] == '__init__':
                    
                    if toks[1] == '.py' or toks[1] == '':
                        name = toks[0]
                
                    path = [os.path.abspath(dir)]
                    file = None
                    try:
                        if toks[1] == '':
                            mod_path = '.'.join([dir, name])
                            module = __import__(mod_path, globals(),
                                                locals(), [name])
                        else:
                            (file, path, info) = imp.find_module(name, path)
                            module = imp.load_module( name, file, item, info)
                        if hasattr(module, "PLUGIN_ID"):
                            try: 
                                plug = module.Plugin()
                                if plug.set_default_perspective():
                                    self._current_perspective = plug
                                plugins.append(plug)
                                msg = "Found plug-in: %s" % module.PLUGIN_ID
                                logging.info(msg)
                            except:
                                msg = "Error accessing PluginPanel"
                                msg += " in %s\n  %s" % (name, sys.exc_value)
                                config.printEVT(msg)
                    except:
                        print sys.exc_value
                        msg = "ViewerFrame._find_plugins: %s" % sys.exc_value
                        logging.error(msg)
                    finally:
                        if not file == None:
                            file.close()
        except:
            # Should raise and catch at a higher level and 
            # display error on status bar
            pass   
        return plugins
    
    def set_welcome_panel(self, panel_class):
        """
        Sets the default panel as the given welcome panel 
        
        :param panel_class: class of the welcome panel to be instantiated
        
        """
        self.defaultPanel = panel_class(self, -1, style=wx.RAISED_BORDER)
        
    def _get_panels_size(self, p):
        """
        find the proper size of the current panel
        get the proper panel width and height
        """
        panel_height_min = self._window_height
        panel_width_min = self._window_width 
        style = self.__gui_style & (GUIFRAME.MANAGER_ON)
        if self._data_panel is not None  and (p == self._data_panel):
            panel_width_min = self._window_width * 5/25 
            return panel_width_min, panel_height_min
        if hasattr(p, "CENTER_PANE") and p.CENTER_PANE:
            style = self.__gui_style & (GUIFRAME.PLOTTING_ON|GUIFRAME.MANAGER_ON)
            if style == (GUIFRAME.PLOTTING_ON|GUIFRAME.MANAGER_ON):
                panel_width_min = self._window_width * 15/25 
            return panel_width_min, panel_height_min
        return panel_width_min, panel_height_min
    
    def _load_panels(self):
        """
        Load all panels in the panels directory
        """
        
        # Look for plug-in panels
        panels = []    
        for item in self.plugins:
            if hasattr(item, "get_panels"):
                ps = item.get_panels(self)
                panels.extend(ps)
       
        # Show a default panel with some help information
        # It also sets the size of the application windows
        #TODO: Use this for slpash screen
        if self.defaultPanel is None:
            self.defaultPanel = DefaultPanel(self, -1, style=wx.RAISED_BORDER)
        # add a blank default panel always present 
        self.panels["default"] = self.defaultPanel
        self._mgr.AddPane(self.defaultPanel, wx.aui.AuiPaneInfo().
                              Name("default").
                              Center().
                              CloseButton(False).
                              MinimizeButton(False).
                              # This is where we set the size of
                              # the application window
                              BestSize(wx.Size(self._window_width, 
                                               self._window_height)).
                              Show())
        #add data panel 
        self.panels["data_panel"] = self._data_panel
        w, h = self._get_panels_size(self._data_panel)
        self._mgr.AddPane(self._data_panel, wx.aui.AuiPaneInfo().
                              Name(self._data_panel.window_name).
                              Left().
                              MinimizeButton().
                              TopDockable(False).
                              BottomDockable(False).
                              LeftDockable(True).
                              RightDockable(False).
                              BestSize(wx.Size(w, h)).
                              Hide())
        style = self.__gui_style & GUIFRAME.MANAGER_ON
        if style != GUIFRAME.MANAGER_ON:
            self._mgr.GetPane(self.panels["data_panel"].window_name).Hide()
        else:
            self._mgr.GetPane(self.panels["data_panel"].window_name).Show()
            
        # Add the panels to the AUI manager
        for panel_class in panels:
            p = panel_class
            id = wx.NewId()
            w, h = self._get_panels_size(p)
            # Check whether we need to put this panel
            # in the center pane
            if hasattr(p, "CENTER_PANE") and p.CENTER_PANE:
                if p.CENTER_PANE:
                    self.panels[str(id)] = p
                    self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                                          Name(p.window_name).Caption(p.window_caption).
                                           #CenterPane().
                                            Center().
                                            CloseButton(False).
                                            MinimizeButton(False).
                                           MinSize(wx.Size(w, h)).
                                           Hide())
            else:
                self.panels[str(id)] = p
                self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                                  Name(p.window_name).Caption(p.window_caption).
                                  Right().
                                  Dock().
                                  TopDockable().
                                  BottomDockable().
                                  LeftDockable().
                                  RightDockable().
                                  MinimizeButton().
                                  Hide())        
      
    def get_context_menu(self, graph=None):
        """
        Get the context menu items made available 
        by the different plug-ins. 
        This function is used by the plotting module
        """
        menu_list = []
        for item in self.plugins:
            if hasattr(item, "get_context_menu"):
                menu_list.extend(item.get_context_menu(graph))
        return menu_list
        
    def popup_panel(self, p):
        """
        Add a panel object to the AUI manager
        
        :param p: panel object to add to the AUI manager
        
        :return: ID of the event associated with the new panel [int]
        
        """
        ID = wx.NewId()
        self.panels[str(ID)] = p
        count = 0
        for item in self.panels:
            if self.panels[item].window_name.startswith(p.window_name): 
                count += 1
        windowname = p.window_name
        caption = p.window_caption
        if count > 0:
            windowname += str(count+1)
            caption += (' '+str(count))
        p.window_name = windowname
        p.window_caption = caption
            
        style1 = self.__gui_style & GUIFRAME.FIXED_PANEL
        style2 = self.__gui_style & GUIFRAME.FLOATING_PANEL
        if style1 == GUIFRAME.FIXED_PANEL:
            self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                              Name(windowname).Caption(caption).
                              MinimizeButton().
                              Resizable(True).
                              # Use a large best size to make sure the AUI 
                              # manager takes all the available space
                              BestSize(wx.Size(PLOPANEL_WIDTH, PLOPANEL_HEIGTH)))
            self._popup_fixed_panel(p)
    
        elif style2 == GUIFRAME.FLOATING_PANEL:
            self._mgr.AddPane(p, wx.aui.AuiPaneInfo().
                              Name(windowname).Caption(caption).
                              MinimizeButton().
                              Resizable(True).
                              # Use a large best size to make sure the AUI
                              #  manager takes all the available space
                              BestSize(wx.Size(PLOPANEL_WIDTH, PLOPANEL_HEIGTH)))
            self._popup_floating_panel(p)
            
        pane = self._mgr.GetPane(windowname)
        self._mgr.MaximizePane(pane)
        self._mgr.RestoreMaximizedPane()
        # Register for showing/hiding the panel
        wx.EVT_MENU(self, ID, self._on_view)
        
        self._mgr.Update()
        return ID
        
    def _setup_menus(self):
        """
        Set up the application menus
        """
        # Menu
        self._menubar = wx.MenuBar()
        self._add_menu_file()
        self._add_menu_data()
        self._add_menu_application()
        self._add_menu_edit()
        self._add_menu_tool()
        self._add_current_plugin_menu()
        self._add_menu_window()
        self._add_help_menu()
        self.SetMenuBar(self._menubar)
        
    def _setup_tool_bar(self):
        """
        add toolbar to the frame
        """
        #set toolbar
        self._toolbar = GUIToolBar(self, -1)
        self.SetToolBar(self._toolbar)
        self._update_toolbar_helper()
        #self._on_hide_toolbar(event=None)
    
    def _update_toolbar_helper(self):
        """
        """
        application_name = 'No Selected Application'
        panel_name = 'No Panel on Focus'
        self._toolbar.update_toolbar(self.panel_on_focus)
        if self._current_perspective is not None:
            application_name = self._current_perspective.sub_menu
        if self.panel_on_focus is not None:
            panel_name = self.panel_on_focus.window_caption
        self._toolbar.update_button(application_name=application_name, 
                                        panel_name=panel_name)
        self._toolbar.Realize()
        
    def _add_menu_tool(self):
        """
        Tools menu
        Go through plug-ins and find tools to populate the tools menu
        """
        style = self.__gui_style & GUIFRAME.TOOL_ON
        if style == GUIFRAME.TOOL_ON:
            self._tool_menu = None
            for item in self.plugins:
                if hasattr(item, "get_tools"):
                    for tool in item.get_tools():
                        # Only create a menu if we have at least one tool
                        if self._tool_menu is None:
                            self._tool_menu = wx.Menu()
                        id = wx.NewId()
                        self._tool_menu.Append(id, tool[0], tool[1])
                        wx.EVT_MENU(self, id, tool[2])
            if self._tool_menu is not None:
                self._menubar.Append(self._tool_menu, '&Tools')
                
    def _add_current_plugin_menu(self):
        """
        add current plugin menu
        Look for plug-in menus
        Add available plug-in sub-menus. 
        """
        if (self._menubar is None) or (self._current_perspective is None):
            return
        #replace or add a new menu for the current plugin
        name = 'Others'
        pos = self._menubar.FindMenu(name)
        if pos != -1:
            menu_list = self._current_perspective.populate_menu(self)
            if menu_list:
                for (menu, _) in menu_list:
                    hidden_menu = self._menubar.Replace(pos, menu, name)  
            else:
                hidden_menu = self._menubar.Remove(pos)
            #get the position of the menu when it first added
            self._plugin_menu_pos = pos 
        else:
            menu_list = self._current_perspective.populate_menu(self)
            if menu_list:
                for (menu, _) in menu_list:
                    if self._applications_menu_pos == -1:
                        self._menubar.Append(menu, name)
                    else:
                        self._menubar.Insert(self._applications_menu_pos, menu, name)
                  
    def _add_help_menu(self):
        """
        add help menu
        """
        # Help menu
        self._help_menu = wx.Menu()
        style = self.__gui_style & GUIFRAME.WELCOME_PANEL_ON
        if style == GUIFRAME.WELCOME_PANEL_ON:
            # add the welcome panel menu item
            if self.defaultPanel is not None:
                id = wx.NewId()
                self._help_menu.Append(id, '&Welcome', '')
                self._help_menu.AppendSeparator()
                wx.EVT_MENU(self, id, self.show_welcome_panel)
        # Look for help item in plug-ins 
        for item in self.plugins:
            if hasattr(item, "help"):
                id = wx.NewId()
                self._help_menu.Append(id,'&%s help' % item.sub_menu, '')
                wx.EVT_MENU(self, id, item.help)
        if config._do_aboutbox:
            id = wx.NewId()
            self._help_menu.Append(id,'&About', 'Software information')
            wx.EVT_MENU(self, id, self._onAbout)
        
        # Checking for updates needs major refactoring to work with py2exe
        # We need to make sure it doesn't hang the application if the server
        # is not up. We also need to make sure there's a proper executable to
        # run if we spawn a new background process.
        #id = wx.NewId()
        #self._help_menu.Append(id,'&Check for update', 
        #'Check for the latest version of %s' % config.__appname__)
        #wx.EVT_MENU(self, id, self._check_update)
        self._menubar.Append(self._help_menu, '&Help')
            
    def _add_menu_window(self):
        """
        add a menu window to the menu bar
        Window menu
        Attach a menu item for each panel in our
        panel list that also appears in a plug-in.
        
        Only add the panel menu if there is only one perspective and
        it has more than two panels.
        Note: the first plug-in is always the plotting plug-in. 
        The first application
        #plug-in is always the second one in the list.
        """
        self._window_menu = wx.Menu()
        if self._plotting_plugin is not None:
            for (menu, name) in self._plotting_plugin.populate_menu(self):
                self._window_menu.AppendSubMenu(menu, name)
        self._menubar.Append(self._window_menu, '&Window')
     
        style = self.__gui_style & GUIFRAME.MANAGER_ON
        if style == GUIFRAME.MANAGER_ON:
            id = wx.NewId()
            self._window_menu.Append(id,'&Data Manager', '')
            wx.EVT_MENU(self, id, self.show_data_panel)
            
        style = self.__gui_style & GUIFRAME.PLOTTING_ON
        if style == GUIFRAME.PLOTTING_ON:
            self._window_menu.AppendSeparator()
            id = wx.NewId()
            preferences_menu = wx.Menu()
            hint = "Plot panels will floating"
            preferences_menu.Append(id, '&Floating Plot Panel', hint)
            wx.EVT_MENU(self, id, self.set_plotpanel_floating)
            id = wx.NewId()
            hint = "Plot panels will displayed within the frame"
            preferences_menu.Append(id, '&Fixed Plot Panel', hint)
            wx.EVT_MENU(self, id, self.set_plotpanel_fixed)
            id = wx.NewId()
            style1 = self.__gui_style & GUIFRAME.MULTIPLE_APPLICATIONS
            if style1 == GUIFRAME.MULTIPLE_APPLICATIONS:
                id = wx.NewId()
                self._toolbar_menu = preferences_menu.Append(id,'&Hide Toolbar', '')
                wx.EVT_MENU(self, id, self._on_hide_toolbar)
            self._window_menu.AppendSubMenu(preferences_menu,'&Preferences')
        if self._window_menu.GetMenuItemCount() == 0:
            pos = self._menubar.FindMenu('Window')
            self._menubar.Remove(pos)
        #wx.EVT_MENU(self, id, self.show_preferences_panel)   
        """
        if len(self.plugins) == 2:
            plug = self.plugins[1]
            pers = plug.get_perspective()
       
            if len(pers) > 1:
                self._window_menu = wx.Menu()
                for item in self.panels:
                    if item == 'default':
                        continue
                    panel = self.panels[item]
                    if panel.window_name in pers:
                        self._window_menu.Append(int(item),
                                                  panel.window_caption,
                                        "Show %s window" % panel.window_caption)
                        wx.EVT_MENU(self, int(item), self._on_view)
                self._menubar.Append(self._window_menu, '&Window')
                """
                
    def _add_menu_application(self):
        """
        
        # Attach a menu item for each defined perspective or application.
        # Only add the perspective menu if there are more than one perspectives
        add menu application
        """
        style = self.__gui_style & GUIFRAME.MULTIPLE_APPLICATIONS
        if style == GUIFRAME.MULTIPLE_APPLICATIONS:
            plug_data_count = False
            plug_no_data_count = False
            self._applications_menu = wx.Menu()
            separator = self._applications_menu.AppendSeparator()
            for plug in self.plugins:
                if len(plug.get_perspective()) > 0:
                    id = wx.NewId()
                    if plug.use_data():
                        self._applications_menu.InsertCheckItem(0, id, plug.sub_menu,
                                      "Switch to application: %s" % plug.sub_menu)
                        plug_data_count = True
                    else:
                        plug_no_data_count = True
                        self._applications_menu.AppendCheckItem(id, plug.sub_menu,
                                      "Switch to application: %s" % plug.sub_menu)
                    wx.EVT_MENU(self, id, plug.on_perspective)
            if not (plug_data_count and  plug_no_data_count):
                self._applications_menu.RemoveItem(separator)
            self._menubar.Append(self._applications_menu, '&Applications')
            self._check_applications_menu()
            
    def _add_menu_file(self):
        """
        add menu file
        """
        
         # File menu
        self._file_menu = wx.Menu()
        style = self.__gui_style & GUIFRAME.DATALOADER_ON
        if style == GUIFRAME.DATALOADER_ON:
            # some menu of plugin to be seen under file menu
            hint_load_file = "Read state's files and load"
            hint_load_file += " them into the application"
            id = wx.NewId()
            self._save_appl_menu = self._file_menu.Append(id, 
                                    '&Open State from File', hint_load_file)
            wx.EVT_MENU(self, id, self._on_open_state)
            id = wx.NewId()
            self._save_appl_menu = self._file_menu.Append(id, 
                                                          '&Save Application',
                                 'Save state of the current active application')
            wx.EVT_MENU(self, id, self._on_save_application)
            id = wx.NewId()
            self._file_menu.Append(id, '&Save Project',
                                 'Save the state of the whole application')
            wx.EVT_MENU(self, id, self._on_save_project)
            self._file_menu.AppendSeparator()
        
        id = wx.NewId()
        self._file_menu.Append(id, '&Quit', 'Exit') 
        wx.EVT_MENU(self, id, self.Close)
        # Add sub menus
        self._menubar.Append(self._file_menu, '&File')
        
    def _add_menu_edit(self):
        """
        add menu edit
        """
        # Edit Menu
        self._edit_menu = wx.Menu()
        self._edit_menu.Append(GUIFRAME_ID.UNDO_ID, '&Undo', 
                               'Undo the previous action')
        wx.EVT_MENU(self, GUIFRAME_ID.UNDO_ID, self.on_undo_panel)
        self._edit_menu.Append(GUIFRAME_ID.REDO_ID, '&Redo', 
                               'Redo the previous action')
        wx.EVT_MENU(self, GUIFRAME_ID.REDO_ID, self.on_redo_panel)
        #self._edit_menu.AppendSeparator()
        #self._edit_menu.Append(GUIFRAME_ID.BOOKMARK_ID, '&Bookmark', 
        #                       'bookmark current panel')
        #wx.EVT_MENU(self, GUIFRAME_ID.BOOKMARK_ID, self.append_bookmark)
        self._edit_menu.Append(GUIFRAME_ID.SAVE_ID, '&Save As', 
                               'Save current panel into file')
        wx.EVT_MENU(self, GUIFRAME_ID.SAVE_ID, self.on_save_panel)
        self._edit_menu.AppendSeparator()
        self._edit_menu.Append(GUIFRAME_ID.PREVIEW_ID, '&Print Preview',
                               'Preview current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.PREVIEW_ID, self.on_preview_panel)
        self._edit_menu.Append(GUIFRAME_ID.PRINT_ID, '&Print',
                               'Print current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.PRINT_ID, self.on_print_panel)
        self._edit_menu.AppendSeparator()
        self._edit_menu.Append(GUIFRAME_ID.ZOOM_ID, '&Zoom',
                               'Zoom current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.ZOOM_ID, self.on_zoom_panel)
        self._edit_menu.Append(GUIFRAME_ID.ZOOM_IN_ID, '&Zoom In',
                               'Zoom in current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.ZOOM_IN_ID, self.on_zoom_in_panel)
        self._edit_menu.Append(GUIFRAME_ID.ZOOM_OUT_ID, '&Zoom Out', 
                               'Zoom out current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.ZOOM_OUT_ID, self.on_zoom_out_panel)
        self._edit_menu.Append(GUIFRAME_ID.DRAG_ID, '&Drag',
                               'Drag current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.DRAG_ID, self.on_drag_panel)
        self._edit_menu.Append(GUIFRAME_ID.RESET_ID, '&Reset', 
                               'Reset current panel')
        wx.EVT_MENU(self, GUIFRAME_ID.RESET_ID, self.on_reset_panel)
        self._menubar.Append(self._edit_menu,  '&Edit')
        self.enable_edit_menu()
        
    def get_style(self):
        """
        """
        return  self.__gui_style
    
    def _add_menu_data(self):
        """
        Add menu item item data to menu bar
        """
        if self._data_plugin is not None:
            menu_list = self._data_plugin.populate_menu(self)
            if menu_list:
                for (menu, name) in menu_list:
                    self._menubar.Append(menu, name)
            
    def _on_hide_toolbar(self, event=None):
        """
        hide or show toolbar
        """
        if self._toolbar is None:
            return
        if self._toolbar.IsShown():
            if self._toolbar_menu is not None:
                self._toolbar_menu.SetItemLabel('Show Toolbar')
            self._toolbar.Hide()
        else:
            if self._toolbar_menu is not None:
                self._toolbar_menu.SetItemLabel('Hide Toolbar')
            self._toolbar.Show()
        self._toolbar.Realize()
        
    def _on_status_event(self, evt):
        """
        Display status message
        """
        self.sb.set_status(event=evt)
       
    def _on_view(self, evt):
        """
        A panel was selected to be shown. If it's not already
        shown, display it.
        
        :param evt: menu event
        
        """
        self.show_panel(evt.GetId())
        
    def on_close_welcome_panel(self):
        """
        Close the welcome panel
        """
        if self.defaultPanel is None:
            return 
        self._mgr.GetPane(self.panels["default"].window_name).Hide()
        self._mgr.Update()
        # set a default perspective
        self.set_default_perspective()
        
    def show_welcome_panel(self, event):
        """    
        Display the welcome panel
        """
        if self.defaultPanel is None:
            return 
        for id in self.panels.keys():
            if id  ==  'default':
                # Show default panel
                if not self._mgr.GetPane(self.panels["default"].window_name).IsShown():
                    self._mgr.GetPane(self.panels["default"].window_name).Show(True)
            elif id == "data_panel":
                flag = self._mgr.GetPane(self.panels["data_panel"].window_name).IsShown()
                self._mgr.GetPane(self.panels["data_panel"].window_name).Show(flag)
            else:
                self._mgr.GetPane(self.panels[id].window_name).IsShown()
                self._mgr.GetPane(self.panels[id].window_name).Hide()
        self._mgr.Update()
       
    def show_panel(self, uid):
        """
        Shows the panel with the given id
        
        :param uid: unique ID number of the panel to show
        
        """
        ID = str(uid)
        config.printEVT("show_panel: %s" % ID)
        if ID in self.panels.keys():
            if not self._mgr.GetPane(self.panels[ID].window_name).IsShown():
                self._mgr.GetPane(self.panels[ID].window_name).Show()
                # Hide default panel
                self._mgr.GetPane(self.panels["default"].window_name).Hide()
            self._mgr.Update()
    
    def clear_panel(self):
        """
        """
        for item in self.panels:
            try:
                self.panels[item].clear_panel()
            except:
                pass
            
    def create_gui_data(self, data, path=None):
        """
        """
        return self._data_manager.create_gui_data(data, path)
    
    def get_data(self, path):
        """
        """
        message = ""
        log_msg = ''
        output = []
        error_message = ""
        basename  = os.path.basename(path)
        root, extension = os.path.splitext(basename)
        if extension.lower() not in EXTENSIONS:
            log_msg = "File Loader cannot "
            log_msg += "load: %s\n" % str(basename)
            log_msg += "Try Data opening...."
            logging.info(log_msg)
            self.load_complete(output=output, error_message=error_message,
                   message=log_msg, path=path)    
            return
        
        #reading a state file
        for plug in self.plugins:
            reader, ext = plug.get_extensions()
            if reader is not None:
                #read the state of the single plugin
                if extension == ext:
                    reader.read(path)
                    return
                elif extension == '.svs':
                    reader.read(path)
        
        style = self.__gui_style & GUIFRAME.MANAGER_ON
        if style == GUIFRAME.MANAGER_ON:
            if self._data_panel is not None:
                data_state = self._data_manager.get_selected_data()
                self._data_panel.load_data_list(data_state)
                self._mgr.GetPane(self._data_panel.window_name).Show(True)
                        
    def _on_open_state(self, event):
        """
        """
        path = None
        if self._default_save_location == None:
            self._default_save_location = os.getcwd()
 
        wlist = ['SansView files (*.svs)|*.svs',
                  'P(r) files (*.prv)|*.prv',
                  'Fitting files (*.fitv)|*.fitv',
                  'Invariant files (*.inv)|*.inv']
        wlist = '|'.join(wlist)
        dlg = wx.FileDialog(self, 
                            "Choose a file", 
                            self._default_save_location, "",
                             wlist)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path is not None:
                self._default_save_location = os.path.dirname(path)
        dlg.Destroy()
        if path and os.path.isfile(path):
            basename  = os.path.basename(path)
            if  basename.endswith('.svs'):
                #remove panels for new states
                for plug in self.plugins:
                    plug.clear_panel()
                    self.panel_on_focus = None
                
            self.get_data(path)
                
        if self.defaultPanel is not None and \
            self._mgr.GetPane(self.panels["default"].window_name).IsShown():
            self.on_close_welcome_panel()
    
    def _on_save_application(self, event):
        """
        save the state of the current active application
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_save(event)
            
    def _on_save_project(self, event):
        """
        save the state of the current active application
        """
        ## Default file location for save
        self._default_save_location = os.getcwd()
        if self._current_perspective is  None:
            return
        reader, ext = self._current_perspective.get_extensions()
        path = None
        dlg = wx.FileDialog(self, "Save Project file",
                            self._default_save_location, "", '.svs', wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._default_save_location = os.path.dirname(path)
        else:
            return None
        dlg.Destroy()
        if path is None:
            return
        # default cansas xml doc
        doc = None
        for panel in self.panels.values():
            doc = self.on_save_helper(doc, reader, panel, path)
        
            
    def on_save_helper(self, doc, reader, panel, path):
        """
        Save state into a file
        """
        try:
            data = panel.get_data()
            state = panel.get_state()
            if reader is not None:
                if data is not None:
                    new_doc = reader.write_toXML(data, state)
                    if hasattr(doc, "firstChild"):
                        child = new_doc.firstChild.firstChild
                        doc.firstChild.appendChild(child)  
                    else:
                        doc = new_doc 
        except: 
            raise
            #pass
        # Write the XML document
        if doc != None:
            fd = open(path, 'w')
            fd.write(doc.toprettyxml())
            fd.close()
        else:
            raise
            #print "Nothing to save..."
            #raise RuntimeError, "%s is not a SansView (.svs) file..." % path
        return doc

    def quit_guiframe(self):
        """
        Pop up message to make sure the user wants to quit the application
        """
        message = "Do you really want to quit \n"
        message += "this application?"
        dial = wx.MessageDialog(self, message, 'Question',
                           wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
        if dial.ShowModal() == wx.ID_YES:
            return True
        else:
            return False    
        
    def Close(self, event=None):
        """
        Quit the application
        """
        #flag = self.quit_guiframe()
        if True:
            wx.Exit()
            sys.exit()

    def _check_update(self, event=None): 
        """
        Check with the deployment server whether a new version
        of the application is available.
        A thread is started for the connecting with the server. The thread calls
        a call-back method when the current version number has been obtained.
        """
        if hasattr(config, "__update_URL__"):
            import version
            checker = version.VersionThread(config.__update_URL__,
                                            self._process_version,
                                            baggage=event==None)
            checker.start()  
    
    def _process_version(self, version, standalone=True):
        """
        Call-back method for the process of checking for updates.
        This methods is called by a VersionThread object once the current
        version number has been obtained. If the check is being done in the
        background, the user will not be notified unless there's an update.
        
        :param version: version string
        :param standalone: True of the update is being checked in 
           the background, False otherwise.
           
        """
        try:
            if cmp(version, config.__version__) > 0:
                msg = "Version %s is available! See the Help "
                msg += "menu to download it." % version
                self.SetStatusText(msg)
                if not standalone:
                    import webbrowser
                    webbrowser.open(config.__download_page__)
            else:
                if not standalone:
                    msg = "You have the latest version"
                    msg += " of %s" % config.__appname__
                    self.SetStatusText(msg)
        except:
            msg = "guiframe: could not get latest application"
            msg += " version number\n  %s" % sys.exc_value
            logging.error(msg)
            if not standalone:
                msg = "Could not connect to the application server."
                msg += " Please try again later."
                self.SetStatusText(msg)
                    
    def _onAbout(self, evt):
        """
        Pop up the about dialog
        
        :param evt: menu event
        
        """
        if config._do_aboutbox:
            import aboutbox 
            dialog = aboutbox.DialogAbout(None, -1, "")
            dialog.ShowModal()            
            
    def set_manager(self, manager):
        """
        Sets the application manager for this frame
        
        :param manager: frame manager
        """
        self.app_manager = manager
        
    def post_init(self):
        """
        This initialization method is called after the GUI 
        has been created and all plug-ins loaded. It calls
        the post_init() method of each plug-in (if it exists)
        so that final initialization can be done.
        """
        for item in self.plugins:
            if hasattr(item, "post_init"):
                item.post_init()
        
    def set_default_perspective(self):
        """
        Choose among the plugin the first plug-in that has 
        "set_default_perspective" method and its return value is True will be
        as a default perspective when the welcome page is closed
        """
        for item in self.plugins:
            if hasattr(item, "set_default_perspective"):
                if item.set_default_perspective():
                    item.on_perspective(event=None)
                    return 
        
    def set_perspective(self, panels):
        """
        Sets the perspective of the GUI.
        Opens all the panels in the list, and closes
        all the others.
        
        :param panels: list of panels
        """
        for item in self.panels:
            # Check whether this is a sticky panel
            if hasattr(self.panels[item], "ALWAYS_ON"):
                if self.panels[item].ALWAYS_ON:
                    continue 
            if self.panels[item].window_name in panels:
                if not self._mgr.GetPane(self.panels[item].window_name).IsShown():
                    self._mgr.GetPane(self.panels[item].window_name).Show()
            else:
                # always show the data panel if enable
                style = self.__gui_style & GUIFRAME.MANAGER_ON
                if (style == GUIFRAME.MANAGER_ON) and self.panels[item] == self._data_panel:
                    if 'data_panel' in self.panels.keys():
                        flag = self._mgr.GetPane(self.panels['data_panel'].window_name).IsShown()
                        self._mgr.GetPane(self.panels['data_panel'].window_name).Show(flag)
                else:
                    if self._mgr.GetPane(self.panels[item].window_name).IsShown():
                        self._mgr.GetPane(self.panels[item].window_name).Hide()
        self._mgr.Update()
        
    def show_data_panel(self, event=None):
        """
        show the data panel
        """
        style = self.__gui_style & GUIFRAME.MANAGER_ON
        if style == GUIFRAME.MANAGER_ON:
            pane = self._mgr.GetPane(self.panels["data_panel"].window_name)
            #if not pane.IsShown():
            pane.Show(True)
            self._mgr.Update()
 
    def add_data(self, data_list):
        """
        receive a list of data . store them its data manager if possible
        determine if data was be plot of send to data perspectives
        """
        #send a list of available data to plotting plugin
        avalaible_data = []
        if self._data_manager is not None:
            self._data_manager.add_data(data_list)
            avalaible_data = self._data_manager.get_all_data()

        style = self.__gui_style & GUIFRAME.MANAGER_ON
        if style == GUIFRAME.MANAGER_ON:
            if self._data_panel is not None:
                data_state = self._data_manager.get_selected_data()
                self._data_panel.load_data_list(data_state)
                self._mgr.GetPane(self._data_panel.window_name).Show(True)
                #wait for button press from the data panel to send data
        else:
            #automatically send that to the current perspective
            style = self.__gui_style & GUIFRAME.SINGLE_APPLICATION
            if style == GUIFRAME.SINGLE_APPLICATION:
                self.set_data(data_list)
                
    def get_data_from_panel(self, data_id, plot=False,append=False):
        """
        receive a list of data key retreive the data from data manager and set 
        then to the current perspective
        """
        data_dict = self._data_manager.get_by_id(data_id)
        data_list = []
        for data_state in data_dict.values():
            data_list.append(data_state.data)
        if plot:
            self.plot_data(data_list, append=append)
        else:
            #sent data to active application
            self.set_data(data_list=data_list)
       
        
    def set_data(self, data_list):
        """
        set data to current perspective
        """
        if self._current_perspective is not None:
            try:
                self._current_perspective.set_data(data_list)
            except:
                msg = str(sys.exc_value)
                wx.PostEvent(self, StatusEvent(status=msg, info="error"))
        else:
            msg = "Guiframe does not have a current perspective"
            logging.info(msg)
            
    def plot_data(self, data_list, append=False):
        """
        send a list of data to plot
        """
        if not data_list:
            message = "Please check data to plot or append"
            wx.PostEvent(self, StatusEvent(status=message, info='warning'))
            return 
        for new_plot in data_list:
            if append:
                if self.panel_on_focus is None or \
                    not self.enable_add_data(new_plot):
                    message = "cannot append plot. No plot panel on focus!"
                    message += "please click on any available plot to set focus"
                    wx.PostEvent(self, StatusEvent(status=message, 
                                                   info='warning'))
                    return 
                else:
                    if self.enable_add_data(new_plot) and \
                    hasattr(self.panel_on_focus, 'group_id'):
                        new_plot.group_id = self.panel_on_focus.group_id
            wx.PostEvent(self, NewPlotEvent(plot=new_plot,
                                                  title=str(new_plot.title)))
            
    def add_theory(self, data_id, theory):
        """
        """
        self._data_manager.append_theory(data_id, theory)
        style = self.__gui_style & GUIFRAME.MANAGER_ON
        if style == GUIFRAME.MANAGER_ON:
            if self._data_panel is not None:
                data_state = self._data_manager.get_by_id([data_id])
                self._data_panel.load_data_list(data_state)
                
    def remove_data(self, data_id, theory_id=None, delete_all=True):
        """
        Delete data state if data_id is provide
        delete theory created with data of id data_id if theory_id is provide
        if delete all true: delete the all state
        else delete theory
        """
        self._data_manager.delete_data(data_id=data_id, 
                                       theory_id=theory_id, 
                                       delete_all=delete_all)
        for plug in self.plugins:
            plug.delete_data(data_id)
            
        
    def set_current_perspective(self, perspective):
        """
        set the current active perspective 
        """
        self._current_perspective = perspective
        name = "No current Application selected"
        if self._current_perspective is not None:
            self._add_current_plugin_menu()
            for panel in self.panels.values():
                if hasattr(panel, 'CENTER_PANE') and panel.CENTER_PANE:
                    for name in self._current_perspective.get_perspective():
                        if name == panel.window_name:
                            panel.on_set_focus(event=None)
                            break
                           
            name = self._current_perspective.sub_menu
            if self._data_panel is not None:
                self._data_panel.set_active_perspective(name)
                self._check_applications_menu()
  
    def _check_applications_menu(self):
        """
        check the menu of the current application
        """
        if self._applications_menu is not None:
            for menu in self._applications_menu.GetMenuItems():
                if self._current_perspective is not None:
                    name = self._current_perspective.sub_menu
                    if menu.IsCheckable():
                        if menu.GetLabel() == name:
                            menu.Check(True)
                        else:
                             menu.Check(False) 
           
    def set_plotpanel_floating(self, event=None):
        """
        make the plot panel floatable
        """
        self.__gui_style &= (~GUIFRAME.FIXED_PANEL)
        self.__gui_style |= GUIFRAME.FLOATING_PANEL
        for p in self.panels.values():
            plot_panel = self._plotting_plugin.plot_panels
            for p in self.panels.values():
                if p in plot_panel:
                    self._popup_floating_panel(p)
        
    def set_plotpanel_fixed(self, event=None):
        """
        make the plot panel fixed
        """
        self.__gui_style &= (~GUIFRAME.FLOATING_PANEL)
        self.__gui_style |= GUIFRAME.FIXED_PANEL
        plot_panel = []
        if self._plotting_plugin is not None:
            plot_panel = self._plotting_plugin.plot_panels
            for p in self.panels.values():
                if p in plot_panel:
                    self._popup_fixed_panel(p)
                    
    def _popup_fixed_panel(self, p):
        """
        """
        style = self.__gui_style & GUIFRAME.FIXED_PANEL
        if style == GUIFRAME.FIXED_PANEL:
            self._mgr.GetPane(p.window_name).Floatable()
            self._mgr.GetPane(p.window_name).Right()
            self._mgr.GetPane(p.window_name).TopDockable(False)
            self._mgr.GetPane(p.window_name).BottomDockable(False)
            self._mgr.GetPane(p.window_name).LeftDockable(False)
            self._mgr.GetPane(p.window_name).RightDockable(True)
            flag = self._mgr.GetPane(p.window_name).IsShown()
            self._mgr.GetPane(p.window_name).Show(flag)
            self._mgr.Update()
            
    def _popup_floating_panel(self, p):
        """
        """
        style = self.__gui_style &  GUIFRAME.FLOATING_PANEL
        if style == GUIFRAME.FLOATING_PANEL: 
            self._mgr.GetPane(p.window_name).Floatable(True)
            self._mgr.GetPane(p.window_name).Float()
            self._mgr.GetPane(p.window_name).Dockable(False)
            flag = self._mgr.GetPane(p.window_name).IsShown()
            self._mgr.GetPane(p.window_name).Show(flag)
            self._mgr.Update()
            
    def enable_add_data(self, new_plot):
        """
        Enable append data on a plot panel
        """
        is_theory = len(self.panel_on_focus.plots) <= 1 and \
            self.panel_on_focus.plots.values()[0].__class__.__name__ == "Theory1D"
            
        is_data2d = hasattr(new_plot, 'data')
        is_data1d = self.panel_on_focus.__class__.__name__ == "ModelPanel1D"\
            and self.panel_on_focus.group_id is not None
        has_meta_data = hasattr(new_plot, 'meta_data')
        
        #disable_add_data if the data is being recovered from  a saved state file.
        is_state_data = False
        if has_meta_data:
            if 'invstate' in new_plot.meta_data: is_state_data = True
            if  'prstate' in new_plot.meta_data: is_state_data = True
            if  'fitstate' in new_plot.meta_data: is_state_data = True
    
        return is_data1d and not is_data2d and not is_theory and not is_state_data
    
    def enable_edit_menu(self):
        """
        enable menu item under edit menu depending on the panel on focus
        """
        if self.panel_on_focus is not None and self._edit_menu is not None:
            flag = self.panel_on_focus.get_undo_flag()
            self._edit_menu.Enable(GUIFRAME_ID.UNDO_ID, flag)
            flag = self.panel_on_focus.get_redo_flag()
            self._edit_menu.Enable(GUIFRAME_ID.REDO_ID, flag)
            #flag = self.panel_on_focus.get_bookmark_flag()
            #self._edit_menu.Enable(GUIFRAME_ID.BOOKMARK_ID, flag)
            flag = self.panel_on_focus.get_save_flag()
            self._edit_menu.Enable(GUIFRAME_ID.SAVE_ID, flag)
            flag = self.panel_on_focus.get_print_flag()
            self._edit_menu.Enable(GUIFRAME_ID.PRINT_ID, flag)
            flag = self.panel_on_focus.get_preview_flag()
            self._edit_menu.Enable(GUIFRAME_ID.PREVIEW_ID, flag)
            flag = self.panel_on_focus.get_zoom_flag()
            self._edit_menu.Enable(GUIFRAME_ID.ZOOM_ID, flag)
            flag = self.panel_on_focus.get_zoom_in_flag()
            self._edit_menu.Enable(GUIFRAME_ID.ZOOM_IN_ID, flag)
            flag = self.panel_on_focus.get_zoom_out_flag()
            self._edit_menu.Enable(GUIFRAME_ID.ZOOM_OUT_ID, flag)
            flag = self.panel_on_focus.get_drag_flag()
            self._edit_menu.Enable(GUIFRAME_ID.DRAG_ID, flag)
            flag = self.panel_on_focus.get_reset_flag()
            self._edit_menu.Enable(GUIFRAME_ID.RESET_ID, flag)
        else:
            flag = False
            self._edit_menu.Enable(GUIFRAME_ID.UNDO_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.REDO_ID, flag)
            #self._edit_menu.Enable(GUIFRAME_ID.BOOKMARK_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.SAVE_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.PRINT_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.PREVIEW_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.ZOOM_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.ZOOM_IN_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.ZOOM_OUT_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.DRAG_ID, flag)
            self._edit_menu.Enable(GUIFRAME_ID.RESET_ID, flag)
            
    def on_undo_panel(self, event=None):
        """
        undo previous action of the last panel on focus if possible
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_undo(event)
            
    def on_redo_panel(self, event=None):
        """
        redo the last cancel action done on the last panel on focus
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_redo(event)
            
    def on_bookmark_panel(self, event=None):
        """
        bookmark panel
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_bookmark(event)
            
    def append_bookmark(self, event=None):
        """
        Bookmark available information of the panel on focus
        """
        self._toolbar.append_bookmark(event)
            
    def on_save_panel(self, event=None):
        """
        save possible information on the current panel
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_save(event)
            
    def on_preview_panel(self, event=None):
        """
        preview information on the panel on focus
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_preview(event)
            
    def on_print_panel(self, event=None):
        """
        print available information on the last panel on focus
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_print(event)
            
    def on_zoom_panel(self, event=None):
        """
        zoom on the current panel if possible
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_zoom(event)
            
    def on_zoom_in_panel(self, event=None):
        """
        zoom in of the panel on focus
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_zoom_in(event)
            
    def on_zoom_out_panel(self, event=None):
        """
        zoom out on the panel on focus
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_zoom_out(event)
            
    def on_drag_panel(self, event=None):
        """
        drag apply to the panel on focus
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_drag(event)
            
    def on_reset_panel(self, event=None):
        """
        reset the current panel
        """
        if self.panel_on_focus is not None:
            self.panel_on_focus.on_reset(event)
            
    def enable_undo(self):
        """
        enable undo related control
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_undo(self.panel_on_focus)
            
    def enable_redo(self):
        """
        enable redo 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_redo(self.panel_on_focus)
            
    def enable_bookmark(self):
        """
        Bookmark 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_bookmark(self.panel_on_focus)
            
    def enable_save(self):
        """
        save 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_save(self.panel_on_focus)
            
    def enable_preview(self):
        """
        preview 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_preview(self.panel_on_focus)
            
    def enable_print(self):
        """
        print 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_print(self.panel_on_focus)
            
    def enable_zoom(self):
        """
        zoom 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_zoom(self.panel_on_focus)
            
    def enable_zoom_in(self):
        """
        zoom in 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_zoom_in(self.panel_on_focus)
            
    def enable_zoom_out(self):
        """
        zoom out 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_zoom_out(self.panel_on_focus)
            
    def enable_drag(self, event=None):
        """
        drag 
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_drag(self.panel_on_focus)
            
    def enable_reset(self):
        """
        reset the current panel
        """
        if self.panel_on_focus is not None:
            self._toolbar.enable_reset(self.panel_on_focus)
        
class DefaultPanel(wx.Panel, PanelBase):
    """
    Defines the API for a panels to work with
    the GUI manager
    """
    ## Internal nickname for the window, used by the AUI manager
    window_name = "default"
    ## Name to appear on the window title bar
    window_caption = "Welcome panel"
    ## Flag to tell the AUI manager to put this panel in the center pane
    CENTER_PANE = True
    def __init__(self, parent, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)
        PanelBase.__init__(self, parent)
    


# Toy application to test this Frame
class ViewApp(wx.App):
    """
    """
    SIZE = (GUIFRAME_WIDTH,GUIFRAME_HEIGHT)
    TITLE = config.__appname__
    PROG_SPLASH_PATH = PROG_SPLASH_SCREEN
    STYLE = GUIFRAME.SINGLE_APPLICATION
    def OnInit(self):
        """
        """
        pos, size = self.window_placement(self.SIZE)
        self.frame = ViewerFrame(parent=None, 
                                 title=self.TITLE, 
                                 pos=pos, 
                                 gui_style = self.STYLE,
                                 size=size) 
         # Display a splash screen on top of the frame.
        if len(sys.argv) > 1 and '--time' in sys.argv[1:]:
            log_time("Starting to display the splash screen")
        if self.PROG_SPLASH_PATH is not None and \
            os.path.isfile(self.PROG_SPLASH_PATH):
            try:
                self.display_splash_screen(parent=self.frame, path=self.PROG_SPLASH_PATH)   
            except:
                msg = "Cannot display splash screen\n"
                msg += str (sys.exc_value)
                logging.error(msg)
        self.frame.Show(True)

        if hasattr(self.frame, 'special'):
            self.frame.special.SetCurrent()
        self.SetTopWindow(self.frame)
        return True
    
    def set_manager(self, manager):
        """
        Sets a reference to the application manager
        of the GUI manager (Frame) 
        """
        self.frame.set_manager(manager)
        
    def build_gui(self):
        """
        Build the GUI
        """
        self.frame.build_gui()
        self.frame.post_init()
        
    def set_welcome_panel(self, panel_class):
        """
        Set the welcome panel
        
        :param panel_class: class of the welcome panel to be instantiated
        
        """
        self.frame.set_welcome_panel(panel_class)
        
    def add_perspective(self, perspective):
        """
        Manually add a perspective to the application GUI
        """
        self.frame.add_perspective(perspective)
    
    def window_placement(self, size):
        """
        Determines the position and size of the application frame such that it
        fits on the user's screen without obstructing (or being obstructed by)
        the Windows task bar.  The maximum initial size in pixels is bounded by
        WIDTH x HEIGHT.  For most monitors, the application
        will be centered on the screen; for very large monitors it will be
        placed on the left side of the screen.
        """
        window_width, window_height = size
        screen_size = wx.GetDisplaySize()
        window_height = window_height if screen_size[1]>window_height else screen_size[1]-50
        window_width  = window_width if screen_size[0]> window_width else screen_size[0]-50
        xpos = ypos = 0

        # Note that when running Linux and using an Xming (X11) server on a PC
        # with a dual  monitor configuration, the reported display size may be
        # that of both monitors combined with an incorrect display count of 1.
        # To avoid displaying this app across both monitors, we check for
        # screen 'too big'.  If so, we assume a smaller width which means the
        # application will be placed towards the left hand side of the screen.

        _, _, x, y = wx.Display().GetClientArea() # size excludes task bar
        if len(sys.argv) > 1 and '--platform' in sys.argv[1:]:
            w, h = wx.DisplaySize()  # size includes task bar area
        if x > 1920: x = 1280  # display on left side, not centered on screen
        if x > window_width:  xpos = (x - window_width)/2
        if y > window_height: ypos = (y - window_height)/2

        # Return the suggested position and size for the application frame.
        return (xpos, ypos), (min(x, window_width), min(y, window_height))
    
    def display_splash_screen(self, parent, path=PROG_SPLASH_SCREEN):
        """Displays the splash screen.  It will exactly cover the main frame."""

        # Prepare the picture.  On a 2GHz intel cpu, this takes about a second.
        x, y = parent.GetSizeTuple()
        image = wx.Image(path, wx.BITMAP_TYPE_PNG)
        image.Rescale(x, y, wx.IMAGE_QUALITY_HIGH)
        bm = image.ConvertToBitmap()

        # Create and show the splash screen.  It will disappear only when the
        # program has entered the event loop AND either the timeout has expired
        # or the user has left clicked on the screen.  Thus any processing
        # performed in this routine (including sleeping) or processing in the
        # calling routine (including doing imports) will prevent the splash
        # screen from disappearing.
        #
        # Note that on Linux, the timeout appears to occur immediately in which
        # case the splash screen disappears upon entering the event loop.
        wx.SplashScreen(bitmap=bm,
                        splashStyle=(wx.SPLASH_CENTRE_ON_PARENT|
                                     wx.SPLASH_TIMEOUT|
                                     wx.STAY_ON_TOP),
                        milliseconds=4000,
                        parent=parent,
                        id=wx.ID_ANY)

        # Keep the splash screen up a minimum amount of time for non-Windows
        # systems.  This is a workaround for Linux and possibly MacOS that
        # appear to ignore the splash screen timeout option.
        if '__WXMSW__' not in wx.PlatformInfo:
            if len(sys.argv) > 1 and '--time' in sys.argv[1:]:
                log_time("Starting sleep of 2 secs")
            time.sleep(2)

        # A call to wx.Yield does not appear to be required.  If used on
        # Windows, the cursor changes from 'busy' to 'ready' before the event
        # loop is reached which is not desirable.  On Linux it seems to have
        # no effect.
        #wx.Yield()

        

if __name__ == "__main__": 
    app = ViewApp(0)
    app.MainLoop()

             