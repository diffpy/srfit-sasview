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

.. WARNING::

   THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
   DO NOT MODIFY THIS FILE, MODIFY
   src\sans\models\include\raspberry.h
   AND RE-RUN THE GENERATOR SCRIPT
"""

from sans.models.BaseComponent import BaseComponent
from sans.models.sans_extension.c_models import CRaspBerryModel

def create_RaspBerryModel():
    """
       Create a model instance
    """
    obj = RaspBerryModel()
    # CRaspBerryModel.__init__(obj) is called by
    # the RaspBerryModel constructor
    return obj

class RaspBerryModel(CRaspBerryModel, BaseComponent):
    """ 
    Class that evaluates a RaspBerryModel model. 
    This file was auto-generated from src\sans\models\include\raspberry.h.
    Refer to that file and the structure it contains
    for details of the model.
    
    List of default parameters:

    * volf_Lsph       = 0.05 
    * radius_Lsph     = 5000.0 [A]
    * sld_Lsph        = -4e-07 [1/A^(2)]
    * volf_Ssph       = 0.005 
    * radius_Ssph     = 100.0 [A]
    * surfrac_Ssph    = 0.4 
    * sld_Ssph        = 3.5e-06 [1/A^(2)]
    * delta_Ssph      = 0.0 
    * sld_solv        = 6.3e-06 [1/A^(2)]
    * background      = 0.0 [1/cm]

    """
        
    def __init__(self, multfactor=1):
        """ Initialization """
        self.__dict__ = {}
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        #apply(CRaspBerryModel.__init__, (self,)) 

        CRaspBerryModel.__init__(self)
        self.is_multifunc = False
		        
        ## Name of the model
        self.name = "RaspBerryModel"
        ## Model description
        self.description = """
         RaspBerryModel:
		volf_Lsph = volume fraction large spheres
		radius_Lsph = radius large sphere (A)
		sld_Lsph = sld large sphere (A-2)
		volf_Ssph = volume fraction small spheres
		radius_Ssph = radius small sphere (A)
		surfrac_Ssph = fraction of small spheres at surface
		sld_Ssph = sld small sphere
		delta_Ssph = small sphere penetration (A)
		sld_solv   = sld solvent
		background = background (cm-1)
		Ref: J. coll. inter. sci. (2010) vol. 343 (1) pp. 36-41.
        """
       
        ## Parameter details [units, min, max]
        self.details = {}
        self.details['volf_Lsph'] = ['', None, None]
        self.details['radius_Lsph'] = ['[A]', None, None]
        self.details['sld_Lsph'] = ['[1/A^(2)]', None, None]
        self.details['volf_Ssph'] = ['', None, None]
        self.details['radius_Ssph'] = ['[A]', None, None]
        self.details['surfrac_Ssph'] = ['', None, None]
        self.details['sld_Ssph'] = ['[1/A^(2)]', None, None]
        self.details['delta_Ssph'] = ['', None, None]
        self.details['sld_solv'] = ['[1/A^(2)]', None, None]
        self.details['background'] = ['[1/cm]', None, None]

        ## fittable parameters
        self.fixed = ['radius_Lsph.width']
        
        ## non-fittable parameters
        self.non_fittable = []
        
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
        return (create_RaspBerryModel, tuple(), state, None, None)
        
    def clone(self):
        """ Return a identical copy of self """
        return self._clone(RaspBerryModel())   
       	
    def run(self, x=0.0):
        """ 
        Evaluate the model
        
        :param x: input q, or [q,phi]
        
        :return: scattering function P(q)
        
        """
        return CRaspBerryModel.run(self, x)
   
    def runXY(self, x=0.0):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q, or [qx, qy]
        
        :return: scattering function P(q)
        
        """
        return CRaspBerryModel.runXY(self, x)
        
    def evalDistribution(self, x):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q[], or [qx[], qy[]]
        
        :return: scattering function P(q[])
        
        """
        return CRaspBerryModel.evalDistribution(self, x)
        
    def calculate_ER(self):
        """ 
        Calculate the effective radius for P(q)*S(q)
        
        :return: the value of the effective radius
        
        """       
        return CRaspBerryModel.calculate_ER(self)
        
    def calculate_VR(self):
        """ 
        Calculate the volf ratio for P(q)*S(q)
        
        :return: the value of the volf ratio
        
        """       
        return CRaspBerryModel.calculate_VR(self)
              
    def set_dispersion(self, parameter, dispersion):
        """
        Set the dispersion object for a model parameter
        
        :param parameter: name of the parameter [string]
        :param dispersion: dispersion object of type DispersionModel
        
        """
        return CRaspBerryModel.set_dispersion(self,
               parameter, dispersion.cdisp)
        
   
# End of file
