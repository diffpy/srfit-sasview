import  re
import sys, wx, logging
import string, numpy, math

from copy import deepcopy 
from danse.common.plottools.plottables import Data1D, Theory1D,Data2D
from danse.common.plottools.PlotPanel import PlotPanel
from sans.guicomm.events import NewPlotEvent, StatusEvent  
from sans.guicomm.events import EVT_SLICER_PANEL,ERR_DATA

from sans.fit.AbstractFitEngine import Model,FitData1D,FitData2D#,Data,
from fitproblem import FitProblem
from fitpanel import FitPanel
from fit_thread import FitThread
import models
import fitpage1D

DEFAULT_BEAM = 0.005
DEFAULT_QMIN = 0.0
DEFAULT_QMAX = 0.1
DEFAULT_NPTS = 50
import time
import thread

class Plugin:
    """
        Fitting plugin is used to perform fit 
    """
    def __init__(self):
        ## Plug-in name
        self.sub_menu = "Fitting"
        
        ## Reference to the parent window
        self.parent = None
        #Provide list of models existing in the application
        self.menu_mng = models.ModelManager()
        ## List of panels for the simulation perspective (names)
        self.perspective = []
        #list of panel to send to guiframe
        self.mypanels=[]
        # reference to the current running thread
        self.calc_thread = None
        # Start with a good default
        self.elapsed = 0.022
        # the type of optimizer selected, park or scipy
        self.fitter  = None
        #Flag to let the plug-in know that it is running stand alone
        self.standalone=True
        ## Fit engine
        self._fit_engine = 'scipy'
        #List of selected data
        self.selected_data_list=[]
        # Log startup
        logging.info("Fitting plug-in started")   
        # model 2D view
        self.model2D_id=None
        #keep reference of the simultaneous fit page
        self.sim_page=None
        #dictionary containing data name and error on dy of that data 
        self.err_dy={}
        
    def _on_data_error(self, event):
        """
            receives and event from plotting plu-gins to store the data name and 
            their errors of y coordinates for 1Data hide and show error
        """
        self.err_dy= event.err_dy
        
    def populate_menu(self, id, owner):
        """
            Create a menu for the Fitting plug-in
            @param id: id to create a menu
            @param owner: owner of menu
            @ return : list of information to populate the main menu
        """
        #Menu for fitting
        self.menu1 = wx.Menu()
        id1 = wx.NewId()
        self.menu1.Append(id1, '&Simultaneous')
        wx.EVT_MENU(owner, id1, self.on_add_sim_page)
        #Set park engine
        id3 = wx.NewId()
        scipy_help= "Scipy Engine: Perform Simple fit. More in Help window...."
        self.menu1.Append(id3, "Scipy",scipy_help) 
        wx.EVT_MENU(owner, id3,  self._onset_engine_scipy)
        
        id3 = wx.NewId()
        park_help = "Park Engine: Perform Complex fit. More in Help window...."
        self.menu1.Append(id3, "park",park_help) 
        wx.EVT_MENU(owner, id3,  self._onset_engine_park)
        
        #menu for model
        menu2 = wx.Menu()
    
        self.menu_mng.populate_menu(menu2, owner)
        id2 = wx.NewId()
        owner.Bind(models.EVT_MODEL,self._on_model_menu)
      
        self.fit_panel.set_owner(owner)
        self.fit_panel.set_model_list(self.menu_mng.get_model_list())
        owner.Bind(fitpage1D.EVT_MODEL_BOX,self._on_model_panel)
        
        #create  menubar items
        return [(id, self.menu1, "Fitting"),(id2, menu2, "Model")]
    
    def on_add_sim_page(self, event):
        """
            Create a page to access simultaneous fit option
        """
        self.sim_page= self.fit_panel.add_sim_page()
        self.sim_page.add_model(self.page_finder)
        
        
    def help(self, evt):
        """
            Show a general help dialog. 
            TODO: replace the text with a nice image
        """
        from helpPanel import  HelpWindow
        frame = HelpWindow(None, -1, 'HelpWindow')    
        frame.Show(True)
        
        
    def get_context_menu(self, graph=None):
        """
            Get the context menu items available for P(r)
            @param graph: the Graph object to which we attach the context menu
            @return: a list of menu items with call-back function
        """
        self.graph=graph
        for item in graph.plottables:
            if item.__class__.__name__ is "Data2D":
                return [["Select data  for Fitting",\
                          "Dialog with fitting parameters ", self._onSelect]] 
            else:
               
                if item.name==graph.selected_plottable :
                    if not hasattr(item, "group_id"):
                        return []
                    return [["Select data  for Fitting", \
                             "Dialog with fitting parameters ", self._onSelect]] 
        return []   


    def get_panels(self, parent):
        """
            Create and return a list of panel objects
        """
        self.parent = parent
        # Creation of the fit panel
        self.fit_panel = FitPanel(self.parent, -1)
        #Set the manager for the main panel
        self.fit_panel.set_manager(self)
        # List of windows used for the perspective
        self.perspective = []
        self.perspective.append(self.fit_panel.window_name)
        # take care of saving  data, model and page associated with each other
        self.page_finder = {}
        #index number to create random model name
        self.index_model = 0
        self.index_theory= 0
        self.parent.Bind(EVT_SLICER_PANEL, self._on_slicer_event)
        self.parent.Bind( ERR_DATA, self._on_data_error)
        
        #Send the fitting panel to guiframe
        self.mypanels.append(self.fit_panel)
        return self.mypanels

        
    def _on_slicer_event(self, event):
        """
            Receive a panel as event and send it to guiframe 
            @param event: event containing a panel
        """
        if event.panel!=None:
            new_panel = event.panel
            # Set group ID if available
            event_id = self.parent.popup_panel(new_panel)
            self.menu1.Append(event_id, new_panel.window_caption, 
                             "Show %s plot panel" % new_panel.window_caption)
            # Set UID to allow us to reference the panel later
            new_panel.uid = event_id
            new_panel
            self.mypanels.append(new_panel) 
        return    
    
        
    def _on_show_panel(self, event):
        print "_on_show_panel: fitting"
      
      
    def get_perspective(self):
        """
            Get the list of panel names for this perspective
        """
        return self.perspective
    
    
    def on_perspective(self, event):
        """
            Call back function for the perspective menu item.
            We notify the parent window that the perspective
            has changed.
        """
        self.parent.set_perspective(self.perspective)
    
    
    def post_init(self):
        """
            Post initialization call back to close the loose ends
            [Somehow openGL needs this call]
        """
        self.parent.set_perspective(self.perspective)


    def copy_data(self, item, dy):
        """
            receive a data 1D and the list of errors on dy
            and create a new data1D data
            @param return 
        """
        detector=None
        source=None
        dxl=None
        dxw=None
        if hasattr(item, "dxl"):
            dxl = item.dxl
        if hasattr(item, "dxw"):
            dxw = item.dxw
        if hasattr(item, "detector"):
            detector =item.detector
        if hasattr(item, "source"):
            source =item.source
        from sans.guiframe import dataFitting 
        data= dataFitting.Data1D(x=item.x, y=item.y, dy=dy, dxl=dxl, dxw=dxw)
        data.name=item.name
        data.detector=detector
        data.source= source
        return data


    def _onSelect(self,event):
        """ 
            when Select data to fit a new page is created .Its reference is 
            added to self.page_finder
        """
        self.panel = event.GetEventObject()
        for item in self.panel.graph.plottables:
            if item.name == self.panel.graph.selected_plottable:
                if len(self.err_dy)>0:
                    if item.name in  self.err_dy.iterkeys():
                        dy= self.err_dy[item.name]
                        data= self.copy_data(item, dy)
                    else:
                        data= item
                else:
                    if item.dy==None:
                        dy= numpy.zeros(len(item.y))
                        dy[dy==0]=1
                        data= self.copy_data(item, dy)
                    else:
                        data= item
            else:
                data= item
            ## create anew page                   
            if item.name == self.panel.graph.selected_plottable or\
                 item.__class__.__name__ is "Data2D":
                try:
                    page = self.fit_panel.add_fit_page(data)
                    # add data associated to the page created
                    if page !=None:   
                        #create a fitproblem storing all link to data,model,page creation
                        self.page_finder[page]= FitProblem()
                        ## item is almost the same as data but contains
                        ## axis info for plotting 
                        self.page_finder[page].add_plotted_data(item)
                        self.page_finder[page].add_fit_data(data)
                        
                        wx.PostEvent(self.parent, StatusEvent(status="Page Created"))
                    else:
                        wx.PostEvent(self.parent, StatusEvent(status="Page was already Created"))
                except:
                    wx.PostEvent(self.parent, StatusEvent(status="Creating Fit page: %s"\
                    %sys.exc_value))
                    return
                    
                    
    def schedule_for_fit(self,value=0,fitproblem =None):  
        """
            Set the fit problem field to 0 or 1 to schedule that problem to fit.
            Schedule the specified fitproblem or get the fit problem related to 
            the current page and set value.
            @param value : integer 0 or 1 
            @param fitproblem: fitproblem to schedule or not to fit
        """   
        if fitproblem !=None:
            fitproblem.schedule_tofit(value)
        else:
            current_pg=self.fit_panel.get_current_page() 
            for page, val in self.page_finder.iteritems():
                if page ==current_pg :
                    val.schedule_tofit(value)
                    break
                      
                    
    def get_page_finder(self):
        """ @return self.page_finder used also by simfitpage.py"""  
        return self.page_finder 
    
    
    def set_page_finder(self,modelname,names,values):
        """
             Used by simfitpage.py to reset a parameter given the string constrainst.
             @param modelname: the name ot the model for with the parameter has to reset
             @param value: can be a string in this case.
             @param names: the paramter name
             @note: expecting park used for fit.
        """  
        sim_page= self.sim_page
        for page, value in self.page_finder.iteritems():
            if page != sim_page:
                list=value.get_model()
                model = list[0]
                if model.name== modelname:
                    value.set_model_param(names,values)
                    break

   
                            
    def split_string(self,item): 
        """
            receive a word containing dot and split it. used to split parameterset
            name into model name and parameter name example:
            paramaterset (item) = M1.A
            @return model_name =M1 , parameter name =A
        """
        if string.find(item,".")!=-1:
            param_names= re.split("\.",item)
            model_name=param_names[0]
            param_name=param_names[1]  
            return model_name,param_name
        
   
    def _single_fit_completed(self,result,pars,cpage,qmin,qmax,elapsed=None,
                              ymin=None, ymax=None, xmin=None, xmax=None):
        """
            Display fit result on one page of the notebook.
            @param result: result of fit 
            @param pars: list of names of parameters fitted
            @param current_pg: the page where information will be displayed
            @param qmin: the minimum value of x to replot the model 
            @param qmax: the maximum value of x to replot model
          
        """
        wx.PostEvent(self.parent, StatusEvent(status="Single fit \
        complete! " , type="stop"))
        try:
            for page, value in self.page_finder.iteritems():
                if page==cpage :
                    list = value.get_model()
                    model= list[0]
                    break
            i = 0
            for name in pars:
                if result.pvec.__class__==numpy.float64:
                    model.setParam(name,result.pvec)
                else:
                    model.setParam(name,result.pvec[i])
                    i += 1
            ## Reset values of the current page to fit result
            cpage.onsetValues(result.fitness, result.pvec,result.stderr)
            ## plot the current model with new param
            self.plot_helper(currpage=cpage,qmin=qmin,qmax=qmax,
                             ymin=ymin, ymax=ymax,
                             xmin=xmin, xmax=xmax,title=None)
        except:
            msg= "Single Fit completed but Following error occurred:"
            wx.PostEvent(self.parent, StatusEvent(status="%s %s" % (msg, sys.exc_value)))
            return
       
       
    def _simul_fit_completed(self,result,qmin,qmax, elapsed,pars=None,cpage=None,
                             xmin=None, xmax=None, ymin=None, ymax=None):
        """
            Parameter estimation completed, 
            display the results to the user
            @param alpha: estimated best alpha
            @param elapsed: computation time
        """
        if cpage!=None:
            self._single_fit_completed(result=result,pars=pars,cpage=cpage,
                                       qmin=qmin,qmax=qmax,
                              ymin=ymin, ymax=ymax, xmin=xmin, xmax=xmax)
            return
        else:
            wx.PostEvent(self.parent, StatusEvent(status="Simultaneous fit \
            complete ", type="stop"))
            ## fit more than 1 model at the same time 
            try:
                for page, value in self.page_finder.iteritems():
                    if value.get_scheduled()==1:
                        list = value.get_model()
                        model= list[0]
                       
                        small_out = []
                        small_cov = []
                        i = 0
                        #Separate result in to data corresponding to each page
                        for p in result.parameters:
                            model_name,param_name = self.split_string(p.name)  
                            if model.name == model_name:
                                small_out.append(p.value )
                                if p.stderr==None:
                                    p.stderr=numpy.nan
                                small_cov.append(p.stderr)
                                model.setParam(param_name,p.value)  
                                
                        # Display result on each page 
                        page.onsetValues(result.fitness, small_out,small_cov)
                        #Replot models
                        msg= "Single Fit completed plotting %s:"%model.name
                        wx.PostEvent(self.parent, StatusEvent(status="%s " % msg))
                        self.plot_helper(currpage= page,qmin= qmin,qmax= qmax,
                                         xmin=xmin, xmax=xmax,
                                         ymin=ymin, ymax=ymax) 
            except:
                 msg= "Simultaneous Fit completed but Following error occurred: "
                 wx.PostEvent(self.parent, StatusEvent(status="%s%s" %(msg,sys.exc_value)))
                 return 
             
             
    def stop_fit(self):
        """
            Stop the fit engine
        """
        if self.calc_thread != None and self.calc_thread.isrunning():
            self.calc_thread.stop()
            wx.PostEvent(self.parent, StatusEvent(status="Fitting  \
                is cancelled" , type="stop"))
            
            
    def _on_single_fit(self,id=None,qmin=None, qmax=None,ymin=None, ymax=None,xmin=None,xmax=None):
        """ 
            perform fit for the  current page  and return chisqr,out and cov
            @param engineName: type of fit to be performed
            @param id: unique id corresponding to a fit problem(model, set of data)
            @param model: model to fit
            
        """
        #set an engine to perform fit
        from sans.fit.Fitting import Fit
        self.fitter = Fit(self._fit_engine)
        #Setting an id to store model and data in fit engine
        self.fit_id = 0
        if id!=None:
            self.fit_id = id
        
        page_fitted = None
        fit_problem = None
        #Get information (model , data) related to the page on 
        #with the fit will be perform
        current_pg= self.fit_panel.get_current_page() 
        simul_pg= self.sim_page
        pars=[]   
        ## Check that the current page is different from self.sim_page
        if current_pg != simul_pg:
            value = self.page_finder[current_pg]
            metadata =  value.get_fit_data()
            list = value.get_model()
            model = list[0]
            smearer = value.get_smearer()
           
            #Create list of parameters for fitting used
            templist=[]
            try:
                ## get the list of parameter names to fit
                templist = current_pg.get_param_list()
                for element in templist:
                    pars.append(str(element[0].GetLabelText()))
                pars.sort()
                 
                #Do the single fit
                self.fitter.set_model(Model(model), self.fit_id, pars)
                dy=[]
                x=[]
                y=[]
                ## checking the validity of error
                if metadata.__class__ in  ["Data1D","Theory1D"]:
                    for i in range(len(metadata.dy)):
                        if metadata.dy[i] !=0:
                            dy.append(metadata.dy[i])
                            x.append(metadata.x[i])
                            y.append(metadata.y[i])
                    if len(dy)>0:        
                        metadata.dy=numpy.zeros(len(dy))
                        metadata.dy=dy
                        metadata.y=numpy.zeros(len(y))
                        metadata.y=y
                        metadata.x=numpy.zeros(len(x))
                        metadata.x=x
                        
                self.fitter.set_data(data=metadata,Uid=self.fit_id,
                                     smearer=smearer,qmin= qmin,qmax=qmax,
                                     ymin=ymin,ymax=ymax)
                
                self.fitter.select_problem_for_fit(Uid= self.fit_id,
                                                   value= value.get_scheduled())
                page_fitted=current_pg
               
            except:
                msg= "Single Fit error: %s" % sys.exc_value
                wx.PostEvent(self.parent, StatusEvent(status= msg ))
                return
            # make sure to keep an alphabetic order 
            #of parameter names in the list      
            try:
                ## If a thread is already started, stop it
                if self.calc_thread != None and self.calc_thread.isrunning():
                    self.calc_thread.stop()
                        
                self.calc_thread =FitThread(parent =self.parent,
                                            fn= self.fitter,
                                            pars= pars,
                                            cpage= page_fitted,
                                           qmin=qmin,
                                           qmax=qmax,
                                          
                                           completefn=self._single_fit_completed,
                                           updatefn=None)
                self.calc_thread.queue()
                self.calc_thread.ready(2.5)
             
            except:
                wx.PostEvent(self.parent, StatusEvent(status="Single Fit error: %s" % sys.exc_value))
                return
         
    def _on_simul_fit(self, id=None,qmin=None,qmax=None, ymin=None, ymax=None):
        """ 
            perform fit for all the pages selected on simpage and return chisqr,out and cov
            @param engineName: type of fit to be performed
            @param id: unique id corresponding to a fit problem(model, set of data)
             in park_integration
            @param model: model to fit
            
        """
        ##Setting an id to store model and data
        self.fit_id= 0
        #Setting an id to store model and data
        if id!=None:
             self.fit_id= id
        ##  count the number of fitproblem schedule to fit 
        fitproblem_count= 0
        for value in self.page_finder.itervalues():
            if value.get_scheduled()==1:
                fitproblem_count += 1
        ## if simultaneous fit change automatically the engine to park
        if fitproblem_count >1:
            self._on_change_engine(engine='park')
        from sans.fit.Fitting import Fit
        self.fitter= Fit(self._fit_engine)
        
        
        for page, value in self.page_finder.iteritems():
            try:
                if value.get_scheduled()==1:
                    metadata = value.get_fit_data()
                    list = value.get_model()
                    model= list[0]
                    ## store page
                    cpage= page
                    #Get list of parameters name to fit
                    pars = []
                    templist = []
                    templist = page.get_param_list()
                    for element in templist:
                        try:
                            name = str(element[0].GetLabelText())
                            pars.append(name)
                        except:
                            wx.PostEvent(self.parent, StatusEvent(status="Simultaneous Fit error: %s" % sys.exc_value))
                            return
                    ## create a park model and reset parameter value if constraint
                    ## is given
                    new_model=Model(model)
                    param=value.get_model_param()
                    
                    if len(param)>0:
                        for item in param:
                            param_value = item[1]
                            param_name = item[0]
    
                            new_model.parameterset[ param_name].set( param_value )
                        
                    self.fitter.set_model(new_model, self.fit_id, pars) 
                    ## check that non -zero value are send as dy in the fit engine
                    dy=[]
                    x=[]
                    y=[]
                    if metadata.__class__ in  ["Data1D","Theory1D"]:
                        for i in range(len(metadata.dy)):
                            if metadata.dy[i] !=0:
                                dy.append(metadata.dy[i])
                                x.append(metadata.x[i])
                                y.append(metadata.y[i])
                            if len(dy)>0:        
                                metadata.dy=numpy.zeros(len(dy))
                                metadata.dy=dy
                                metadata.y=numpy.zeros(len(y))
                                metadata.y=y
                                metadata.x=numpy.zeros(len(x))
                                metadata.x=x
                                
                    self.fitter.set_data(metadata,self.fit_id,qmin,qmax,ymin,ymax)
                    self.fitter.select_problem_for_fit(Uid= self.fit_id,
                                                       value= value.get_scheduled())
                    self.fit_id += 1 
                    value.clear_model_param()
                   
            except:
                msg= "Simultaneous Fit error: %s" % sys.exc_value
                wx.PostEvent(self.parent, StatusEvent(status= msg ))
                return 
            
        #Do the simultaneous fit
        try:
            ## If a thread is already started, stop it
            if self.calc_thread != None and self.calc_thread.isrunning():
                self.calc_thread.stop()
			## perform single fit
            if  fitproblem_count==1:
                self.calc_thread =FitThread(parent =self.parent,
                                        fn= self.fitter,
                                       qmin=qmin,
                                       qmax=qmax,
                                       ymin= ymin,
                                       ymax= ymax,
                                       cpage=cpage,
                                       pars= pars,
                                       completefn= self._simul_fit_completed,
                                       updatefn=None)
                      
            else:
                ## Perform more than 1 fit at the time
                self.calc_thread =FitThread(parent =self.parent,
                                        fn= self.fitter,
                                       qmin=qmin,
                                       qmax=qmax,
                                       ymin= ymin,
                                       ymax= ymax,
                                       completefn= self._simul_fit_completed,
                                       updatefn=None)
            self.calc_thread.queue()
            self.calc_thread.ready(2.5)
            
        except:
            msg= "Simultaneous Fit error: %s" % sys.exc_value
            wx.PostEvent(self.parent, StatusEvent(status= msg ))
            return
        
    def _onset_engine_park(self,event):
        """ 
            set engine to park
        """
        self._on_change_engine('park')
       
       
    def _onset_engine_scipy(self,event):
        """ 
            set engine to scipy
        """
        self._on_change_engine('scipy')
       
    
    def _on_change_engine(self, engine='park'):
        """
            Allow to select the type of engine to perform fit 
            @param engine: the key work of the engine
        """
        self._fit_engine = engine
        wx.PostEvent(self.parent, StatusEvent(status="Engine set to: %s" % self._fit_engine))
   
   
    def _on_model_panel(self, evt):
        """
            react to model selection on any combo box or model menu.plot the model  
            @param evt: wx.combobox event
        """
       
        model = evt.model
        name = evt.name
       
        sim_page=self.sim_page
        current_pg = self.fit_panel.get_current_page() 
        ## make sure nothing is done on self.sim_page
        ## example trying to call set_panel on self.sim_page
        if current_pg != sim_page:
           
            if len(self.page_finder[current_pg].get_model())==0:
                
                model.name="M"+str(self.index_model)
                self.index_model += 1  
            else:
                model.name= self.page_finder[current_pg].get_model()[0].name
                
            try:
                metadata=self.page_finder[current_pg].get_plotted_data()
                M_name = model.name+"= "+name+"("+metadata.name+")"
            except:
                M_name = model.name+"= "+name
            # save the name containing the data name with the appropriate model
            self.page_finder[current_pg].set_model(model,M_name)
            
                
            # save model name
            self.plot_helper(currpage= current_pg,qmin= None,qmax= None)
            if self.sim_page!=None:
                self.sim_page.add_model(self.page_finder)
        
        
        
    def  set_smearer(self,smearer):
        """
            Get a smear object and store it to a fit problem
            @param smearer: smear object to allow smearing data
        """   
        current_pg=self.fit_panel.get_current_page()
        self.page_finder[current_pg].set_smearer(smearer)
         
         
    def redraw_model(self,qmin= None,qmax= None):
        """
            Draw a theory according to model changes or data range.
            @param qmin: the minimum value plotted for theory
            @param qmax: the maximum value plotted for theory
        """
        current_pg=self.fit_panel.get_current_page()
        for page, value in self.page_finder.iteritems():
            if page ==current_pg :
                break 
        self.plot_helper(currpage=page,qmin= qmin,qmax= qmax)
        
        
        
    def plot_helper(self,currpage, qmin=None,qmax=None,
                    ymin=None,ymax=None, xmin=None, xmax=None,title=None ):
        """
            Plot a theory given a model and data
            @param model: the model from where the theory is derived
            @param currpage: page in a dictionary referring to some data
        """
        if self.fit_panel.GetPageCount() >1:
            for page in self.page_finder.iterkeys():
                if  page == currpage :  
                    data= self.page_finder[page].get_plotted_data()
                    list= self.page_finder[page].get_model()
                    smearer = self.page_finder[page].get_smearer()
                    model = list[0]
                    break 
            ## create Model 1D
            if data != None and data.__class__.__name__ != 'Data2D':
                x= numpy.zeros(len(data.x))  
                y= numpy.zeros(len(data.y)) 
                
                theory = Theory1D(x=x, y=y)
                theory.name = model.name
                if hasattr(data ,"group_id"):
                    theory.group_id = data.group_id
                theory.id = "Model"
                
                x_name, x_units = data.get_xaxis() 
                y_name, y_units = data.get_yaxis() 
                theory.xaxis(x_name, x_units)
                theory.yaxis(y_name, y_units)
                if qmin == None :
                    qmin = min(data.x)
                if qmax == None :
                    qmax = max(data.x)
                
                j=0
                try:
                    tempx = qmin
                    tempy = model.run(qmin)
                    theory.x[j]=tempx
                    theory.y[j]=tempy
                    j+=1
                except :
                        wx.PostEvent(self.parent, StatusEvent(status="fitting \
                        skipping point x %g %s" %(qmin, sys.exc_value)))
                           
                for i in range(len(data.x)):
                    try:
                        if data.x[i]> qmin and data.x[i]< qmax: 
                            tempx = data.x[i]
                            tempy = model.run(tempx)
                            
                            if j< i:
                                theory.x[j]=tempx 
                                theory.y[j]=tempy
                                j+=1
                           
                    except:
                        wx.PostEvent(self.parent, StatusEvent(status="fitting \
                        skipping point x %g %s" %(data.x[i], sys.exc_value)))   
                try:
                    tempx = qmax
                    tempy = model.run(qmax)
                
                    theory.x[j]=tempx 
                    theory.y[j]=tempy
                    j+=1
                except:
                    wx.PostEvent(self.parent, StatusEvent(status="fitting \
                        skipping point x %g %s" %(qmin, sys.exc_value)) )
                
                if smearer!=None:
                    theory.y= smearer(theory.y)   
                wx.PostEvent(self.parent, NewPlotEvent(plot=theory,
                                                title=str(data.name)))
            else:
                ## create Model 2D
                theory=Data2D(data.data, data.err_data)
                theory.name= model.name
                if title !=None:
                    self.title = title
                    theory.id= self.title
                    theory.group_id= self.title+data.name
                else:
                    self.title= "Analytical model 2D "
                    theory.id= "Model"
                    theory.group_id= "Model"+data.name
                theory.x_bins= data.x_bins
                theory.y_bins= data.y_bins
                tempy=[]
                
                if qmin==None:
                    qmin=0
                if qmax==None:
                    x= math.pow(max(math.fabs(data.xmax),math.fabs(data.xmin)),2)
                    y= math.pow(max(math.fabs(data.ymax),math.fabs(data.ymin)),2)
                    qmax=math.sqrt( x+y )
                    
                if ymin==None:
                    ymin=data.ymin
                if ymax==None:
                    ymax=data.ymax
                if xmin ==None:
                    xmin=data.xmin
                if xmax==None:
                    xmax=data.xmax      
                                  
                theory.data = numpy.zeros((len(data.y_bins),len(data.x_bins)))
                for j in range(len(data.y_bins)):
                    for i in range(len(data.x_bins)):
                        tempqij=math.sqrt(( math.pow(data.y_bins[j],2)\
                                           +math.pow(data.x_bins[i],2) ))
                        
                        if tempqij>= qmin and tempqij<= qmax: 
                            theory.data[j][i] = model.runXY([data.y_bins[j],
                                                             data.x_bins[i]] )
                        else:
                            ## Later, We need to decide which of  0 and None is better.
                            theory.data[j][i]=0 
             
                theory.detector= data.detector
                theory.source= data.source
                ## qmin, qmax will used later to define q range.
                theory.qmin= qmin
                theory.qmax= qmax
                ## plot boundaries
                theory.ymin= ymin
                theory.ymax= ymax
                theory.xmin= xmin
                theory.xmax= xmax
        
                wx.PostEvent(self.parent, NewPlotEvent(plot=theory,
                                                title=self.title +str(data.name)))
        
        
    def _on_model_menu(self, evt):
        """
            Plot a theory from a model selected from the menu
            @param evt: wx.menu event
        """
        name = evt.model.__class__.__name__
        if hasattr(evt.model, "name"):
            name = evt.model.name
        model=evt.model
        description=model.description
        
        # Create a model page. If a new page is created, the model
        # will be plotted automatically. If a page already exists,
        # the content will be updated and the plot refreshed
        self.fit_panel.add_model_page(model,description,name,topmenu=True)
    
    def complete1D_from_data(self, output,model, data, x, elapsed, name):
        """
             plot model 1D with data info 
        """
        y= output
        x= data.x
        theory = Theory1D(x=x, y=y)
        theory.name = model.name
        theory.group_id = data.group_id
        theory.id = "Model"
        
        x_name, x_units = data.get_xaxis() 
        y_name, y_units = data.get_yaxis() 
        theory.xaxis(x_name, x_units)
        theory.yaxis(y_name, y_units)
        wx.PostEvent(self.parent, NewPlotEvent(plot=theory,
                                                title=str(data.name)))
        
    def draw_model1D_from_Data(self, data, model,name=None,
                                qmin=None, qmax=None, smearer= None):
        """
            Draw model 1D from loaded data1D
            @param data: loaded data
            @param model: the model to plot
        """
        x = data.x
        self.model= model
        if qmin == None :
           qmin = min(data.x)
        if qmax == None :
           qmax = max(data.x)
        if name ==None:
            name=model.name
        try:
            from model_thread import Calc1D
            ## If a thread is already started, stop it
            if self.calc_thread != None and self.calc_thread.isrunning():
                self.calc_thread.stop()
            self.calc_thread = Calc1D( x= x,
                                      model= self.model, 
                                       qmin= qmin,
                                       qmax= qmax,
                                       name= name,
                                       smearer= smearer,
                            completefn= self.complete1D_from_data,
                            updatefn= self.update1D)
            self.calc_thread.queue()
            
        except:
            msg= " Error occurred when drawing %s Model 1D: "%self.model.name
            msg+= " %s"%sys.exc_value
            wx.PostEvent( self.parent, StatusEvent(status= msg ))
            return  
            
    def draw_model(self, model, name, data= None, description= None,
                   enable1D= True, enable2D= False,
                   qmin= DEFAULT_QMIN, qmax= DEFAULT_QMAX, qstep= DEFAULT_NPTS):
        """
             Draw model.
             @param model: the model to draw
             @param name: the name of the model to draw
             @param data: the data on which the model is based to be drawn
             @param description: model's description
             @param enable1D: if true enable drawing model 1D
             @param enable2D: if true enable drawing model 2D
             @param qmin:  Range's minimum value to draw model
             @param qmax:  Range's maximum value to draw model
             @param qstep: number of step to divide the x and y-axis
             
        """
        ## draw model based on loaded data
        if data !=None:
            self.redraw_model(qmin,qmax)
            return 
        ## draw model 1D with no loaded data
        self._draw_model1D(model,name,model.description, enable1D,qmin,qmax, qstep)
        ## draw model 2D with no initial data
        self._draw_model2D(model=model,
                           description=model.description,
                           enable2D= enable2D,
                           qmin=qmin,
                           qmax=qmax,
                           qstep=qstep)
        
    
    def update1D(self,x, output):
        """
            Update the output of plotting model 1D
        """
        self.calc_thread.ready(1)
    
    def complete1D(self, x,output, elapsed, name,data=None):
        """
            Complete plotting 1D data
        """ 
        try:
            y = output
            new_plot = Theory1D(x, y)
            new_plot.name = name
            new_plot.xaxis("\\rm{Q}", 'A^{-1}')
            new_plot.yaxis("\\rm{Intensity} ","cm^{-1}")
            new_plot.id ="Model"
            new_plot.group_id ="Model"
            # Pass the reset flag to let the plotting event handler
            # know that we are replacing the whole plot
            wx.PostEvent(self.parent, NewPlotEvent(plot=new_plot,
                             title="Analytical model 1D ", reset=True ))
            
        except:
            msg= " Error occurred when drawing %s Model 1D: "%new_plot.name
            msg+= " %s"%sys.exc_value
            wx.PostEvent( self.parent, StatusEvent(status= msg ))
            return  
        
                 
    def _draw_model1D(self, model, name, description= None, enable1D= True,
                      qmin= DEFAULT_QMIN, qmax= DEFAULT_QMAX, qstep= DEFAULT_NPTS):
        """
            Draw model 1D between qmin and qmax value
            @param model: the model to draw
            @param name: the name of the model
            @param description: descripion of the model as string
            @param enable1D:  allow to draw model 1D if True  else False
            @param qmin: the minimum value of the range to draw the model
            @param qmax: the maximum value of the range to draw the model
            @param qstep: the number of points to draw  
        """
        x=  numpy.linspace(start= qmin,
                           stop= qmax,
                           num= qstep,
                           endpoint=True
                           )      
        self.model= model
        if enable1D:
            try:
                from model_thread import Calc1D
                ## If a thread is already started, stop it
                if self.calc_thread != None and self.calc_thread.isrunning():
                    self.calc_thread.stop()
                self.calc_thread = Calc1D( x= x,
                                          model= self.model, 
                                           qmin= qmin,
                                           qmax= qmax,
                                           name= name,
                                           data=None,
                                        smearer=None,
                                completefn= self.complete1D,
                                updatefn= self.update1D)
                self.calc_thread.queue()
                
            except:
                msg= " Error occurred when drawing %s Model 1D: "%self.model.name
                msg+= " %s"%sys.exc_value
                wx.PostEvent( self.parent, StatusEvent(status= msg ))
                return  
                


        
    def update2D(self, output,time=None):
        """
            Update the output of plotting model
        """
        wx.PostEvent(self.parent, StatusEvent(status="Plot \
        #updating ... ",type="update"))
        self.calc_thread.ready(0.01)
        
        
    def complete2D(self, output, elapsed, model, qmin, qmax,qstep=DEFAULT_NPTS):
        """
            Complete get the result of modelthread and create model 2D
            that can be plot.
        """
        msg = "Calc complete !"
        wx.PostEvent( self.parent, StatusEvent( status= msg , type="stop" ))
    
        data = output
        temp= numpy.zeros(numpy.shape(data))
        temp[temp==0]=1
        theory= Data2D(image=data, err_image=temp)
    
        from DataLoader.data_info import Detector, Source
        
        detector = Detector()
        theory.detector=[]
        theory.detector.append(detector) 
            
        theory.detector[0].distance=1e+32
        theory.source= Source()
        theory.source.wavelength=2*math.pi/1e+32
        theory.x_bins =[]
        theory.y_bins =[]
        ## Create detector for Model 2D
        xmax=2*theory.detector[0].distance*math.atan(\
                            qmax/(4*math.pi/theory.source.wavelength))
        
        theory.detector[0].pixel_size.x= xmax/(qstep/2-0.5)
        theory.detector[0].pixel_size.y= xmax/(qstep/2-0.5)
        theory.detector[0].beam_center.x= qmax
        theory.detector[0].beam_center.y= qmax
        ## create x_bins and y_bins of the model 2D
        distance   = theory.detector[0].distance
        pixel      = qstep/2-1
        theta      = pixel / distance / qstep#100.0
        wavelength = theory.source.wavelength
        pixel_width_x = theory.detector[0].pixel_size.x
        pixel_width_y = theory.detector[0].pixel_size.y
        center_x      = theory.detector[0].beam_center.x/pixel_width_x
        center_y      = theory.detector[0].beam_center.y/pixel_width_y
        
        
        size_x, size_y= numpy.shape(theory.data)
        for i_x in range(size_x):
            theta = (i_x-center_x)*pixel_width_x / distance 
            qx = 4.0*math.pi/wavelength * math.tan(theta/2.0)
            theory.x_bins.append(qx)    
        for i_y in range(size_y):
            theta = (i_y-center_y)*pixel_width_y / distance 
            qy =4.0*math.pi/wavelength * math.tan(theta/2.0)
            theory.y_bins.append(qy)
           
        theory.name= model.name
        theory.group_id ="Model"
        theory.id ="Model"
        ## determine plot boundaries
        theory.xmin= -qmax
        theory.xmax= qmax
        theory.ymin= -qmax
        theory.ymax= qmax
        ## plot
        wx.PostEvent(self.parent, NewPlotEvent(plot=theory,
                         title="Analytical model 2D ", reset=True ))
         
        
         
    def _draw_model2D(self,model,description=None, enable2D=False,
                      qmin=DEFAULT_QMIN, qmax=DEFAULT_QMAX, qstep=DEFAULT_NPTS):
        """
            draw model in 2D
            @param model: instance of the model to draw
            @param description: the description of the model
            @param enable2D: when True allows to draw model 2D
            @param qmin: the minimum value to  draw model 2D
            @param qmax: the maximum value to draw model 2D
            @param qstep: the number of division of Qx and Qy of the model to draw
            
        """
        x=  numpy.linspace(start= -1*qmax,
                               stop= qmax,
                               num= qstep,
                               endpoint=True )  
        y = numpy.linspace(start= -1*qmax,
                               stop= qmax,
                               num= qstep,
                               endpoint=True )
       
        self.model= model
        if enable2D:
            try:
                from model_thread import Calc2D
                ## If a thread is already started, stop it
                if self.calc_thread != None and self.calc_thread.isrunning():
                    self.calc_thread.stop()
                self.calc_thread = Calc2D( x= x,
                                           y= y, model= self.model, 
                                           qmin= qmin,
                                           qmax= qmax,
                                           qstep= qstep,
                                completefn= self.complete2D,
                                updatefn= self.update2D )
                self.calc_thread.queue()
                
            except:
                raise
    
   
if __name__ == "__main__":
    i = Plugin()
    
    
    
    