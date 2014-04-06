"""
Class Fit contains ScipyFit and ParkFit methods declaration
allows to create instance of type ScipyFit or ParkFit to perform either
a park fit or a scipy fit.
"""

#from scipy import optimize
from sans.fit.ScipyFitting import ScipyFit
from sans.fit.ParkFitting import ParkFit
from sans.fit.BumpsFitting import BumpsFit

ENGINES={
    'scipy': ScipyFit,
    'park': ParkFit,
    'bumps': BumpsFit,
}

class Fit(object):
    """ 
    Wrap class that allows to select the fitting type.this class 
    can be used as follow : ::
    
        from sans.fit.Fitting import Fit
        fitter= Fit()
        fitter.fit_engine('scipy') or fitter.fit_engine('park')
        engine = fitter.returnEngine()
        engine.set_data(data,id)
        engine.set_param( model,model.name, pars)
        engine.set_model(model,id)
        
        chisqr1, out1, cov1=engine.fit(pars,qmin,qmax)
        
    """  
    def __init__(self, engine='scipy'):
        """
        """
        #self._engine will contain an instance of ScipyFit or ParkFit
        self._engine = None
        self.fitter_id = None
        self.set_engine(engine)
          
    def __setattr__(self, name, value):
        """
        set fitter_id and its engine at the same time
        """
        if name == "fitter_id":
            self.__dict__[name] = value
            if hasattr(self, "_engine") and self._engine is not None:
                self._engine.fitter_id = value    
        elif name == "_engine":
            self.__dict__[name] = value
            if hasattr(self, "fitter_id") and self.fitter_id is not None:
                self._engine.fitter_id = self.fitter_id
        else:
            self.__dict__[name] = value
                
    def set_engine(self, word):
        """
        Select the type of Fit 
        
        :param word: the keyword to select the fit type 
        
        :raise: if the user does not enter 'scipy' or 'park',
             a valueError is raised 
             
        """
        try:
            self._engine = ENGINES[word]()
        except KeyError, exc:
            raise KeyError("fit engine should be one of scipy, park or bumps")

    def fit(self, msg_q=None, q=None, handler=None, 
                        curr_thread=None, 
                        ftol=1.49012e-8,
                        reset_flag=False):
        """Perform the fit """
        return self._engine.fit(msg_q=msg_q, 
                                q=q, handler=handler, curr_thread=curr_thread,
                                ftol=ftol, reset_flag=reset_flag)
     
    def set_model(self, model, id, pars=[], constraints=[], data=None):
        """
        store a model model to fit at the position id of the fit engine
        """
        self._engine.set_model(model, id, pars, constraints, data=data)
   
    def set_data(self, data, id, smearer=None, qmin=None, qmax=None):
        """
        Store data to fit at the psotion id of the fit engine
        
        :param data: data to fit
        :param smearer: smearerobject to smear data
        :param qmin: the minimum q range to fit 
        :param qmax: the minimum q range to fit
        
        """
        self._engine.set_data(data, id, smearer, qmin, qmax)
        
    def get_model(self, id):
        """ return list of data"""
        self._engine.get_model(id)


    def remove_fit_problem(self, id):
        """remove fitarrange in id"""
        self._engine.remove_fit_problem(id)
        
    def select_problem_for_fit(self, id, value):
        """
        select a couple of model and data at the id position in dictionary
        and set in self.selected value to value
        
        :param value: the value to allow fitting.
             can only have the value one or zero
        """
        self._engine.select_problem_for_fit(id, value)
        
    def get_problem_to_fit(self, id):
        """
        return the self.selected value of the fit problem of id
           
        :param id: the id of the problem
        
        """
        return self._engine.get_problem_to_fit(id)
