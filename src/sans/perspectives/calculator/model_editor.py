################################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation. 
#
#See the license text in license.txt
#
#copyright 2009, University of Tennessee
################################################################################
import wx
import sys
import os
import math
from wx.py.editwindow import EditWindow

if sys.platform.count("win32") > 0:
    FONT_VARIANT = 0
    PNL_WIDTH = 450
    PNL_HITE = 320
else:
    FONT_VARIANT = 1
    PNL_WIDTH = 590
    PNL_HITE = 350
M_NAME = 'Model'
EDITOR_WIDTH = 800
EDITOR_HEIGTH = 735
PANEL_WIDTH = 500
_BOX_WIDTH = 55

    
def _compileFile(path):
    """
    Compile the file in the path
    """
    try:
        import py_compile
        py_compile.compile(file=path, doraise=True)
        return ''
    except:
        _, value, _ = sys.exc_info()
        return value
    
def _deleteFile(path):
    """
    Delete file in the path
    """
    try:
        os.remove(path)
    except:
        raise

 
class TextDialog(wx.Dialog):
    """
    Dialog for easy custom sum models  
    """
    def __init__(self, parent=None, base=None, id=None, title='', 
                 model_list=[], plugin_dir=None):
        """
        Dialog window popup when selecting 'Easy Custom Sum/Multiply' 
        on the menu
        """
        wx.Dialog.__init__(self, parent=parent, id=id, 
                           title=title, size=(PNL_WIDTH, PNL_HITE))
        self.parent = base
        #Font
        self.SetWindowVariant(variant=FONT_VARIANT)
        # default
        self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        self.font.SetPointSize(10)
        self.overwrite_name = False
        self.plugin_dir = plugin_dir
        self.model_list = model_list
        self.model1_string = "SphereModel"
        self.model2_string = "CylinderModel"
        self.name = 'Sum' + M_NAME
        self.factor = 'scale_factor'
        self._notes = ''
        self.operator = '+'
        self.operator_cbox = None
        self.explanation = ''
        self.explanationctr = None
        self.sizer = None
        self.name_sizer = None
        self.name_hsizer = None
        self.desc_sizer = None
        self.desc_tcl = None
        self.model1 = None
        self.model2 = None
        self.static_line_1 = None
        self.okButton = None
        self.closeButton = None
        self._msg_box = None
        self.msg_sizer = None
        self.fname = None
        self.cm_list = None
        self.is_p1_custom = False
        self.is_p2_custom = False
        self._build_sizer()
        self.model1_name = str(self.model1.GetValue())
        self.model2_name = str(self.model2.GetValue())
        self.good_name = True
        self.fill_oprator_combox()
        
    def _layout_name(self):
        """
        Do the layout for file/function name related widgets
        """
        self.name_sizer = wx.BoxSizer(wx.VERTICAL)
        self.name_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        #title name [string]
        name_txt = wx.StaticText(self, -1, 'Function Name : ')  
        self.name_tcl = wx.TextCtrl(self, -1, size=(PANEL_WIDTH*3/5, -1)) 
        self.name_tcl.Bind(wx.EVT_TEXT_ENTER, self.on_change_name)
        self.name_tcl.SetValue('')
        self.name_tcl.SetFont(self.font)
        hint_name = "Unique Sum/Multiply Model Function Name."
        self.name_tcl.SetToolTipString(hint_name)
        self.name_hsizer.AddMany([(name_txt, 0, wx.LEFT|wx.TOP, 10),
                            (self.name_tcl, -1, 
                             wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, 10)])
        self.name_sizer.AddMany([(self.name_hsizer, -1, 
                                        wx.LEFT|wx.TOP, 10)])
        
        
    def _layout_description(self):
        """
        Do the layout for description related widgets
        """
        self.desc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #title name [string]
        desc_txt = wx.StaticText(self, -1, 'Description (optional) : ')  
        self.desc_tcl = wx.TextCtrl(self, -1, size=(PANEL_WIDTH*3/5, -1)) 
        self.desc_tcl.SetValue('')
        #self.name_tcl.SetFont(self.font)
        hint_desc = "Write a short description of this model function."
        self.desc_tcl.SetToolTipString(hint_desc)
        self.desc_sizer.AddMany([(desc_txt, 0, wx.LEFT|wx.TOP, 10),
                                (self.desc_tcl, -1, 
                                wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, 10)])     
  
    def _build_sizer(self):
        """
        Build gui
        """
        box_width = 195 # combobox width
        vbox  = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.GridBagSizer(1, 3)
        self._layout_name()
        self._layout_description()
        
        
        sum_description = wx.StaticBox(self, -1, 'Select', 
                                       size=(PNL_WIDTH-30, 70))
        sum_box = wx.StaticBoxSizer(sum_description, wx.VERTICAL)
        model1_box = wx.BoxSizer(wx.HORIZONTAL)
        model2_box = wx.BoxSizer(wx.HORIZONTAL)
        model_vbox = wx.BoxSizer(wx.VERTICAL)
        self.model1 =  wx.ComboBox(self, -1, style=wx.CB_READONLY)
        wx.EVT_COMBOBOX(self.model1, -1, self.on_model1)
        self.model1.SetMinSize((box_width*5/6, -1))
        self.model1.SetToolTipString("model1")
        
        self.operator_cbox = wx.ComboBox(self, -1, size=(50, -1), 
                                         style=wx.CB_READONLY)
        wx.EVT_COMBOBOX(self.operator_cbox, -1, self.on_select_operator)
        operation_tip = "Add: +, Multiply: * "
        self.operator_cbox.SetToolTipString(operation_tip)
        
        self.model2 =  wx.ComboBox(self, -1, style=wx.CB_READONLY)
        wx.EVT_COMBOBOX(self.model2, -1, self.on_model2)
        self.model2.SetMinSize((box_width*5/6, -1))
        self.model2.SetToolTipString("model2")
        self._set_model_list()
        
         # Buttons on the bottom
        self.static_line_1 = wx.StaticLine(self, -1)
        self.okButton = wx.Button(self,wx.ID_OK, 'Apply', size=(box_width/2, 25))
        self.okButton.Bind(wx.EVT_BUTTON, self.check_name)
        self.closeButton = wx.Button(self,wx.ID_CANCEL, 'Close', 
                                     size=(box_width/2, 25))
        # Intro
        self.explanation  = "  custom model = %s %s "% (self.factor, '*')
        self.explanation  += "(model1 %s model2)\n"% self.operator
        #explanation  += "  Note: This will overwrite the previous sum model.\n"
        model_string = " Model%s (p%s):"
        # msg
        self._msg_box = wx.StaticText(self, -1, self._notes)
        self.msg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.msg_sizer.Add(self._msg_box, 0, wx.LEFT, 0)
        vbox.Add(self.name_hsizer)
        vbox.Add(self.desc_sizer)
        vbox.Add(self.sizer)
        ix = 0
        iy = 1
        self.explanationctr = wx.StaticText(self, -1, self.explanation)
        self.sizer.Add(self.explanationctr , (iy, ix),
                 (1, 1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        model1_box.Add(wx.StaticText(self, -1, model_string% (1, 1)), -1, 0)
        model1_box.Add((box_width-15, 10))
        model1_box.Add(wx.StaticText(self, -1, model_string% (2, 2)), -1, 0)
        model2_box.Add(self.model1, -1, 0)
        model2_box.Add((15, 10))
        model2_box.Add(self.operator_cbox, 0, 0)
        model2_box.Add((15, 10))
        model2_box.Add(self.model2, -1, 0)
        model_vbox.Add(model1_box, -1, 0)
        model_vbox.Add(model2_box, -1, 0)
        sum_box.Add(model_vbox, -1, 10)
        iy += 1
        ix = 0
        self.sizer.Add(sum_box, (iy, ix),
                  (1, 1), wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 15)
        vbox.Add((10, 10))
        vbox.Add(self.static_line_1, 0, wx.EXPAND, 10)
        vbox.Add(self.msg_sizer, 0, 
                 wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE|wx.BOTTOM, 10)
        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer_button.Add((20, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_button.Add(self.okButton, 0, 
                         wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_button.Add(self.closeButton, 0,
                          wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)        
        vbox.Add(sizer_button, 0, wx.EXPAND|wx.BOTTOM|wx.TOP, 10)
         
        self.SetSizer(vbox)
        self.Centre()
        
    def on_change_name(self, event=None):
        """
        Change name
        """
        if event is not None:
            event.Skip()
        self.name_tcl.SetBackgroundColour('white')
        self.Refresh()
    
    def check_name(self, event=None):
        """
        Check name if exist already
        """
        mname = M_NAME
        self.on_change_name(None)
        list_fnames = os.listdir(self.plugin_dir)
        # fake existing regular model name list
        m_list = [model + ".py" for model in self.model_list]
        list_fnames.append(m_list)
        # function/file name
        title = self.name_tcl.GetValue().lstrip().rstrip()
        if title == '':
            text = self.operator
            if text.count('+') > 0:
                mname = 'Sum'
            else:
                mname = 'Multi'
            mname += M_NAME
            title = mname
        self.name = title
        t_fname = title + '.py'
        if not self.overwrite_name:
            if t_fname in list_fnames and title != mname:
                self.name_tcl.SetBackgroundColour('pink')
                self.good_name = False
                info = 'Error'
                msg = "Name exists already."
                wx.MessageBox(msg, info)  
                self._notes = msg
                color = 'red'
                self._msg_box.SetLabel(msg)
                self._msg_box.SetForegroundColour(color)
                return self.good_name
        self.fname = os.path.join(self.plugin_dir, t_fname)
        s_title = title
        if len(title) > 20:
            s_title = title[0:19] + '...'
        self._notes = "Model function (%s) has been set! \n" % str(s_title)
        self.good_name = True
        self.on_apply(self.fname)
        return self.good_name
    
    def on_apply(self, path):
        """
        On Apply
        """
        try:
            label = self.getText()
            fname = path
            name1 = label[0]
            name2 = label[1]
            self.write_string(fname, name1, name2)
            self.compile_file(fname)
            self.parent.update_custom_combo()
            msg = self._notes
            info = 'Info'
            color = 'blue'
        except:
            msg= "Easy Custom Sum/Multipy: Error occurred..."
            info = 'Error'
            color = 'red'
        self._msg_box.SetLabel(msg)
        self._msg_box.SetForegroundColour(color)
        if self.parent.parent != None:
            from sans.guiframe.events import StatusEvent 
            wx.PostEvent(self.parent.parent, StatusEvent(status = msg, 
                                                      info=info))
        else:
            raise
                  
    def _set_model_list(self):
        """
        Set the list of models
        """
        # list of model names
        cm_list = []
        # models
        list = self.model_list
        # custom models
        al_list = os.listdir(self.plugin_dir)
        for c_name in al_list:
            if c_name.split('.')[-1] == 'py' and \
                    c_name.split('.')[0] != '__init__':
                name = str(c_name.split('.')[0])
                cm_list.append(name)
                if name not in list:
                    list.append(name)
        self.cm_list = cm_list
        if len(list) > 1:
            list.sort()
        for idx in range(len(list)):
            self.model1.Append(str(list[idx]), idx) 
            self.model2.Append(str(list[idx]), idx)
        self.model1.SetStringSelection(self.model1_string)
        self.model2.SetStringSelection(self.model2_string)
    
    def update_cm_list(self):
        """
        Update custom model list
        """
        cm_list = []
        al_list = os.listdir(self.plugin_dir)
        for c_name in al_list:
            if c_name.split('.')[-1] == 'py' and \
                    c_name.split('.')[0] != '__init__':
                name = str(c_name.split('.')[0])
                cm_list.append(name)
        self.cm_list = cm_list 
              
    def on_model1(self, event):
        """
        Set model1
        """
        event.Skip()
        self.update_cm_list()
        self.model1_name = str(self.model1.GetValue())
        self.model1_string = self.model1_name
        if self.model1_name in self.cm_list:
            self.is_p1_custom = True
        else:
            self.is_p1_custom = False
            
    def on_model2(self, event):
        """
        Set model2
        """
        event.Skip()
        self.update_cm_list()
        self.model2_name = str(self.model2.GetValue())
        self.model2_string = self.model2_name
        if self.model2_name in self.cm_list:
            self.is_p2_custom = True
        else:
            self.is_p2_custom = False
        
    def on_select_operator(self, event=None):
        """
        On Select an Operator
        """
        # For Mac
        if event != None:
            event.Skip()
        name = ''    
        item = event.GetEventObject()
        text = item.GetValue()
        if text.count('*') > 0:
            name = 'Multi'
            factor = 'BackGround'
            f_oper = '+'
        else:
            name = 'Sum'
            factor = 'scale_factor'
            f_oper = '*'

        self.factor = factor
        self.operator = text
        self.explanation = "  Custom Model = %s %s (model1 %s model2)\n"% \
                    (self.factor, f_oper, self.operator)
        self.explanationctr.SetLabel(self.explanation)
        self.name = name + M_NAME 
        self.sizer.Layout()
             
    def fill_oprator_combox(self):
        """
        fill the current combobox with the operator
        """   
        operator_list = [' +', ' *']
        for oper in operator_list:
            pos = self.operator_cbox.Append(str(oper))
            self.operator_cbox.SetClientData(pos, str(oper.strip()))
        self.operator_cbox.SetSelection(0)
            
    def getText(self):
        """
        Returns model name string as list
        """
        return [self.model1_name, self.model2_name]
    
    def write_string(self, fname, name1, name2):
        """
        Write and Save file
        """
        self.fname = fname  
        description = self.desc_tcl.GetValue().lstrip().rstrip()
        if description == '':
            description = name1 + self.operator + name2
        name = self.name_tcl.GetValue().lstrip().rstrip()
        text = self.operator_cbox.GetValue()
        if text.count('+') > 0:
            factor = 'scale_factor'
            f_oper = '*'
            default_val = '1.0'
        else:
            factor = 'BackGround'
            f_oper = '+'
            default_val = '0.0'
        path = self.fname
        try:
            out_f =  open(path,'w')
        except :
            raise
        lines = SUM_TEMPLATE.split('\n')
        for line in lines:
            try:
                if line.count("scale_factor"):
                    line = line.replace('scale_factor', factor)
                    #print "scale_factor", line
                if line.count("= %s"):
                    out_f.write(line % (default_val) + "\n")
                elif line.count("import Model as P1"):
                    if self.is_p1_custom:
                        line = line.replace('#', '')
                        out_f.write(line % name1 + "\n")
                    else:
                        out_f.write(line + "\n")
                elif line.count("import %s as P1"):
                    if not self.is_p1_custom:
                        line = line.replace('#', '')
                        out_f.write(line % (name1, name1) + "\n")
                    else:
                        out_f.write(line + "\n")
                elif line.count("import Model as P2"):
                    if self.is_p2_custom:
                        line = line.replace('#', '')
                        out_f.write(line % name2 + "\n")
                    else:
                        out_f.write(line + "\n")
                elif line.count("import %s as P2"):
                    if not self.is_p2_custom:
                        line = line.replace('#', '')
                        out_f.write(line % (name2, name2) + "\n")
                    else:
                        out_f.write(line + "\n")
                elif line.count("self.description = '%s'"):
                    out_f.write(line % description + "\n")
                #elif line.count("run") and line.count("%s"):
                #    out_f.write(line % self.operator + "\n")
                #elif line.count("evalDistribution") and line.count("%s"):
                #    out_f.write(line % self.operator + "\n")
                elif line.count("return") and line.count("%s") == 2:
                    #print "line return", line
                    out_f.write(line % (f_oper, self.operator) + "\n")
                elif line.count("out2")and line.count("%s"):
                    out_f.write(line % self.operator + "\n")
                else:
                    out_f.write(line + "\n")
            except:
                raise
        out_f.close()
        #else:
        #    msg = "Name exists already."
        
    def compile_file(self, path):
        """
        Compile the file in the path
        """
        path = self.fname
        _compileFile(path)
        
    def delete_file(self, path):
        """
        Delete file in the path
        """
        _deleteFile(path)


class EditorPanel(wx.ScrolledWindow):
    """
    Custom model function editor
    """
    def __init__(self, parent, base, path, title, *args, **kwds):
        kwds['name'] = title
        kwds["size"] = (EDITOR_WIDTH, EDITOR_HEIGTH)
        kwds["style"] = wx.FULL_REPAINT_ON_RESIZE
        wx.ScrolledWindow.__init__(self, parent, *args, **kwds)
        #self.SetupScrolling()
        self.parent = parent
        self.base = base
        self.path = path
        self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        self.font.SetPointSize(10)
        self.reader = None
        self.name = 'untitled'
        self.overwrite_name = False
        self.is_2d = False
        self.fname = None
        self.param_strings = ''
        self.function_strings = ''
        self._notes = ""
        self._msg_box = None
        self.msg_sizer = None
        self.warning = ""
        self._description = "New Custom Model"
        self.function_tcl = None
        #self._default_save_location = os.getcwd()
        self._do_layout()
        #self.bt_apply.Disable()

             
    def _define_structure(self):
        """
        define initial sizer 
        """
        #w, h = self.parent.GetSize()
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.name_sizer = wx.BoxSizer(wx.VERTICAL)
        self.name_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.desc_sizer = wx.BoxSizer(wx.VERTICAL)
        self.param_sizer = wx.BoxSizer(wx.VERTICAL)
        self.function_sizer = wx.BoxSizer(wx.VERTICAL)
        self.func_horizon_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.msg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
    def _layout_name(self):
        """
        Do the layout for file/function name related widgets
        """
        #title name [string]
        name_txt = wx.StaticText(self, -1, 'Function Name : ')  
        overwrite_cb = wx.CheckBox(self, -1, "Overwrite?", (10, 10))
        overwrite_cb.SetValue(False)
        overwrite_cb.SetToolTipString("Overwrite it if already exists?")
        wx.EVT_CHECKBOX(self, overwrite_cb.GetId(), self.on_over_cb)
        #overwrite_cb.Show(False)
        self.name_tcl = wx.TextCtrl(self, -1, size=(PANEL_WIDTH*3/5, -1)) 
        self.name_tcl.Bind(wx.EVT_TEXT_ENTER, self.on_change_name)
        self.name_tcl.SetValue('MyFunction')
        self.name_tcl.SetFont(self.font)
        hint_name = "Unique Model Function Name."
        self.name_tcl.SetToolTipString(hint_name)
        self.name_hsizer.AddMany([(self.name_tcl, 0, wx.LEFT|wx.TOP, 0),
                                       (overwrite_cb, 0, wx.LEFT, 20)])
        self.name_sizer.AddMany([(name_txt, 0, wx.LEFT|wx.TOP, 10),
                                       (self.name_hsizer, 0, 
                                        wx.LEFT|wx.TOP|wx.BOTTOM, 10)])
        
        
    def _layout_description(self):
        """
        Do the layout for description related widgets
        """
        #title name [string]
        desc_txt = wx.StaticText(self, -1, 'Description (optional) : ')  
        self.desc_tcl = wx.TextCtrl(self, -1, size=(PANEL_WIDTH*3/5, -1)) 
        self.desc_tcl.SetValue('')
        #self.name_tcl.SetFont(self.font)
        hint_desc = "Write a short description of the model function."
        self.desc_tcl.SetToolTipString(hint_desc)
        self.desc_sizer.AddMany([(desc_txt, 0, wx.LEFT|wx.TOP, 10),
                                       (self.desc_tcl, 0, 
                                        wx.LEFT|wx.TOP|wx.BOTTOM, 10)])     
    def _layout_param(self):
        """
        Do the layout for parameter related widgets
        """
        param_txt = wx.StaticText(self, -1, 'Fit Parameters (if any): ') 
        
        param_tip = "#Set the parameters and initial values.\n"
        param_tip += "#Example:\n"
        param_tip += "A = 1\nB = 1"
        #param_txt.SetToolTipString(param_tip)
        id  = wx.NewId() 
        self.param_tcl = EditWindow(self, id, wx.DefaultPosition, 
                            wx.DefaultSize, wx.CLIP_CHILDREN|wx.SUNKEN_BORDER)
        self.param_tcl.setDisplayLineNumbers(True)
        self.param_tcl.SetToolTipString(param_tip)

        self.param_sizer.AddMany([(param_txt, 0, wx.LEFT, 10),
                        (self.param_tcl, 1, wx.EXPAND|wx.ALL, 10)])
                
    def _layout_function(self):
        """
        Do the layout for function related widgets
        """
        function_txt = wx.StaticText(self, -1, 'Function(x) : ') 
        hint_function = "#Example:\n"
        hint_function += "if x <= 0:\n"
        hint_function += "    y = A + B\n"
        hint_function += "else:\n"
        hint_function += "    y = A + B * cos(2 * pi * x)\n"
        hint_function += "return y\n"
        math_txt = wx.StaticText(self, -1, '*Useful math functions: ')
        math_combo = self._fill_math_combo()
        
        id  = wx.NewId() 
        self.function_tcl = EditWindow(self, id, wx.DefaultPosition, 
                            wx.DefaultSize, wx.CLIP_CHILDREN|wx.SUNKEN_BORDER)
        self.function_tcl.setDisplayLineNumbers(True)
        self.function_tcl.SetToolTipString(hint_function)
        
        self.func_horizon_sizer.Add(function_txt)
        self.func_horizon_sizer.Add(math_txt, 0, wx.LEFT, 250)
        self.func_horizon_sizer.Add(math_combo, 0, wx.LEFT, 10)

        self.function_sizer.Add(self.func_horizon_sizer, 0, wx.LEFT, 10)
        self.function_sizer.Add( self.function_tcl, 1, wx.EXPAND|wx.ALL, 10)
        
    def _layout_msg(self):
        """
        Layout msg
        """
        self._msg_box = wx.StaticText(self, -1, self._notes, 
                                      size=(PANEL_WIDTH, -1))
        self.msg_sizer.Add(self._msg_box, 0, wx.LEFT, 10)  
                    
    def _layout_button(self):  
        """
        Do the layout for the button widgets
        """         
        self.bt_apply = wx.Button(self, -1, "Apply", size=(_BOX_WIDTH, -1))
        self.bt_apply.SetToolTipString("Save changes into the imported data.")
        self.bt_apply.Bind(wx.EVT_BUTTON, self.on_click_apply)
        
        self.bt_close = wx.Button(self, -1, 'Close', size=(_BOX_WIDTH, -1))
        self.bt_close.Bind(wx.EVT_BUTTON, self.on_close)
        self.bt_close.SetToolTipString("Close this panel.")
        
        self.button_sizer.AddMany([(self.bt_apply, 0, 
                                    wx.LEFT, EDITOR_WIDTH * 0.8),
                                   (self.bt_close, 0, 
                                    wx.LEFT|wx.BOTTOM, 15)])
          
    def _do_layout(self):
        """
        Draw the current panel
        """
        self._define_structure()
        self._layout_name()
        self._layout_description()
        self._layout_param()
        self._layout_function()
        self._layout_msg()
        self._layout_button()
        self.main_sizer.AddMany([(self.name_sizer, 0,  
                                        wx.EXPAND|wx.ALL, 5),
                                 (wx.StaticLine(self), 0, 
                                       wx.ALL|wx.EXPAND, 5),
                                 (self.desc_sizer, 0,  
                                        wx.EXPAND|wx.ALL, 5),
                                 (wx.StaticLine(self), 0, 
                                       wx.ALL|wx.EXPAND, 5),
                                (self.param_sizer, 1,
                                         wx.EXPAND|wx.ALL, 5),
                                 (wx.StaticLine(self), 0, 
                                       wx.ALL|wx.EXPAND, 5),
                                (self.function_sizer, 2,
                                         wx.EXPAND|wx.ALL, 5),
                                 (wx.StaticLine(self), 0, 
                                       wx.ALL|wx.EXPAND, 5),
                                 (self.msg_sizer, 0, 
                                        wx.EXPAND|wx.ALL, 5),
                                (self.button_sizer, 0,
                                         wx.EXPAND|wx.ALL, 5)])
        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)

    def _fill_math_combo(self):
        """
        Fill up the math combo box
        """
        self.math_combo = wx.ComboBox(self, -1, size=(100, -1), 
                                      style=wx.CB_READONLY) 
        for item in dir(math):
            if item.count("_") < 1:
                try:
                    exec "float(math.%s)"% item
                    self.math_combo.Append(str(item))
                except:
                    self.math_combo.Append(str(item) + "()" )
        self.math_combo.Bind(wx.EVT_COMBOBOX, self._on_math_select)
        self.math_combo.SetSelection(0)
        return self.math_combo
        
    def _on_math_select(self, event):
        """
        On math selection on ComboBox
        """
        event.Skip()
        label = self.math_combo.GetLabel() 
        self.function_tcl.SetFocus()
        # Put the text at the cursor position
        pos = self.function_tcl.GetCurrentPos()
        self.function_tcl.InsertText(pos, label)  
        # Put the cursor at appropriate postion
        length = len(label)
        if label[-1] == ')':
            length -= 1
        f_pos = pos + length
        self.function_tcl.GotoPos(f_pos)   

    def get_notes(self):
        """
        return notes
        """
        return self._notes
                 
    def on_change_name(self, event=None):
        """
        Change name
        """
        if event is not None:
            event.Skip()
        self.name_tcl.SetBackgroundColour('white')
        self.Refresh()
    
    def check_name(self):
        """
        Check name if exist already
        """
        self._notes = ''
        self.on_change_name(None)
        plugin_dir = self.path
        list_fnames = os.listdir(plugin_dir)
        # function/file name
        title = self.name_tcl.GetValue().lstrip().rstrip()
        self.name = title
        t_fname = title + '.py'
        if not self.overwrite_name:
            if t_fname in list_fnames:
                self.name_tcl.SetBackgroundColour('pink')
                return False
        self.fname = os.path.join(plugin_dir, t_fname)
        s_title = title
        if len(title) > 20:
            s_title = title[0:19] + '...'
        self._notes += "Model function name is set "
        self._notes += "to %s. \n" % str(s_title)
        return True
    
    def on_over_cb(self, event):
        """
        Set overwrite name flag on cb event
        """
        if event is not None:
            event.Skip()
        cb = event.GetEventObject()
        self.overwrite_name = cb.GetValue()
        
    def on_click_apply(self, event):
        """   
        Changes are saved in data object imported to edit
        """
        #must post event here
        event.Skip()
        info = 'Info'
        msg = ''
        # Sort out the errors if occur
        if self.check_name():
            name = self.name_tcl.GetValue().lstrip().rstrip()
            description = self.desc_tcl.GetValue()
            param_str = self.param_tcl.GetText()
            func_str = self.function_tcl.GetText()
            # No input for the model function
            if func_str.lstrip().rstrip():     
                if func_str.count('return') > 0:
                    self.write_file(self.fname, description, param_str, 
                                                                    func_str)
                    tr_msg = _compileFile(self.fname)
                    msg = str(tr_msg.__str__())
                    # Compile error
                    if msg:
                        msg.replace("  ", "\n")
                        msg +=  "\nCompiling Failed"
                else:
                    msg = "Error: The func(x) must 'return' a value at least.\n"
                    msg += "For example: \n\nreturn 2*x"
            else:
                msg = 'Error: Function is not defined.'
        else:
            msg = "Name exists already."
        # Prepare for the messagebox
        if self.base != None and not msg:
            self.base.update_custom_combo()
            Model  = None
            exec "from %s import Model"% name 
            try:
                Model().run(0.01) 
            except:
                msg = "Error "
                _, value, _ = sys.exc_info()
                msg += "in %s:\n%s\n" % (name,  value)
        if msg:
            info = 'Error'
            color = 'red' 
            try:
                # try to remove pyc file if exists
                _deleteFile(self.fname)
                _deleteFile(self.fname + "c")
            except:
                pass
        else:
            msg = "Successful! "
            msg += "  " + self._notes
            msg += " Please look for it in the Customized Models."
            info = 'Info'
            color = 'blue'
        # Not to display long error msg
        if info == 'Error':
            mss = info
        else:
            mss = msg
        self._msg_box.SetLabel(mss)
        self._msg_box.SetForegroundColour(color)
        # Send msg to the top window  
        if self.base != None:
                from sans.guiframe.events import StatusEvent 
                wx.PostEvent(self.base.parent, StatusEvent(status = msg, 
                                                      info=info))
        self.warning = msg

                
    def write_file(self, fname, desc_str, param_str, func_str):  
        """
        Write content in file
        
        :param fname: full file path
        :param desc_str: content of the description strings
        :param param_str: content of params; Strings  
        :param func_str: content of func; Strings
        """ 
        try:
            out_f =  open(fname,'w')
        except :
            raise
        # Prepare the content of the function
        lines = CUSTOM_TEMPLATE.split('\n')

        has_scipy = func_str.count("scipy.")
        self.is_2d = func_str.count("#self.ndim = 2")
        line_2d = ''
        if self.is_2d:
            line_2d = CUSTOM_2D_TEMP.split('\n')
        line_test = TEST_TEMPLATE.split('\n')
        local_params = ''
        spaces = '        '#8spaces
        # write function here
        for line in lines:
            # The location where to put the strings is 
            # hard-coded in the template as shown below.
            if line.count("#self.params here"):
                for param_line in param_str.split('\n'):
                    p_line = param_line.lstrip().rstrip()
                    if p_line:
                        p0_line = self.set_param_helper(p_line)
                        local_params += self.set_function_helper(p_line)
                        out_f.write(p0_line)
            elif line.count("#local params here"):
                if local_params:
                    out_f.write(local_params)
            elif line.count("self.description = "):
                des0 = self.name + "\\n"
                desc = str(desc_str.lstrip().rstrip().replace('\"', ''))
                out_f.write(line% (des0 + desc) + "\n")
            elif line.count("def function(self, x=0.0%s):"):
                if self.is_2d:
                    y_str = ', y=0.0'
                    out_f.write(line% y_str + "\n")
                else:
                    out_f.write(line% '' + "\n")
            elif line.count("#function here"):
                for func_line in func_str.split('\n'):
                    f_line = func_line.rstrip()
                    if f_line:
                        out_f.write(spaces + f_line + "\n")
                if not func_str:
                    dep_var = 'y'
                    if self.is_2d:
                        dep_var = 'z'
                    out_f.write(spaces + 'return %s'% dep_var + "\n")
            elif line.count("#import scipy?"):
                if has_scipy:
                    out_f.write("import scipy" + "\n")
            #elif line.count("name = "):
            #    out_f.write(line % self.name + "\n")
            elif line:
                out_f.write(line + "\n")
        # run string for 2d
        if line_2d:
            for line in line_2d:
                out_f.write(line + "\n")
        # Test strins
        for line in line_test:
            out_f.write(line + "\n")
   
        out_f.close() 
    
    def set_param_helper(self, line):   
        """
        Get string in line to define the params dictionary
        
        :param line: one line of string got from the param_str
        """
        flag = True
        params_str = ''
        spaces = '        '#8spaces
        items = line.split(";")
        for item in items:
            name = item.split("=")[0].lstrip().rstrip()
            try:
                value = item.split("=")[1].lstrip().rstrip()
                float(value)
            except:
                value = 1.0 # default
            params_str += spaces + "self.params['%s'] = %s\n"% (name, value)
            
        return params_str

    def set_function_helper(self, line):   
        """
        Get string in line to define the local params
        
        :param line: one line of string got from the param_str
        """
        flag = True
        params_str = ''
        spaces = '        '#8spaces
        items = line.split(";")
        for item in items:
            name = item.split("=")[0].lstrip().rstrip()
            params_str += spaces + "%s = self.params['%s']\n"% (name, name)
        return params_str
    
    def get_warning(self):
        """
        Get the warning msg 
        """
        return self.warning
        
    def on_close(self, event):
        """
        leave data as it is and close
        """
        self.parent.Show(False)#Close()
        event.Skip()
        
class EditorWindow(wx.Frame):
    """
    Editor Window
    """
    def __init__(self, parent, base, path, title, 
                 size=(EDITOR_WIDTH, EDITOR_HEIGTH), *args, **kwds):
        """
        Init
        """
        kwds["title"] = title
        kwds["size"] = size
        wx.Frame.__init__(self, parent=None, *args, **kwds)
        self.parent = parent
        self.panel = EditorPanel(parent=self, base=parent, 
                                 path=path, title=title)
        self.Show(True)
        wx.EVT_CLOSE(self, self.OnClose)
    
    def OnClose(self, event):  
        """
        On close event
        """
        self.Show(False)
        #if self.parent != None:
        #    self.parent.new_model_frame = None
        #self.Destroy()  

## Templates for custom models
CUSTOM_TEMPLATE = """
from sans.models.pluginmodel import Model1DPlugin
from math import *
import os
import sys
import numpy
#import scipy?
class Model(Model1DPlugin):
    name = ""                             
    def __init__(self):
        Model1DPlugin.__init__(self, name=self.name)  
        #set name same as file name 
        self.name = self.get_fname()                                                   
        #self.params here
        self.description = "%s"
        self.set_details()
    def function(self, x=0.0%s):
        #local params here
        #function here
"""
CUSTOM_2D_TEMP = """
    def run(self, x=0.0, y=0.0):
        if x.__class__.__name__ == 'list':
            x_val = x[0]
            y_val = y[0]*0.0
            return self.function(x_val, y_val)
        elif x.__class__.__name__ == 'tuple':
            msg = "Tuples are not allowed as input to BaseComponent models"
            raise ValueError, msg
        else:
            return self.function(x, 0.0)
    def runXY(self, x=0.0, y=0.0):
        if x.__class__.__name__ == 'list':
            return self.function(x, y)
        elif x.__class__.__name__ == 'tuple':
            msg = "Tuples are not allowed as input to BaseComponent models"
            raise ValueError, msg
        else:
            return self.function(x, y)
    def evalDistribution(self, qdist):
        if qdist.__class__.__name__ == 'list':
            msg = "evalDistribution expects a list of 2 ndarrays"
            if len(qdist)!=2:
                raise RuntimeError, msg
            if qdist[0].__class__.__name__ != 'ndarray':
                raise RuntimeError, msg
            if qdist[1].__class__.__name__ != 'ndarray':
                raise RuntimeError, msg
            v_model = numpy.vectorize(self.runXY, otypes=[float])
            iq_array = v_model(qdist[0], qdist[1])
            return iq_array
        elif qdist.__class__.__name__ == 'ndarray':
            v_model = numpy.vectorize(self.runXY, otypes=[float])
            iq_array = v_model(qdist)
            return iq_array
"""
TEST_TEMPLATE = """
    def get_fname(self):
        path = sys._getframe().f_code.co_filename
        basename  = os.path.basename(path)
        name, _ = os.path.splitext(basename)
        return name
######################################################################
## THIS IS FOR TEST. DO NOT MODIFY THE FOLLOWING LINES!!!!!!!!!!!!!!!!       
if __name__ == "__main__": 
    m= Model() 
    out1 = m.runXY(0.0)
    out2 = m.runXY(0.01)
    isfine1 = numpy.isfinite(out1)
    isfine2 = numpy.isfinite(out2)
    print "Testing the value at Q = 0.0:"
    print out1, " : finite? ", isfine1
    print "Testing the value at Q = 0.01:"
    print out2, " : finite? ", isfine2
    if isfine1 and isfine2:
        print "===> Simple Test: Passed!"
    else:
        print "===> Simple Test: Failed!"
"""
SUM_TEMPLATE = """
# A sample of an experimental model function for Sum/Multiply(Pmodel1,Pmodel2)
import copy
from sans.models.pluginmodel import Model1DPlugin
# User can change the name of the model (only with single functional model)
#P1_model: 
#from sans.models.%s import %s as P1
#from %s import Model as P1 

#P2_model: 
#from sans.models.%s import %s as P2
#from %s import Model as P2 
import os
import sys

class Model(Model1DPlugin):
    name = ""
    def __init__(self):
        Model1DPlugin.__init__(self, name='')
        p_model1 = P1()
        p_model2 = P2()
        ## Setting  model name model description
        self.description = '%s'
        self.name = self.get_fname()
        if self.name.rstrip().lstrip() == '':
            self.name = self._get_name(p_model1.name, p_model2.name)
        if self.description.rstrip().lstrip() == '':
            self.description = p_model1.name
            self.description += p_model2.name
            self.fill_description(p_model1, p_model2)

        ## Define parameters
        self.params = {}

        ## Parameter details [units, min, max]
        self.details = {}
        ## Magnetic Panrameters
        self.magnetic_params = []
        # non-fittable parameters
        self.non_fittable = p_model1.non_fittable  
        self.non_fittable += p_model2.non_fittable  
            
        ##models 
        self.p_model1= p_model1
        self.p_model2= p_model2
        
       
        ## dispersion
        self._set_dispersion()
        ## Define parameters
        self._set_params()
        ## New parameter:scaling_factor
        self.params['scale_factor'] = %s
        
        ## Parameter details [units, min, max]
        self._set_details()
        self.details['scale_factor'] = ['', None, None]

        
        #list of parameter that can be fitted
        self._set_fixed_params()  
        ## parameters with orientation
        for item in self.p_model1.orientation_params:
            new_item = "p1_" + item
            if not new_item in self.orientation_params:
                self.orientation_params.append(new_item)
            
        for item in self.p_model2.orientation_params:
            new_item = "p2_" + item
            if not new_item in self.orientation_params:
                self.orientation_params.append(new_item)
        ## magnetic params
        for item in self.p_model1.magnetic_params:
            new_item = "p1_" + item
            if not new_item in self.magnetic_params:
                self.magnetic_params.append(new_item)
            
        for item in self.p_model2.magnetic_params:
            new_item = "p2_" + item
            if not new_item in self.magnetic_params:
                self.magnetic_params.append(new_item)
        # get multiplicity if model provide it, else 1.
        try:
            multiplicity1 = p_model1.multiplicity
            try:
                multiplicity2 = p_model2.multiplicity
            except:
                multiplicity2 = 1
        except:
            multiplicity1 = 1
            multiplicity2 = 1
        ## functional multiplicity of the model
        self.multiplicity1 = multiplicity1  
        self.multiplicity2 = multiplicity2    
        self.multiplicity_info = []   
        
    def _clone(self, obj):
        obj.params     = copy.deepcopy(self.params)
        obj.description     = copy.deepcopy(self.description)
        obj.details    = copy.deepcopy(self.details)
        obj.dispersion = copy.deepcopy(self.dispersion)
        obj.p_model1  = self.p_model1.clone()
        obj.p_model2  = self.p_model2.clone()
        #obj = copy.deepcopy(self)
        return obj
    
    def _get_name(self, name1, name2):
        p1_name = self._get_upper_name(name1)
        if not p1_name:
            p1_name = name1
        name = p1_name
        name += "_and_"
        p2_name = self._get_upper_name(name2)
        if not p2_name:
            p2_name = name2
        name += p2_name
        return name
    
    def _get_upper_name(self, name=None):
        if name == None:
            return ""
        upper_name = ""
        str_name = str(name)
        for index in range(len(str_name)):
            if str_name[index].isupper():
                upper_name += str_name[index]
        return upper_name
        
    def _set_dispersion(self):
        ##set dispersion only from p_model 
        for name , value in self.p_model1.dispersion.iteritems():
            #if name.lower() not in self.p_model1.orientation_params:
            new_name = "p1_" + name
            self.dispersion[new_name]= value 
        for name , value in self.p_model2.dispersion.iteritems():
            #if name.lower() not in self.p_model2.orientation_params:
            new_name = "p2_" + name
            self.dispersion[new_name]= value 
            
    def function(self, x=0.0): 
        return 0
                               
    def getProfile(self):
        try:
            x,y = self.p_model1.getProfile()
        except:
            x = None
            y = None
            
        return x, y
    
    def _set_params(self):
        for name , value in self.p_model1.params.iteritems():
            # No 2D-supported
            #if name not in self.p_model1.orientation_params:
            new_name = "p1_" + name
            self.params[new_name]= value
            
        for name , value in self.p_model2.params.iteritems():
            # No 2D-supported
            #if name not in self.p_model2.orientation_params:
            new_name = "p2_" + name
            self.params[new_name]= value
                
        # Set "scale" as initializing
        self._set_scale_factor()
      
            
    def _set_details(self):
        for name ,detail in self.p_model1.details.iteritems():
            new_name = "p1_" + name
            #if new_name not in self.orientation_params:
            self.details[new_name]= detail
            
        for name ,detail in self.p_model2.details.iteritems():
            new_name = "p2_" + name
            #if new_name not in self.orientation_params:
            self.details[new_name]= detail
    
    def _set_scale_factor(self):
        pass
        
                
    def setParam(self, name, value):
        # set param to this (p1, p2) model
        self._setParamHelper(name, value)
        
        ## setParam to p model 
        model_pre = ''
        new_name = ''
        name_split = name.split('_', 1)
        if len(name_split) == 2:
            model_pre = name.split('_', 1)[0]
            new_name = name.split('_', 1)[1]
        if model_pre == "p1":
            if new_name in self.p_model1.getParamList():
                self.p_model1.setParam(new_name, value)
        elif model_pre == "p2":
             if new_name in self.p_model2.getParamList():
                self.p_model2.setParam(new_name, value)
        elif name == 'scale_factor':
            self.params['scale_factor'] = value
        else:
            raise ValueError, "Model does not contain parameter %s" % name
            
    def getParam(self, name):
        # Look for dispersion parameters
        toks = name.split('.')
        if len(toks)==2:
            for item in self.dispersion.keys():
                # 2D not supported
                if item.lower()==toks[0].lower():
                    for par in self.dispersion[item]:
                        if par.lower() == toks[1].lower():
                            return self.dispersion[item][par]
        else:
            # Look for standard parameter
            for item in self.params.keys():
                if item.lower()==name.lower():
                    return self.params[item]
        return  
        #raise ValueError, "Model does not contain parameter %s" % name
       
    def _setParamHelper(self, name, value):
        # Look for dispersion parameters
        toks = name.split('.')
        if len(toks)== 2:
            for item in self.dispersion.keys():
                if item.lower()== toks[0].lower():
                    for par in self.dispersion[item]:
                        if par.lower() == toks[1].lower():
                            self.dispersion[item][par] = value
                            return
        else:
            # Look for standard parameter
            for item in self.params.keys():
                if item.lower()== name.lower():
                    self.params[item] = value
                    return
            
        raise ValueError, "Model does not contain parameter %s" % name
             
   
    def _set_fixed_params(self):
        for item in self.p_model1.fixed:
            new_item = "p1" + item
            self.fixed.append(new_item)
        for item in self.p_model2.fixed:
            new_item = "p2" + item
            self.fixed.append(new_item)

        self.fixed.sort()
                
                    
    def run(self, x = 0.0):
        self._set_scale_factor()
        return self.params['scale_factor'] %s \
(self.p_model1.run(x) %s self.p_model2.run(x))
    
    def runXY(self, x = 0.0):
        self._set_scale_factor()
        return self.params['scale_factor'] %s \
(self.p_model1.runXY(x) %s self.p_model2.runXY(x))
    
    ## Now (May27,10) directly uses the model eval function 
    ## instead of the for-loop in Base Component.
    def evalDistribution(self, x = []):
        self._set_scale_factor()
        return self.params['scale_factor'] %s \
(self.p_model1.evalDistribution(x) %s \
self.p_model2.evalDistribution(x))

    def set_dispersion(self, parameter, dispersion):
        value= None
        new_pre = parameter.split("_", 1)[0]
        new_parameter = parameter.split("_", 1)[1]
        try:
            if new_pre == 'p1' and \
new_parameter in self.p_model1.dispersion.keys():
                value= self.p_model1.set_dispersion(new_parameter, dispersion)
            if new_pre == 'p2' and \
new_parameter in self.p_model2.dispersion.keys():
                value= self.p_model2.set_dispersion(new_parameter, dispersion)
            self._set_dispersion()
            return value
        except:
            raise 

    def fill_description(self, p_model1, p_model2):
        description = ""
        description += "This model gives the summation or multiplication of"
        description += "%s and %s. "% ( p_model1.name, p_model2.name )
        self.description += description
          
    def get_fname(self):
        path = sys._getframe().f_code.co_filename
        basename  = os.path.basename(path)
        name, _ = os.path.splitext(basename)
        return name     
           
if __name__ == "__main__": 
    m1= Model() 
    #m1.setParam("p1_scale", 25)  
    #m1.setParam("p1_length", 1000)
    #m1.setParam("p2_scale", 100) 
    #m1.setParam("p2_rg", 100) 
    out1 = m1.runXY(0.01)

    m2= Model()
    #m2.p_model1.setParam("scale", 25) 
    #m2.p_model1.setParam("length", 1000) 
    #m2.p_model2.setParam("scale", 100)
    #m2.p_model2.setParam("rg", 100)
    out2 = m2.p_model1.runXY(0.01) %s m2.p_model2.runXY(0.01)\n
    print "My name is %s."% m1.name
    print out1, " = ", out2
    if out1 == out2:
        print "===> Simple Test: Passed!"
    else:
        print "===> Simple Test: Failed!"
"""
      
#if __name__ == "__main__": 
#    app = wx.PySimpleApp()
#    frame = TextDialog(id=1, model_list=["SphereModel", "CylinderModel"])   
#    frame.Show(True)
#    app.MainLoop()             

if __name__ == "__main__":
    from sans.perspectives.fitting import models
    dir_path = models.find_plugins_dir()
    app  = wx.App()
    window = EditorWindow(parent=None, base=None, path=dir_path, title="Editor")
    app.MainLoop()         