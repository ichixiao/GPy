import sys
import numpy as np
import sympy as sym
from sympy import Function, S, oo, I, cos, sin, asin, log, erf, pi, exp, sqrt, sign, gamma, polygamma
from sympy.matrices import Matrix
from sympy.core import Derivative
########################################
## Try to do some matrix functions: problem, you can't do derivatives
## with respect to matrix functions :-(

class IndMatrix(Matrix, Function):
    def __init__(self, rows, cols, expressions, index=0, row_index=0, col_index=0):
        super(IndMatrix, self).__init__(expressions)
        self.row_var = row_index
        self.col_var = col_index
        self.index_var = index
    def fdiff(self, argindex=1):
        base = [sym.sympify(0)]*self.rows*self.cols
        base[argindex-1] = sym.sympify(1)
        return IndMatrix(self.rows, self.cols, base, index=self.index_var)
    def _format_str(self, printer=None):
        if not printer:
            from sympy.printing.str import StrPrinter
            printer = StrPrinter()
        # Handle zero dimensions:
        if self.rows == 0 or self.cols == 0:
            return 'IndMatrix(%s, %s, [])' % (self.rows, self.cols)
        if self.rows == 1:
            return "IndMatrix([%s])" % self.table(printer, rowsep=',\n')
        return "IndMatrix([\n%s])" % self.table(printer, rowsep=',\n')


        
    #@_sympifyit('other', NotImplemented)
    def __add__(self, other):
        if isinstance(other, Matrix):
            if other.rows==self.rows and other.rows==self.cols:
                base = [self[i, j] + other[i, j] for i in range(self.rows) for j in range[self.cols]]
                return IndMatrix(self.rows, self.cols, base, index=self.index_var)
        # if isinstance(other, Number):
        #     if other is S.NaN:
        #         return S.NaN
        #     elif other is S.Infinity:
        #         return S.Infinity
        #     elif other is S.NegativeInfinity:
        #         return S.NegativeInfinity
        # return AtomicExpr.__add__(self, other)

    def __str__(self):
        if self.rows == 0 or self.cols == 0:
            return 'IndMatrix(%s, %s, [])' % (self.rows, self.cols)
        return "IndMatrix(%s)" % str(self.tolist())

    def is_real(self):
        return True

    def atoms(self, *types):
        ex_list = [e2 for e in self for e2 in e.atoms(*types)]
        if hasattr(self, 'row_var') and self.row_var:
            if isinstance(self.row_var, sym.Expr):
                ex_list += [e for e in self.row_var.atoms(*types)]
        if hasattr(self, 'col_var') and self.col_var:
            if isinstance(self.col_var, sym.Expr):
                ex_list += [e for e in self.col_var.atoms(*types)]
        if hasattr(self, 'index_var') and self.index_var:
            if isinstance(self.index_var, sym.Expr):
                ex_list += [e for e in self.index_var.atoms(*types)]
        return ex_list

    @property
    def free_symbols(self):
        """Return from the atoms of self those which are free symbols.

        For most expressions, all symbols are free symbols. For some classes
        this is not true. e.g. Integrals use Symbols for the dummy variables
        which are bound variables, so Integral has a method to return all symbols
        except those. Derivative keeps track of symbols with respect to which it
        will perform a derivative; those are bound variables, too, so it has
        its own symbols method.

        Any other method that uses bound variables should implement a symbols
        method."""
        union = set.union
        return reduce(union, [e.free_symbols for e in self], set())

    @property
    def args(self):
        """Returns a tuple of arguments of 'self'.
        """
        return [e for e in self]

    def diff(self, *args):
        return self._new(self.rows, self.cols,
                         lambda i, j: self[i, j].diff(*args))

    def sum(self):
        result = 0
        for e in self:
            result+=e
        return result

    def prod(self):
        result = 1
        for e in self:
            result*=e
        return result

    def expressions(self):
        return [expr for expr in self]

def create_matrix(name, rows, cols):
    """A helper function for creating a matrix based on numbered symbols."""
    if rows==1:
        X = IndMatrix(rows, cols, sym.symbols(name.lower() + '_:' + str(cols)))
    elif cols==1:
        X = IndMatrix(rows, cols, sym.symbols(name.lower() + '_:' + str(rows)))
    else:
        X = IndMatrix(rows, cols, sym.symbols(name.lower() + '_:' + str(rows) + '\,:' + str(cols)))
    return X

class selector(Function):
    """A function that returns an element of a Matrix depending on input indices."""
    nargs = 3
    def fdiff(self, argindex=1):
        return selector(*self.args)
    @classmethod
    def eval(cls, X, i, j):
        if i.is_Number and j.is_Number:
            return X[i, j]
        
##################################################    
class logistic(Function):
    """The logistic function as a symbolic function."""
    nargs = 1
    def fdiff(self, argindex=1):
        x = self.args[0]
        return logistic(x)*(1-logistic(x))

    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return 1/(1+exp(-x))
    
class logisticln(Function):
    """The log logistic, which can often be computed with more precision than the simply taking log(logistic(x)) when x is small or large."""
    nargs = 1

    def fdiff(self, argindex=1):
        x = self.args[0]
        return 1-logistic(x)

    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return -np.log(1+exp(-x))

class erfc(Function):
    """The complementary error function, erfc(x) = 1-erf(x). Used as a helper function, particularly for erfcx, the scaled complementary error function. and the normal distributions cdf."""
    nargs = 1
    
    @classmethod
    def eval(cls, arg):
        return 1-erf(arg)

class erfcx(Function):
    nargs = 1
    def fdiff(self, argindex=1):
        x = self.args[0]
        return x*erfcx(x)-2/sqrt(pi)
        
    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return exp(x**2)*erfc(x)

class gammaln(Function):
    """The log of the gamma function, which is often needed instead of log(gamma(x)) for better accuracy for large x."""
    nargs = 1

    def fdiff(self, argindex=1):
        x=self.args[0]
        return polygamma(0, x)

    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return log(gamma(x))
    

class normcdfln(Function):
    """The log of the normal cdf. Can often be computed with better accuracy than log(normcdf(x)), particulary when x is either small or large."""
    nargs = 1

    def fdiff(self, argindex=1):
        x = self.args[0]
        #return -erfcx(-x/sqrt(2))/sqrt(2*pi)
        #return exp(-normcdfln(x) - 0.5*x*x)/sqrt(2*pi)
        return sqrt(2/pi)*1/erfcx(-x/sqrt(2))

    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return log(normcdf(x))

    def _eval_is_real(self):
        return self.args[0].is_real

class normcdf(Function):
    """The cumulative distribution function of the standard normal. Provided as a convenient helper function. It is computed throught -0.5*erfc(-x/sqrt(2))."""
    nargs = 1
    def fdiff(self, argindex=1):
        x = self.args[0]
        return normal(x)

    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return 0.5*(erfc(-x/sqrt(2)))

    def _eval_is_real(self):
        return self.args[0].is_real

class normalln(Function):
    """The log of the standard normal distribution."""
    nargs = 1
    def fdiff(self, argindex=1):
         x = self.args[0]
         return -x
     
    @classmethod
    def eval(cls, x):
        if x.is_Number:
            return 0.5*sqrt(2*pi) - 0.5*x*x


    def _eval_is_real(self):
        return True


class normal(Function):
    """The standard normal distribution. Provided as a convenience function."""
    nargs = 1
    @classmethod
    def eval(cls, x):
        return 1/sqrt(2*pi)*exp(-0.5*x*x)

    def _eval_is_real(self):
        return True

class differfln(Function):
    nargs = 2

    def fdiff(self, argindex=2):
        if argindex == 2:
            x0, x1 = self.args
            return -2/(sqrt(pi)*(erfcx(x1)-exp(x1**2-x0**2)*erfcx(x0)))
        elif argindex == 1:
            x0, x1 = self.args
            return 2/(sqrt(pi)*(exp(x0**2-x1**2)*erfcx(x1)-erfcx(x0)))
        else:
            raise ArgumentIndexError(self, argindex)
        
    @classmethod
    def eval(cls, x0, x1):
        if x0.is_Number and x1.is_Number:            
            return log(erfc(x1)-erfc(x0))

class dh_dd_i(Function):
    nargs = 5
    @classmethod
    def eval(cls, t, tprime, d_i, d_j, l):
        if (t.is_Number
            and tprime.is_Number
            and d_i.is_Number
            and d_j.is_Number
            and l.is_Number):

            diff_t = (t-tprime)
            l2 = l*l
            h = h(t, tprime, d_i, d_j, l)
            half_l_di = 0.5*l*d_i
            arg_1 = half_l_di + tprime/l
            arg_2 = half_l_di - (t-tprime)/l
            ln_part_1 = ln_diff_erf(arg_1, arg_2)
            arg_1 = half_l_di 
            arg_2 = half_l_di - t/l
            sign_val = sign(t/l)
            ln_part_2 = ln_diff_erf(half_l_di, half_l_di - t/l)

            base = ((0.5*d_i*l2*(d_i+d_j)-1)*h 
                    + (-diff_t*sign_val*exp(half_l_di*half_l_di
                                          -d_i*diff_t
                                          +ln_part_1)
                       +t*sign_val*exp(half_l_di*half_l_di
                                          -d_i*t-d_j*tprime
                                          +ln_part_2))
                    + l/sqrt(pi)*(-exp(-diff_t*diff_t/l2)
                                     +exp(-tprime*tprime/l2-d_i*t)
                                     +exp(-t*t/l2-d_j*tprime)
                                     -exp(-(d_i*t + d_j*tprime))))
            return base/(d_i+d_j)

class dh_dd_j(Function):
    nargs = 5
    @classmethod
    def eval(cls, t, tprime, d_i, d_j, l):
        if (t.is_Number
            and tprime.is_Number
            and d_i.is_Number
            and d_j.is_Number
            and l.is_Number):
            diff_t = (t-tprime)
            l2 = l*l
            half_l_di = 0.5*l*d_i
            h = h(t, tprime, d_i, d_j, l)
            arg_1 = half_l_di + tprime/l
            arg_2 = half_l_di - (t-tprime)/l
            ln_part_1 = ln_diff_erf(arg_1, arg_2)
            arg_1 = half_l_di 
            arg_2 = half_l_di - t/l
            sign_val = sign(t/l)
            ln_part_2 = ln_diff_erf(half_l_di, half_l_di - t/l)
            sign_val = sign(t/l)
            base = tprime*sign_val*exp(half_l_di*half_l_di-(d_i*t+d_j*tprime)+ln_part_2)-h
            return base/(d_i+d_j)
    
class dh_dl(Function):
    nargs = 5
    @classmethod
    def eval(cls, t, tprime, d_i, d_j, l):
        if (t.is_Number
            and tprime.is_Number
            and d_i.is_Number
            and d_j.is_Number
            and l.is_Number):

            diff_t = (t-tprime)
            l2 = l*l
            h = h(t, tprime, d_i, d_j, l)
            return 0.5*d_i*d_i*l*h + 2./(sqrt(pi)*(d_i+d_j))*((-diff_t/l2-d_i/2.)*exp(-diff_t*diff_t/l2)+(-tprime/l2+d_i/2.)*exp(-tprime*tprime/l2-d_i*t)-(-t/l2-d_i/2.)*exp(-t*t/l2-d_j*tprime)-d_i/2.*exp(-(d_i*t+d_j*tprime)))

class dh_dt(Function):
    nargs = 5
    @classmethod
    def eval(cls, t, tprime, d_i, d_j, l):
        if (t.is_Number
            and tprime.is_Number
            and d_i.is_Number
            and d_j.is_Number
            and l.is_Number):
            if (t is S.NaN
                or tprime is S.NaN
                or d_i is S.NaN
                or d_j is S.NaN
                or l is S.NaN):
                return S.NaN
            else:
                half_l_di = 0.5*l*d_i
                arg_1 = half_l_di + tprime/l
                arg_2 = half_l_di - (t-tprime)/l
                ln_part_1 = ln_diff_erf(arg_1, arg_2)
                arg_1 = half_l_di 
                arg_2 = half_l_di - t/l
                sign_val = sign(t/l)
                ln_part_2 = ln_diff_erf(half_l_di, half_l_di - t/l)

                
                return (sign_val*exp(half_l_di*half_l_di
                                        - d_i*(t-tprime)
                                        + ln_part_1
                                        - log(d_i + d_j))
                        - sign_val*exp(half_l_di*half_l_di
                                          - d_i*t - d_j*tprime
                                          + ln_part_2
                                          - log(d_i + d_j))).diff(t)

class dh_dtprime(Function):
    nargs = 5
    @classmethod
    def eval(cls, t, tprime, d_i, d_j, l):
        if (t.is_Number
            and tprime.is_Number
            and d_i.is_Number
            and d_j.is_Number
            and l.is_Number):
            if (t is S.NaN
                or tprime is S.NaN
                or d_i is S.NaN
                or d_j is S.NaN
                or l is S.NaN):
                return S.NaN
            else:
                half_l_di = 0.5*l*d_i
                arg_1 = half_l_di + tprime/l
                arg_2 = half_l_di - (t-tprime)/l
                ln_part_1 = ln_diff_erf(arg_1, arg_2)
                arg_1 = half_l_di 
                arg_2 = half_l_di - t/l
                sign_val = sign(t/l)
                ln_part_2 = ln_diff_erf(half_l_di, half_l_di - t/l)

                
                return (sign_val*exp(half_l_di*half_l_di
                                        - d_i*(t-tprime)
                                        + ln_part_1
                                        - log(d_i + d_j))
                        - sign_val*exp(half_l_di*half_l_di
                                          - d_i*t - d_j*tprime
                                          + ln_part_2
                                          - log(d_i + d_j))).diff(tprime)


class h(Function):
    nargs = 5
    def fdiff(self, argindex=5):
        t, tprime, d_i, d_j, l = self.args
        if argindex == 1:
            return dh_dt(t, tprime, d_i, d_j, l)
        elif argindex == 2:
            return dh_dtprime(t, tprime, d_i, d_j, l)
        elif argindex == 3:
            return dh_dd_i(t, tprime, d_i, d_j, l)
        elif argindex == 4:
            return dh_dd_j(t, tprime, d_i, d_j, l)
        elif argindex == 5:
            return dh_dl(t, tprime, d_i, d_j, l)
                                                                
    
    @classmethod
    def eval(cls, t, tprime, d_i, d_j, l):
        if (t.is_Number
            and tprime.is_Number
            and d_i.is_Number
            and d_j.is_Number
            and l.is_Number):
            if (t is S.NaN
                or tprime is S.NaN
                or d_i is S.NaN
                or d_j is S.NaN
                or l is S.NaN):
                return S.NaN
            else:
                half_l_di = 0.5*l*d_i
                arg_1 = half_l_di + tprime/l
                arg_2 = half_l_di - (t-tprime)/l
                ln_part_1 = ln_diff_erf(arg_1, arg_2)
                arg_1 = half_l_di 
                arg_2 = half_l_di - t/l
                sign_val = sign(t/l)
                ln_part_2 = ln_diff_erf(half_l_di, half_l_di - t/l)

                
                return (sign_val*exp(half_l_di*half_l_di
                                        - d_i*(t-tprime)
                                        + ln_part_1
                                        - log(d_i + d_j))
                        - sign_val*exp(half_l_di*half_l_di
                                          - d_i*t - d_j*tprime
                                          + ln_part_2
                                          - log(d_i + d_j)))
            
                                  
                # return (exp((d_j/2.*l)**2)/(d_i+d_j)
                #         *(exp(-d_j*(tprime - t))
                #           *(erf((tprime-t)/l - d_j/2.*l)
                #             + erf(t/l + d_j/2.*l))
                #           - exp(-(d_j*tprime + d_i))
                #           *(erf(tprime/l - d_j/2.*l)
                #             + erf(d_j/2.*l))))



