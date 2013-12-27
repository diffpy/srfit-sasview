##############################################################################
# This software was developed by the University of Tennessee as part of the
# Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
# project funded by the US National Science Foundation.
#
# If you use DANSE applications to do scientific research that leads to
# publication, we ask that you acknowledge the use of the software with the
# following sentence:
#
# This work benefited from DANSE software developed under NSF award DMR-0520547
#
# Copyright 2008-2011, University of Tennessee
##############################################################################

""" 
Provide functionality for a C extension model

:WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
         DO NOT MODIFY THIS FILE, MODIFY
            src\sans\models\include\refl.h
         AND RE-RUN THE GENERATOR SCRIPT
"""

from sans.models.BaseComponent import BaseComponent
from sans.models.sans_extension.c_models import CReflModel

def create_ReflModel():
    """
       Create a model instance
    """
    obj = ReflModel()
    # CReflModel.__init__(obj) is called by
    # the ReflModel constructor
    return obj

class ReflModel(CReflModel, BaseComponent):
    """ 
    Class that evaluates a ReflModel model. 
    This file was auto-generated from src\sans\models\include\refl.h.
    Refer to that file and the structure it contains
    for details of the model.
    List of default parameters:
         n_layers        = 1.0 
         scale           = 1.0 
         thick_inter0    = 1.0 [A]
         func_inter0     = 0.0 
         sld_bottom0     = 2.07e-06 [1/A^(2)]
         sld_medium      = 1e-06 [1/A^(2)]
         background      = 0.0 
         sld_flat1       = 4e-06 [1/A^(2)]
         sld_flat2       = 3.5e-06 [1/A^(2)]
         sld_flat3       = 4e-06 [1/A^(2)]
         sld_flat4       = 3.5e-06 [1/A^(2)]
         sld_flat5       = 4e-06 [1/A^(2)]
         sld_flat6       = 3.5e-06 [1/A^(2)]
         sld_flat7       = 4e-06 [1/A^(2)]
         sld_flat8       = 3.5e-06 [1/A^(2)]
         sld_flat9       = 4e-06 [1/A^(2)]
         sld_flat10      = 3.5e-06 [1/A^(2)]
         thick_inter1    = 1.0 [A]
         thick_inter2    = 1.0 [A]
         thick_inter3    = 1.0 [A]
         thick_inter4    = 1.0 [A]
         thick_inter5    = 1.0 [A]
         thick_inter6    = 1.0 [A]
         thick_inter7    = 1.0 [A]
         thick_inter8    = 1.0 [A]
         thick_inter9    = 1.0 [A]
         thick_inter10   = 1.0 [A]
         thick_flat1     = 10.0 [A]
         thick_flat2     = 100.0 [A]
         thick_flat3     = 100.0 [A]
         thick_flat4     = 100.0 [A]
         thick_flat5     = 100.0 [A]
         thick_flat6     = 100.0 [A]
         thick_flat7     = 100.0 [A]
         thick_flat8     = 100.0 [A]
         thick_flat9     = 100.0 [A]
         thick_flat10    = 100.0 [A]
         func_inter1     = 0.0 
         func_inter2     = 0.0 
         func_inter3     = 0.0 
         func_inter4     = 0.0 
         func_inter5     = 0.0 
         func_inter6     = 0.0 
         func_inter7     = 0.0 
         func_inter8     = 0.0 
         func_inter9     = 0.0 
         func_inter10    = 0.0 

    """
        
    def __init__(self, multfactor=1):
        """ Initialization """
        self.__dict__ = {}
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        #apply(CReflModel.__init__, (self,)) 

        CReflModel.__init__(self)
        self.is_multifunc = False
		        
        ## Name of the model
        self.name = "ReflModel"
        ## Model description
        self.description = """
        Calculate neutron reflectivity using the Parratt iterative formula
		Parameters:
		background:background
		scale: scale factor
		sld_bottom0: the SLD of the substrate
		sld_medium: the SLD of the incident medium
		or superstrate
		sld_flatN: the SLD of the flat region of
		the N'th layer
		thick_flatN: the thickness of the flat
		region of the N'th layer
		func_interN: the function used to describe
		the interface of the N'th layer
		thick_interN: the thickness of the interface
		of the N'th layer
		Note: the layer number starts to increase
		from the bottom (substrate) to the top.
        """
       
        ## Parameter details [units, min, max]
        self.details = {}
        self.details['n_layers'] = ['', None, None]
        self.details['scale'] = ['', None, None]
        self.details['thick_inter0'] = ['[A]', None, None]
        self.details['func_inter0'] = ['', None, None]
        self.details['sld_bottom0'] = ['[1/A^(2)]', None, None]
        self.details['sld_medium'] = ['[1/A^(2)]', None, None]
        self.details['background'] = ['', None, None]
        self.details['sld_flat1'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat2'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat3'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat4'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat5'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat6'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat7'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat8'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat9'] = ['[1/A^(2)]', None, None]
        self.details['sld_flat10'] = ['[1/A^(2)]', None, None]
        self.details['thick_inter1'] = ['[A]', None, None]
        self.details['thick_inter2'] = ['[A]', None, None]
        self.details['thick_inter3'] = ['[A]', None, None]
        self.details['thick_inter4'] = ['[A]', None, None]
        self.details['thick_inter5'] = ['[A]', None, None]
        self.details['thick_inter6'] = ['[A]', None, None]
        self.details['thick_inter7'] = ['[A]', None, None]
        self.details['thick_inter8'] = ['[A]', None, None]
        self.details['thick_inter9'] = ['[A]', None, None]
        self.details['thick_inter10'] = ['[A]', None, None]
        self.details['thick_flat1'] = ['[A]', None, None]
        self.details['thick_flat2'] = ['[A]', None, None]
        self.details['thick_flat3'] = ['[A]', None, None]
        self.details['thick_flat4'] = ['[A]', None, None]
        self.details['thick_flat5'] = ['[A]', None, None]
        self.details['thick_flat6'] = ['[A]', None, None]
        self.details['thick_flat7'] = ['[A]', None, None]
        self.details['thick_flat8'] = ['[A]', None, None]
        self.details['thick_flat9'] = ['[A]', None, None]
        self.details['thick_flat10'] = ['[A]', None, None]
        self.details['func_inter1'] = ['', None, None]
        self.details['func_inter2'] = ['', None, None]
        self.details['func_inter3'] = ['', None, None]
        self.details['func_inter4'] = ['', None, None]
        self.details['func_inter5'] = ['', None, None]
        self.details['func_inter6'] = ['', None, None]
        self.details['func_inter7'] = ['', None, None]
        self.details['func_inter8'] = ['', None, None]
        self.details['func_inter9'] = ['', None, None]
        self.details['func_inter10'] = ['', None, None]

        ## fittable parameters
        self.fixed = []
        
        ## non-fittable parameters
        self.non_fittable = ['n_layers',
                             'func_inter0',
                             'func_inter1',
                             'func_inter2',
                             'func_inter3',
                             'func_inter4',
                             'func_inter5',
                             'func_inter5',
                             'func_inter7',
                             'func_inter8',
                             'func_inter9',
                             'func_inter10']
        
        ## parameters with orientation
        self.orientation_params = []

        ## parameters with magnetism
        self.magnetic_params = []

        self.category = None
        self.multiplicity_info = None
        
    def __setstate__(self, state):
        """
        restore the state of a model from pickle
        """
        self.__dict__, self.params, self.dispersion = state
        
    def __reduce_ex__(self, proto):
        """
        Overwrite the __reduce_ex__ of PyTypeObject *type call in the init of 
        c model.
        """
        state = (self.__dict__, self.params, self.dispersion)
        return (create_ReflModel, tuple(), state, None, None)
        
    def clone(self):
        """ Return a identical copy of self """
        return self._clone(ReflModel())   
       	
    def run(self, x=0.0):
        """ 
        Evaluate the model
        
        :param x: input q, or [q,phi]
        
        :return: scattering function P(q)
        
        """
        return CReflModel.run(self, x)
   
    def runXY(self, x=0.0):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q, or [qx, qy]
        
        :return: scattering function P(q)
        
        """
        return CReflModel.runXY(self, x)
        
    def evalDistribution(self, x):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q[], or [qx[], qy[]]
        
        :return: scattering function P(q[])
        
        """
        return CReflModel.evalDistribution(self, x)
        
    def calculate_ER(self):
        """ 
        Calculate the effective radius for P(q)*S(q)
        
        :return: the value of the effective radius
        
        """       
        return CReflModel.calculate_ER(self)
        
    def calculate_VR(self):
        """ 
        Calculate the volf ratio for P(q)*S(q)
        
        :return: the value of the volf ratio
        
        """       
        return CReflModel.calculate_VR(self)
              
    def set_dispersion(self, parameter, dispersion):
        """
        Set the dispersion object for a model parameter
        
        :param parameter: name of the parameter [string]
        :param dispersion: dispersion object of type DispersionModel
        
        """
        return CReflModel.set_dispersion(self,
               parameter, dispersion.cdisp)
        
   
# End of file

