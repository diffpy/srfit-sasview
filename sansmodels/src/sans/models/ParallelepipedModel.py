#!/usr/bin/env python
"""
	This software was developed by the University of Tennessee as part of the
	Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
	project funded by the US National Science Foundation.

	If you use DANSE applications to do scientific research that leads to
	publication, we ask that you acknowledge the use of the software with the
	following sentence:

	"This work benefited from DANSE software developed under NSF award DMR-0520547."

	copyright 2008, University of Tennessee
"""

""" Provide functionality for a C extension model

	WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
 	         DO NOT MODIFY THIS FILE, MODIFY ..\c_extensions\parallelepiped.h
 	         AND RE-RUN THE GENERATOR SCRIPT

"""

from sans.models.BaseComponent import BaseComponent
from sans_extension.c_models import CParallelepipedModel
import copy    
    
class ParallelepipedModel(CParallelepipedModel, BaseComponent):
    """ Class that evaluates a ParallelepipedModel model. 
    	This file was auto-generated from ..\c_extensions\parallelepiped.h.
    	Refer to that file and the structure it contains
    	for details of the model.
    	List of default parameters:
         scale           = 1.0 
         short_a         = 35.0 [A]
         long_b          = 75.0 [A]
         longer_c        = 400.0 [A]
         contrast        = 5.3e-006 [1/A�]
         background      = 0.0 [1/cm]
         parallel_theta  = 0.0 [rad]
         parallel_phi    = 0.0 [rad]
         parallel_psi    = 0.0 [rad]

    """
        
    def __init__(self):
        """ Initialization """
        
        # Initialize BaseComponent first, then sphere
        BaseComponent.__init__(self)
        CParallelepipedModel.__init__(self)
        
        ## Name of the model
        self.name = "ParallelepipedModel"
        ## Model description
        self.description =""" Form factor for a rectangular solid with uniform scattering length density.
		
		scale:Scale factor
		short_a: length of short side of the parallelepiped [A]
		long_b: length of long side of the parallelepiped [A]
		longer_c: length of longer side of the parallelepiped [A]
		contrast: particle_sld - solvent_sld
		background:Incoherent Background [1/cm]"""
       
		## Parameter details [units, min, max]
        self.details = {}
        self.details['scale'] = ['', None, None]
        self.details['short_a'] = ['[A]', None, None]
        self.details['long_b'] = ['[A]', None, None]
        self.details['longer_c'] = ['[A]', None, None]
        self.details['contrast'] = ['[1/A�]', None, None]
        self.details['background'] = ['[1/cm]', None, None]
        self.details['parallel_theta'] = ['[rad]', None, None]
        self.details['parallel_phi'] = ['[rad]', None, None]
        self.details['parallel_psi'] = ['[rad]', None, None]

		## fittable parameters
        self.fixed=['short_a.width', 'long_b.width', 'longer_c.width', 'parallel_phi.width', 'parallel_psi.width', 'parallel_theta.width']
        
        ## parameters with orientation
        self.orientation_params =['parallel_phi', 'parallel_psi', 'parallel_theta', 'parallel_phi.width', 'parallel_psi.width', 'parallel_theta.width']
   
    def clone(self):
        """ Return a identical copy of self """
        return self._clone(ParallelepipedModel())   
   
    def run(self, x = 0.0):
        """ Evaluate the model
            @param x: input q, or [q,phi]
            @return: scattering function P(q)
        """
        
        return CParallelepipedModel.run(self, x)
   
    def runXY(self, x = 0.0):
        """ Evaluate the model in cartesian coordinates
            @param x: input q, or [qx, qy]
            @return: scattering function P(q)
        """
        
        return CParallelepipedModel.runXY(self, x)
        
    def evalDistribition(self, x = []):
        """ Evaluate the model in cartesian coordinates
            @param x: input q[], or [qx[], qy[]]
            @return: scattering function P(q[])
        """
        return CParallelepipedModel.evalDistribition(self, x)
        
    def set_dispersion(self, parameter, dispersion):
        """
            Set the dispersion object for a model parameter
            @param parameter: name of the parameter [string]
            @dispersion: dispersion object of type DispersionModel
        """
        return CParallelepipedModel.set_dispersion(self, parameter, dispersion.cdisp)
        
   
# End of file
