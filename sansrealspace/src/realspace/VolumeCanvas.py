#!/usr/bin/env python
""" Volume Canvas
    Simulation canvas
"""

from sans.models.BaseComponent import BaseComponent
from sansModeling.pointsmodelpy import pointsmodelpy
from sansModeling.geoshapespy import geoshapespy

import os.path

class ShapeDescriptor:
    """
        Class to hold the information about a shape
    """
    def __init__(self):
        """
            Initialization
        """
        ## Real space object
        self.shapeObject = None
        ## Parameters of the object
        self.params = {}
        self.params["center"] = [0, 0, 0]
        self.params["orientation"] = [0, 0, 0]
        # Default to lores shape
        self.params['is_lores'] = True
        self.params['order'] = 0
            
    def create(self):
        """
            Create an instance of the shape
        """
        # Set center
        x0 = self.params["center"][0]
        y0 = self.params["center"][1]
        z0 = self.params["center"][2]
        geoshapespy.set_center(self.shapeObject, x0, y0, z0)
        
        # Set orientation
        x0 = self.params["orientation"][0]
        y0 = self.params["orientation"][1]
        z0 = self.params["orientation"][2]
        geoshapespy.set_orientation(self.shapeObject, x0, y0, z0)
               
class SphereDescriptor(ShapeDescriptor):
    """
        Descriptor for a sphere
    """
    def __init__(self):
        """
            Initialization
        """ 
        ShapeDescriptor.__init__(self)
        # Default parameters
        self.params["type"]   = "sphere"
        self.params["radius"] = 20.0
        self.params["contrast"] = 1.0

    def create(self):
        """
            Create an instance of the shape
            @return: instance of the shape
        """
        self.shapeObject = geoshapespy.new_sphere(\
            self.params["radius"])
        
        ShapeDescriptor.create(self)   
        return self.shapeObject
    
class CylinderDescriptor(ShapeDescriptor):
    """
        Descriptor for a cylinder
    """
    def __init__(self):
        """
            Initialization
        """ 
        ShapeDescriptor.__init__(self)
        # Default parameters
        self.params["type"]   = "cylinder"
        self.params["length"] = 40.0
        self.params["radius"] = 10.0
        self.params["contrast"] = 1.0
        
    def create(self):
        """
            Create an instance of the shape
            @return: instance of the shape
        """
        self.shapeObject = geoshapespy.new_cylinder(\
            self.params["radius"], self.params["length"])

        ShapeDescriptor.create(self)
        return self.shapeObject
        

class EllipsoidDescriptor(ShapeDescriptor):
    """
        Descriptor for an ellipsoid
    """
    def __init__(self):
        """
            Initialization
        """ 
        ShapeDescriptor.__init__(self)
        # Default parameters
        self.params["type"]   = "ellipsoid"
        self.params["radius_x"] = 30.0
        self.params["radius_y"] = 20.0
        self.params["radius_z"] = 10.0
        self.params["contrast"] = 1.0
        
    def create(self):
        """
            Create an instance of the shape
            @return: instance of the shape
        """
        self.shapeObject = geoshapespy.new_ellipsoid(\
            self.params["radius_x"], self.params["radius_y"], 
            self.params["radius_z"])
        
        ShapeDescriptor.create(self)   
        return self.shapeObject
        
class HelixDescriptor(ShapeDescriptor):
    """
        Descriptor for an helix
    """
    def __init__(self):
        """
            Initialization
        """ 
        ShapeDescriptor.__init__(self)
        # Default parameters
        self.params["type"]   = "singlehelix"
        self.params["radius_helix"] = 10.0
        self.params["radius_tube"] = 3.0
        self.params["pitch"] = 34.0
        self.params["turns"] = 3.0
        self.params["contrast"] = 1.0

    def create(self):
        """
            Create an instance of the shape
            @return: instance of the shape
        """
        self.shapeObject = geoshapespy.new_singlehelix(\
            self.params["radius_helix"], self.params["radius_tube"], 
            self.params["pitch"], self.params["turns"])
        
        ShapeDescriptor.create(self)   
        return self.shapeObject
        
class PDBDescriptor(ShapeDescriptor):
    """
        Descriptor for a PDB set of points
    """
    def __init__(self, filename):
        """
            Initialization
            @param filename: name of the PDB file to load
        """ 
        ShapeDescriptor.__init__(self)
        # Default parameters
        self.params["type"]   = "pdb"
        self.params["file"] = filename
        self.params['is_lores'] = False

    def create(self):
        """
            Create an instance of the shape
            @return: instance of the shape
        """
        self.shapeObject = pointsmodelpy.new_pdbmodel()
        pointsmodelpy.pdbmodel_add(self.shapeObject, self.params['file'])       
        
        #ShapeDescriptor.create(self)   
        return self.shapeObject
        
# Define a dictionary for the shape until we find
# a better way to create them
shape_dict = {'sphere':SphereDescriptor,
              'cylinder':CylinderDescriptor,
              'ellipsoid':EllipsoidDescriptor,
              'singlehelix':HelixDescriptor}
        
class VolumeCanvas(BaseComponent):
    """
        Class representing an empty space volume to add 
        geometrical object to.
    """
    
    def __init__(self):
        """
            Initialization
        """
        BaseComponent.__init__(self)
        
        ## Maximum value of q reachable
        self.params['q_max'] = 0.1
        self.params['lores_density'] = 0.1
        self.params['scale'] = 1.0
        self.params['background'] = 0.0
        
        self.lores_model = pointsmodelpy.new_loresmodel(self.params['lores_density'])
        self.complex_model = pointsmodelpy.new_complexmodel()
        self.shapes = {}
        self.shapecount = 0        
        self.points = None
        self.npts = 0
        self.hasPr = False        
        
    def add(self, shape, id = None):
        """
            @param shape: name of the object to add to the canvas [string]
            @param id: string handle for the object [string] [optional]
            @return: string handle for the object
        """
        # If the handle is not provided, create one
        if id == None:
            id = "shape"+str(self.shapecount)
 
        #shapeDesc = ShapeDescriptor(shape.lower())
        if shape.lower() in shape_dict:
            shapeDesc = shape_dict[shape.lower()]()
        elif os.path.isfile(shape):
            # A valid filename was supplier, create a PDB object
            shapeDesc = PDBDescriptor(shape)
        else:
            raise ValueError, "VolumeCanvas.add: Unknown shape %s" % shape
        
        # Self the order number
        shapeDesc.params['order'] = self.shapecount
        # Store the shape in a dictionary entry associated
        # with the handle
        self.shapes[id] = shapeDesc
        self.shapecount += 1

        #model changed, need to recalculate P(r)
        self.hasPr = False

        return id

    def delete(self, id):
        """
            Delete a shape. The ID for the shape is required.
            @param id: string handle for the object [string] [optional]
        """

        if self.shapes.has_key(id):
            del self.shapes[id]
        else:
            raise KeyError, "VolumeCanvas.delete: could not find shape ID"

        #model changed, need to recalculate P(r)
        self.hasPr = False


    def setParam(self, name, value):    
        """
            @param name: name of the parameter to change
            @param value: value to give the parameter
        """
        
        # Lowercase for case insensitivity
        name = name.lower()
        
        # Look for shape access
        toks = name.split('.')
        
        # If a shape identifier was given, look the shape up
        # in the dictionary
        if len(toks)>1:
            if toks[0] in self.shapes.keys():
                # The shape was found, now look for the parameter
                if toks[1] in self.shapes[toks[0]].params:
                    # The parameter was found, now change it
                    self.shapes[toks[0]].params[toks[1]] = value
                    self.hasPr = False
                else:
                    raise ValueError, "Could not find parameter %s" % name
            else:
                raise ValueError, "Could not find shape %s" % toks[0]
        
        else:
            # If we are not accessing the parameters of a 
            # shape, see if the parameter is part of this object
            BaseComponent.setParam(self, name, value)
            self.hasPr = False

    def getParam(self, name):    
        """
            @param name: name of the parameter to change
        """
        #TODO: clean this up
        
        # Lowercase for case insensitivity
        name = name.lower()
        
        # Look for sub-model access
        toks = name.split('.')
        if len(toks) == 1:
            try:
                self.params.has_key(toks[0])
            except KeyError:
                raise ValueError, \
                    "VolumeCanvas.getParam: Could not find %s" % name

            value = self.params[toks[0]]
            if isinstance(value, ShapeDescriptor):
                raise ValueError, \
                    "VolumeCanvas.getParam: Cannot get parameter value." 
            else:
                return value

        elif len(toks) == 2:
            try:
                self.shapes.has_key(toks[0])
            except KeyError:
                raise ValueError, \
                    "VolumeCanvas.getParam: Could not find %s" % name

            shapeinstance = self.shapes[toks[0]]

            try:
                shapeinstance.params.has_key(toks[1])
            except KeyError:
                raise ValueError, \
                    "VolumeCanvas.getParam: Could not find %s" % name

            return shapeinstance.params[toks[1]]

        else:
            raise ValueError, \
                "VolumeCanvas.getParam: Could not find %s" % name
            
    def getParamList(self, shapeid = None):
        """
	       return a full list of all available parameters from 
           self.params.keys(). If a key in self.params is a instance
           of ShapeDescriptor, extend the return list to: 
           [param1,param2,shapeid.param1,shapeid.param2.......]

           If shapeid is provided, return the list of parameters that
           belongs to that shape id only : [shapeid.param1, shapeid.param2...]
        """

        param_list = []
        if shapeid == None:        
            for key1 in self.params.keys():
                #value1 = self.params[key1]
                param_list.append(key1)
            for key2 in self.shapes.keys():
                value2 = self.shapes[key2]
                header = key2 + '.'
                for key3 in value2.params.keys():   
                    fullname = header + key3                 
                    param_list.append(fullname)
     
        else:
            try:
                self.shapes.has_key(shapeid)
            except KeyError:
                raise ValueError, \
                    "VolumeCanvas: getParamList: Could not find %s" % shapeid
            header = shapeid + '.'
            param_list = self.shapes[shapeid].params.keys()  
            for i in range(len(param_list)):
                param_list[i] = header + param_list[i]

        return param_list

    def getShapeList(self):
        """
            Return a list of the shapes 
        """
        return self.shapes.keys()

    def addSingleShape(self, shapeDesc):
        """
            create shapeobject based on shapeDesc
            @param shapeDesc: shape description
        """
        #Create the object model
        shapeDesc.create()
                    
        if shapeDesc.params['is_lores']:
            # Add the shape to the lores_model
            pointsmodelpy.lores_add(self.lores_model, 
                shapeDesc.shapeObject, shapeDesc.params['contrast'])  

    def createVolumeFromList(self):
        """
            Create a new lores model with all the shapes in our internal list
            Whenever we change a parameter of a shape, we have to re-create
            the whole thing.
            
            Items with higher 'order' number take precedence for regions
            of space that are shared with other objects. Points in the 
            overlapping region belonging to objects with lower 'order'
            will be ignored.
            
            Items are added in decreasing 'order' number.
            The item with the highest 'order' will be added *first*.
            [That conventions is prescribed by the realSpaceModeling module]
        """
        
        # Create empty model
        self.lores_model = \
            pointsmodelpy.new_loresmodel(self.params['lores_density'])

        # Create empty complex model
        self.complex_model = pointsmodelpy.new_complexmodel()
       
        # Order the object first
        obj_list = []
    
        for shape in self.shapes:
            order = self.shapes[shape].params['order']
            # find where to place it in the list
            stored = False
            
            for i in range(len(obj_list)):
                if obj_list[i][0] > order:
                    obj_list.insert(i, [order, shape])
                    stored = True
                    break
            
            if not stored:
                obj_list.append([order, shape])
                
        # Add each shape
        len_list = len(obj_list)
        for i in range(len_list-1, -1, -1):
            shapedesc = self.shapes[obj_list[i][1]]
            self.addSingleShape(shapedesc)

        return 0     
    
    def getPr(self):
        """
            Calculate P(r)
            @return: calculation output flag 
        """
        # To find a complete example of the correct call order:
        # In LORES2, in actionclass.py, method CalculateAction._get_iq()
        
        # If there are not shapes, do nothing
        if len(self.shapes) == 0:
            self.hasPr = False
            return 0
        
        # generate space filling points from shape list
        self.createVolumeFromList()

        self.points = pointsmodelpy.new_point3dvec()

        pointsmodelpy.complexmodel_add(self.complex_model, 
                                        self.lores_model, "LORES")
        for shape in self.shapes:
            if self.shapes[shape].params['is_lores'] == False:
                pointsmodelpy.complexmodel_add(self.complex_model, 
                    self.shapes[shape].shapeObject, "PDB")
        
        #pointsmodelpy.get_lorespoints(self.lores_model, self.points)
        self.npts = pointsmodelpy.get_complexpoints(self.complex_model, self.points)
        
        # expecting the rmax is a positive float or 0. The maximum distance.
        #rmax = pointsmodelpy.get_lores_pr(self.lores_model, self.points)   
         
        rmax = pointsmodelpy.get_complex_pr(self.complex_model, self.points) 
        self.hasPr = True   

        return rmax
        
    def run(self, q = 0):
        """
            Returns the value of I(q) for a given q-value
            @param q: q-value [float]
            @return: I(q) [float]
        """
        #TODO: The right simulation function should be
        # called according to the type of input we get.
        # For now, only a q length is supported.
        return getIq(q)
        
    def getIq(self, q):
        """
            Returns the value of I(q) for a given q-value
            
            This method should remain internal to the class
            and the run() method should be used instead.
            
            @param q: q-value [float]
            @return: I(q) [float]
        """
        
        if self.hasPr == False:
            self.getPr()

        # By dividing by the density instead of the actuall V/N, 
        # we have an uncertainty of +-1 on N because the number 
        # of points chosen for the simulation is int(density*volume).
        # Propagation of error gives:
        #   delta(1/density^2) = 2*(1/density^2)/N
        # where N is stored in self.npts

        norm =  1.0e8/self.params['lores_density']*self.params['scale']
        #return norm*pointsmodelpy.get_lores_i(self.lores_model, q)
        return norm*pointsmodelpy.get_complex_i(self.complex_model, q)\
            + self.params['background']
    
    def getError(self, q):
        """
            Returns the error of I(q) for a given q-value
            @param q: q-value [float]
            @return: I(q) [float]
        """
        
        if self.hasPr == False:
            self.getPr()

        # By dividing by the density instead of the actuall V/N, 
        # we have an uncertainty of +-1 on N because the number 
        # of points chosen for the simulation is int(density*volume).
        # Propagation of error gives:
        #   delta(1/density^2) = 2*(1/density^2)/N
        # where N is stored in self.npts

        norm =  1.0e8/self.params['lores_density']*self.params['scale']
        #return norm*pointsmodelpy.get_lores_i(self.lores_model, q)
        return norm*pointsmodelpy.get_complex_i_error(self.complex_model, q)\
            + self.params['background']
    
    def getIqError(self, q):
        """
            Return the simulated value along with its estimated
            error for a given q-value
            
            Propagation of errors is used to evaluate the
            uncertainty.
            
            @param q: q-value [float]
            @return: mean, error [float, float]
        """
        val = self.getIq(q)
        # Simulation error (statistical)
        err = self.getError(q)
        # Error on V/N
        simerr = 2*val/self.npts
        return val, err+simerr
        