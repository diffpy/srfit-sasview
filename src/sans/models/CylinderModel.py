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
   src\sans\models\include\cylinder.h
   AND RE-RUN THE GENERATOR SCRIPT
"""

from sans.models.BaseComponent import BaseComponent
from sans.models.sans_extension.c_models import CCylinderModel

def create_CylinderModel():
    """
       Create a model instance
    """
    obj = CylinderModel()
    # CCylinderModel.__init__(obj) is called by
    # the CylinderModel constructor
    return obj

class CylinderModel(CCylinderModel, BaseComponent):
    """ 
    Class that evaluates a CylinderModel model. 
    This file was auto-generated from src\sans\models\include\cylinder.h.
    Refer to that file and the structure it contains
    for details of the model.
    
    List of default parameters:

    * scale           = 1.0 
    * radius          = 20.0 [A]
    * length          = 400.0 [A]
    * sldCyl          = 4e-06 [1/A^(2)]
    * sldSolv         = 1e-06 [1/A^(2)]
    * background      = 0.0 [1/cm]
    * cyl_theta       = 60.0 [deg]
    * cyl_phi         = 60.0 [deg]
    * M0_sld_cyl      = 0.0 [1/A^(2)]
    * M_theta_cyl     = 0.0 [deg]
    * M_phi_cyl       = 0.0 [deg]
    * M0_sld_solv     = 0.0 [1/A^(2)]
    * M_theta_solv    = 0.0 [deg]
    * M_phi_solv      = 0.0 [deg]
    * Up_frac_i       = 0.5 [u/(u+d)]
    * Up_frac_f       = 0.5 [u/(u+d)]
    * Up_theta        = 0.0 [deg]

    """
        
    def __init__(self, multfactor=1):
        """ Initialization """
        self.__dict__ = {}
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        #apply(CCylinderModel.__init__, (self,)) 

        CCylinderModel.__init__(self)
        self.is_multifunc = False
		        
        ## Name of the model
        self.name = "CylinderModel"
        ## Model description
        self.description = """
         f(q)= 2*(sldCyl - sldSolv)*V*sin(qLcos(alpha/2))
		/[qLcos(alpha/2)]*J1(qRsin(alpha/2))/[qRsin(alpha)]
		
		P(q,alpha)= scale/V*f(q)^(2)+bkg
		V: Volume of the cylinder
		R: Radius of the cylinder
		L: Length of the cylinder
		J1: The bessel function
		alpha: angle betweenthe axis of the
		cylinder and the q-vector for 1D
		:the ouput is P(q)=scale/V*integral
		from pi/2 to zero of...
		f(q)^(2)*sin(alpha)*dalpha+ bkg
        """
       
        ## Parameter details [units, min, max]
        self.details = {}
        self.details['scale'] = ['', None, None]
        self.details['radius'] = ['[A]', None, None]
        self.details['length'] = ['[A]', None, None]
        self.details['sldCyl'] = ['[1/A^(2)]', None, None]
        self.details['sldSolv'] = ['[1/A^(2)]', None, None]
        self.details['background'] = ['[1/cm]', None, None]
        self.details['cyl_theta'] = ['[deg]', None, None]
        self.details['cyl_phi'] = ['[deg]', None, None]
        self.details['M0_sld_cyl'] = ['[1/A^(2)]', None, None]
        self.details['M_theta_cyl'] = ['[deg]', None, None]
        self.details['M_phi_cyl'] = ['[deg]', None, None]
        self.details['M0_sld_solv'] = ['[1/A^(2)]', None, None]
        self.details['M_theta_solv'] = ['[deg]', None, None]
        self.details['M_phi_solv'] = ['[deg]', None, None]
        self.details['Up_frac_i'] = ['[u/(u+d)]', None, None]
        self.details['Up_frac_f'] = ['[u/(u+d)]', None, None]
        self.details['Up_theta'] = ['[deg]', None, None]

        ## fittable parameters
        self.fixed = ['cyl_phi.width',
                      'cyl_theta.width',
                      'length.width',
                      'radius.width']
        
        ## non-fittable parameters
        self.non_fittable = []
        
        ## parameters with orientation
        self.orientation_params = ['cyl_phi',
                                   'cyl_theta',
                                   'cyl_phi.width',
                                   'cyl_theta.width',
                                   'M0_sld_cyl',
                                   'M_theta_cyl',
                                   'M_phi_cyl',
                                   'M0_sld_solv',
                                   'M_theta_solv',
                                   'M_phi_solv',
                                   'Up_frac_i',
                                   'Up_frac_f',
                                   'Up_theta']

        ## parameters with magnetism
        self.magnetic_params = ['M0_sld_cyl', 'M_theta_cyl', 'M_phi_cyl', 'M0_sld_solv', 'M_theta_solv', 'M_phi_solv', 'Up_frac_i', 'Up_frac_f', 'Up_theta']

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
        return (create_CylinderModel, tuple(), state, None, None)
        
    def clone(self):
        """ Return a identical copy of self """
        return self._clone(CylinderModel())   
       	
    def run(self, x=0.0):
        """ 
        Evaluate the model
        
        :param x: input q, or [q,phi]
        
        :return: scattering function P(q)
        
        """
        return CCylinderModel.run(self, x)
   
    def runXY(self, x=0.0):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q, or [qx, qy]
        
        :return: scattering function P(q)
        
        """
        return CCylinderModel.runXY(self, x)
        
    def evalDistribution(self, x):
        """ 
        Evaluate the model in cartesian coordinates
        
        :param x: input q[], or [qx[], qy[]]
        
        :return: scattering function P(q[])
        
        """
        return CCylinderModel.evalDistribution(self, x)
        
    def calculate_ER(self):
        """ 
        Calculate the effective radius for P(q)*S(q)
        
        :return: the value of the effective radius
        
        """       
        return CCylinderModel.calculate_ER(self)
        
    def calculate_VR(self):
        """ 
        Calculate the volf ratio for P(q)*S(q)
        
        :return: the value of the volf ratio
        
        """       
        return CCylinderModel.calculate_VR(self)
              
    def set_dispersion(self, parameter, dispersion):
        """
        Set the dispersion object for a model parameter
        
        :param parameter: name of the parameter [string]
        :param dispersion: dispersion object of type DispersionModel
        
        """
        return CCylinderModel.set_dispersion(self,
               parameter, dispersion.cdisp)
        
   
# End of file
