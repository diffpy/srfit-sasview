"""
This software was developed by the University of Tennessee as part of the
Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
project funded by the US National Science Foundation. 

See the license text in license.txt

copyright 2008, University of Tennessee
"""

import numpy
import os
from DataLoader.data_info import Data1D

# Check whether we have a converter available
has_converter = True
try:
    from data_util.nxsunit import Converter
except:
    has_converter = False

class Reader:
    """
        Class to load ascii files (2 or 3 columns)
    """
    ## File type
    type = ["ASCII files (*.txt)|*.txt",
            "ASCII files (*.dat)|*.dat"]
    ## List of allowed extensions
    ext=['.txt', '.TXT', '.dat', '.DAT']  
    
    def read(self, path):
        """ 
            Load data file
            
            @param path: file path
            @return: Data1D object, or None
            @raise RuntimeError: when the file can't be opened
            @raise ValueError: when the length of the data vectors are inconsistent
        """
        if os.path.isfile(path):
            basename  = os.path.basename(path)
            root, extension = os.path.splitext(basename)
            if extension.lower() in self.ext:
                try:
                    input_f =  open(path,'r')
                except :
                    raise  RuntimeError, "ascii_reader: cannot open %s" % path
                buff = input_f.read()
                lines = buff.split('\n')
                x  = numpy.zeros(0)
                y  = numpy.zeros(0)
                dy = numpy.zeros(0)
                dx = numpy.zeros(0)
                
               #temp. space to sort data
                tx  = numpy.zeros(0)
                ty  = numpy.zeros(0)
                tdy = numpy.zeros(0)
                tdx = numpy.zeros(0)
                
                output = Data1D(x, y, dy=dy, dx=dx)
                self.filename = output.filename = basename
           
                data_conv_q = None
                data_conv_i = None
                
                if has_converter == True and output.x_unit != '1/A':
                    data_conv_q = Converter('1/A')
                    # Test it
                    data_conv_q(1.0, output.x_unit)
                    
                if has_converter == True and output.y_unit != '1/cm':
                    data_conv_i = Converter('1/cm')
                    # Test it
                    data_conv_i(1.0, output.y_unit)
           
                
                # The first good line of data will define whether
                # we have 2-column or 3-column ascii
                has_error_dx = None
                has_error_dy = None
                
                for line in lines:
                    toks = line.split()
                    try:
                        _x = float(toks[0])
                        _y = float(toks[1])
                        
                        if data_conv_q is not None:
                            _x = data_conv_q(_x, units=output.x_unit)
                            
                        if data_conv_i is not None:
                            _y = data_conv_i(_y, units=output.y_unit)                        
                        
                        # If we have an extra token, check
                        # whether it can be interpreted as a
                        # third column.
                        _dy = None
                        if len(toks)>2:
                            try:
                                _dy = float(toks[2])
                                
                                if data_conv_i is not None:
                                    _dy = data_conv_i(_dy, units=output.y_unit)
                                
                            except:
                                # The third column is not a float, skip it.
                                pass
                            
                        # If we haven't set the 3rd column
                        # flag, set it now.
                        if has_error_dy == None:
                            has_error_dy = False if _dy == None else True
                            
                        #Check for dx
                        _dx = None
                        if len(toks)>3:
                            try:
                                _dx = float(toks[3])
                                
                                if data_conv_i is not None:
                                    _dx = data_conv_i(_dx, units=output.x_unit)
                                
                            except:
                                # The 4th column is not a float, skip it.
                                pass
                            
                        # If we haven't set the 3rd column
                        # flag, set it now.
                        if has_error_dx == None:
                            has_error_dx = False if _dx == None else True

                        x  = numpy.append(x,   _x) 
                        y  = numpy.append(y,   _y)
                        if has_error_dy == True:
                            dy = numpy.append(dy, _dy)
                        if has_error_dx == True:
                            dx = numpy.append(dx, _dx)
                            
                        #Same for temp.
                        tx  = numpy.append(tx,   _x) 
                        ty  = numpy.append(ty,   _y)
                        if has_error_dy == True:
                            tdy = numpy.append(tdy, _dy)
                        if has_error_dx == True:
                            tdx = numpy.append(tdx, _dx)
                        
                    except:
                        # Couldn't parse this line, skip it 
                        pass
                         
                     
                # Sanity check
                if has_error_dy == True and not len(y) == len(dy):
                    raise RuntimeError, "ascii_reader: y and dy have different length"
                if has_error_dx == True and not len(x) == len(dx):
                    raise RuntimeError, "ascii_reader: y and dy have different length"

                # If the data length is zero, consider this as
                # though we were not able to read the file.
                if len(x)==0:
                    raise RuntimeError, "ascii_reader: could not load file"
                
                #Let's reoder the data
                ind = numpy.lexsort((ty,tx))
                for i in ind:
                    x[i] = tx[ind[i]]
                    y[i] = ty[ind[i]]
                    if has_error_dy == True:
                        dy[i] = tdy[ind[i]]
                    if has_error_dx == True:
                        dx[i] = tdx[ind[i]]
                    
                output.x = x
                output.y = y
                output.dy = dy if has_error_dy == True else None
                output.dx = dx if has_error_dx == True else None
                
                if data_conv_q is not None:
                    output.xaxis("\\rm{Q}", output.x_unit)
                else:
                    output.xaxis("\\rm{Q}", 'A^{-1}')
                if data_conv_i is not None:
                    output.yaxis("\\{I(Q)}", output.y_unit)
                else:
                    output.yaxis("\\rm{I(Q)}","cm^{-1}")
                
                return output
        else:
            raise RuntimeError, "%s is not a file" % path
        return None
    
if __name__ == "__main__": 
    reader = Reader()
    #print reader.read("../test/test_3_columns.txt")
    print reader.read("../test/empty.txt")
    
    
                        