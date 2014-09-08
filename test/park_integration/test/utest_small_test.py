"""
    Unit tests for fitting module 
"""
import unittest
import math
from sans.fit.Fitting import Fit
from sans.dataloader.loader import Loader

class testFitModule(unittest.TestCase):
    """ test fitting """
    def test_park(self):
        """ Simple cylinder model fit (scipy)  """
        
        out= Loader().load("cyl_400_20.txt")
       
        fitter = Fit('scipy')
        # Receives the type of model for the fitting
        from sans.models.CylinderModel import CylinderModel
        model  = CylinderModel()
        model.setParam('sldCyl', 1)
        model.setParam('sldSolv', 0)

        pars1 =['length','radius','scale']
        fitter.set_data(out,1)
        model.setParam('scale', 1e-10)
        fitter.set_model(model,1,pars1, constraints=())
        fitter.select_problem_for_fit(id=1,value=1)
        result1, = fitter.fit()
        #print result1
        #print result1.__dict__

        self.assert_(result1)
        self.assertTrue(len(result1.pvec)>0 or len(result1.pvec)==0 )
        self.assertTrue(len(result1.stderr)> 0 or len(result1.stderr)==0)
        
        #print result1.pvec[0]-400.0, result1.pvec[0]
        #print math.fabs(result1.pvec[0]-400.0)/3.0
        self.assertTrue( math.fabs(result1.pvec[0]-400.0)/3.0 < result1.stderr[0] )
        self.assertTrue( math.fabs(result1.pvec[1]-20.0)/3.0  < result1.stderr[1] )
        self.assertTrue( math.fabs(result1.pvec[2]-9.0e-12)/3.0   < result1.stderr[2] )
        self.assertTrue( result1.fitness < 1.0 )
        