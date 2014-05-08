# Copyright (c) 2012, GPy authors (see AUTHORS.txt).
# Licensed under the BSD 3-clause license (see LICENSE.txt)

__updated__ = '2014-04-15'

import numpy as np
from parameter_core import Observable, Pickleable

class ObsAr(np.ndarray, Pickleable, Observable):
    """
    An ndarray which reports changes to its observers.
    The observers can add themselves with a callable, which
    will be called every time this array changes. The callable
    takes exactly one argument, which is this array itself.
    """
    __array_priority__ = -1 # Never give back ObsAr
    def __new__(cls, input_array, *a, **kw):
        if not isinstance(input_array, ObsAr):
            obj = np.atleast_1d(np.require(input_array, dtype=np.float64, requirements=['W', 'C'])).view(cls)
        else: obj = input_array
        #cls.__name__ = "ObsAr" # because of fixed printing of `array` in np printing
        super(ObsAr, obj).__init__(*a, **kw)
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.observers = getattr(obj, 'observers', None)

    def __array_wrap__(self, out_arr, context=None):
        return out_arr.view(np.ndarray)

    def copy(self):
        memo = {}
        memo[id(self)] = self
        return self.__deepcopy__(memo)

    def __deepcopy__(self, memo):
        s = self.__new__(self.__class__, input_array=self.view(np.ndarray).copy())
        memo[id(self)] = s
        import copy
        s.__dict__.update(copy.deepcopy(self.__dict__, memo))
        return s

    def __reduce__(self):
        func, args, state = super(ObsAr, self).__reduce__()
        return func, args, (state, Pickleable.__getstate__(self))

    def __setstate__(self, state):
        np.ndarray.__setstate__(self, state[0])
        Pickleable.__setstate__(self, state[1])

    def __setitem__(self, s, val):
        super(ObsAr, self).__setitem__(s, val)
        self.notify_observers()

    def __getslice__(self, start, stop):
        return self.__getitem__(slice(start, stop))

    def __setslice__(self, start, stop, val):
        return self.__setitem__(slice(start, stop), val)

    def __ilshift__(self, *args, **kwargs):
        r = np.ndarray.__ilshift__(self, *args, **kwargs)
        self.notify_observers()
        return r

    def __irshift__(self, *args, **kwargs):
        r = np.ndarray.__irshift__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __ixor__(self, *args, **kwargs):
        r = np.ndarray.__ixor__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __ipow__(self, *args, **kwargs):
        r = np.ndarray.__ipow__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __ifloordiv__(self, *args, **kwargs):
        r = np.ndarray.__ifloordiv__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __isub__(self, *args, **kwargs):
        r = np.ndarray.__isub__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __ior__(self, *args, **kwargs):
        r = np.ndarray.__ior__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __itruediv__(self, *args, **kwargs):
        r = np.ndarray.__itruediv__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __idiv__(self, *args, **kwargs):
        r = np.ndarray.__idiv__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __iand__(self, *args, **kwargs):
        r = np.ndarray.__iand__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __imod__(self, *args, **kwargs):
        r = np.ndarray.__imod__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __iadd__(self, *args, **kwargs):
        r = np.ndarray.__iadd__(self, *args, **kwargs)
        self.notify_observers()
        return r


    def __imul__(self, *args, **kwargs):
        r = np.ndarray.__imul__(self, *args, **kwargs)
        self.notify_observers()
        return r
