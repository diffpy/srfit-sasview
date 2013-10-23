import math
import numpy
import copy
from sans.pr.invertor import Invertor


class Num_terms():
    """
    """
    def __init__(self, invertor):
        """
        """
        self.invertor = invertor
        self.nterm_min = 10
        self.nterm_max = len(self.invertor.x)
        if self.nterm_max > 50:
            self.nterm_max = 50
        self.isquit_func = None
         
        self.osc_list = []
        self.err_list = []
        self.alpha_list = []
        self.mess_list = []
         
        self.dataset = []
     
    def is_odd(self, n):
        """
        """
        return bool(n % 2)

    def sort_osc(self):
        """
        """
        #import copy
        osc = copy.deepcopy(self.dataset)
        lis = []
        for i in range(len(osc)):
            osc.sort()
            re = osc.pop(0)
            lis.append(re)
        return lis
           
    def median_osc(self):
        """
        """
        osc = self.sort_osc()
        dv = len(osc)
        med = float(dv) / 2.0
        odd = self.is_odd(dv)
        medi = 0
        for i in range(dv):
            if odd == True:
                medi = osc[int(med)]
            else:
                medi = osc[int(med) - 1]
        return medi

    def get0_out(self):
        """
        """
        inver = self.invertor
        self.osc_list = []
        self.err_list = []
        self.alpha_list = []
        for k in range(self.nterm_min, self.nterm_max, 1):
            if self.isquit_func != None:
                self.isquit_func()
            best_alpha, message, _ = inver.estimate_alpha(k)
            inver.alpha = best_alpha
            inver.out, inver.cov = inver.lstsq(k)
            osc = inver.oscillations(inver.out)
            err = inver.get_pos_err(inver.out, inver.cov)
            if osc > 10.0:
                break
            self.osc_list.append(osc)
            self.err_list.append(err)
            self.alpha_list.append(inver.alpha)
            self.mess_list.append(message)
         
        new_osc1 = []
        new_osc2 = []
        new_osc3 = []
        flag9 = False
        flag8 = False
        flag7 = False
        for i in range(len(self.err_list)):
            if self.err_list[i] <= 1.0 and self.err_list[i] >= 0.9:
                new_osc1.append(self.osc_list[i])
                flag9 = True
            if self.err_list[i] < 0.9 and self.err_list[i] >= 0.8:
                new_osc2.append(self.osc_list[i])
                flag8 = True
            if self.err_list[i] < 0.8 and self.err_list[i] >= 0.7:
                new_osc3.append(self.osc_list[i])
                flag7 = True
                 
        if flag9 == True:
            self.dataset = new_osc1
        elif flag8 == True:
            self.dataset = new_osc2
        else:
            self.dataset = new_osc3
         
        return self.dataset
        
    def ls_osc(self):
        """
        """
        # Generate data
        ls_osc = self.get0_out()
        med = self.median_osc()
        
        #TODO: check 1
        ls_osc = self.dataset
        ls = []
        for i in range(len(ls_osc)):
            if int(med) == int(ls_osc[i]):
                ls.append(ls_osc[i])
        return ls

    def compare_err(self):
        """
        """
        ls = self.ls_osc()
        #print "ls", ls
        nt_ls = []
        for i in range(len(ls)):
            r = ls[i]
            n = self.osc_list.index(r) + 10
            #er = self.err_list[n]
            #nt = self.osc_list.index(r) + 10
            nt_ls.append(n)
        #print "nt list", nt_ls
        return nt_ls

    def num_terms(self, isquit_func=None):
        """
        """
        try:
            self.isquit_func = isquit_func
            nts = self.compare_err()
            div = len(nts)
            tem = float(div)/2.0
            odd = self.is_odd(div)
            if odd == True:
                nt = nts[int(tem)]
            else:
                nt = nts[int(tem) - 1]
            return nt, self.alpha_list[nt - 10], self.mess_list[nt-10]
        except:
            return self.nterm_min, self.alpha_list[10], self.mess_list[10]


#For testing
def load(path):
    # Read the data from the data file
    data_x   = numpy.zeros(0)
    data_y   = numpy.zeros(0)
    data_err = numpy.zeros(0)
    scale    = None
    min_err  = 0.0
    if not path == None:
        input_f = open(path,'r')
        buff    = input_f.read()
        lines   = buff.split('\n')
        for line in lines:
            try:
                toks = line.split()
                test_x = float(toks[0])
                test_y = float(toks[1])
                if len(toks) > 2:
                    err = float(toks[2])
                else:
                    if scale == None:
                        scale = 0.05 * math.sqrt(test_y)
                        #scale = 0.05/math.sqrt(y)
                        min_err = 0.01 * y
                    err = scale * math.sqrt(test_y) + min_err
                    #err = 0
                    
                data_x = numpy.append(data_x, test_x)
                data_y = numpy.append(data_y, test_y)
                data_err = numpy.append(data_err, err)
            except:
                pass
               
    return data_x, data_y, data_err


if __name__ == "__main__":
    i = Invertor()
    x, y, erro = load("test/Cyl_A_D102.txt")
    i.d_max = 102.0
    i.nfunc = 10
    #i.q_max = 0.4
    #i.q_min = 0.07
    i.x = x
    i.y = y
    i.err = erro
    #i.out, i.cov = i.lstsq(10)
    # Testing estimator
    est = Num_terms(i)
    print est.num_terms()
