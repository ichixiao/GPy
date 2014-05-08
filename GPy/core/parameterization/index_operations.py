'''
Created on Oct 2, 2013

@author: maxzwiessele
'''
import numpy
from numpy.lib.function_base import vectorize
from lists_and_dicts import IntArrayDict

class ParameterIndexOperations(object):
    '''
    Index operations for storing param index _properties
    This class enables index with slices retrieved from object.__getitem__ calls.
    Adding an index will add the selected indexes by the slice of an indexarray
    indexing a shape shaped array to the flattened index array. Remove will
    remove the selected slice indices from the flattened array.
    You can give an offset to set an offset for the given indices in the
    index array, for multi-param handling.
    '''
    _offset = 0
    def __init__(self, constraints=None):
        self._properties = IntArrayDict()
        if constraints is not None:
            for t, i in constraints.iteritems():
                self.add(t, i)

    def iteritems(self):
        return self._properties.iteritems()

    def items(self):
        return self._properties.items()

    def properties(self):
        return self._properties.keys()

    def iterproperties(self):
        return self._properties.iterkeys()

    def shift_right(self, start, size):
        for ind in self.iterindices():
            toshift = ind>=start
            ind[toshift] += size

    def shift_left(self, start, size):
        for v, ind in self.items():
            todelete = (ind>=start) * (ind<start+size)
            if todelete.size != 0:
                ind = ind[~todelete]
            toshift = ind>=start
            if toshift.size != 0:
                ind[toshift] -= size
            if ind.size != 0: self._properties[v] = ind
            else: del self._properties[v]

    def clear(self):
        self._properties.clear()

    @property
    def size(self):
        return reduce(lambda a,b: a+b.size, self.iterindices(), 0)

    def iterindices(self):
        return self._properties.itervalues()

    def indices(self):
        return self._properties.values()

    def properties_for(self, index):
        return vectorize(lambda i: [prop for prop in self.iterproperties() if i in self[prop]], otypes=[list])(index)

    def add(self, prop, indices):
        self._properties[prop] = combine_indices(self._properties[prop], indices)

    def remove(self, prop, indices):
        if prop in self._properties:
            diff = remove_indices(self[prop], indices)
            removed = numpy.intersect1d(self[prop], indices, True)
            if not index_empty(diff):
                self._properties[prop] = diff
            else:
                del self._properties[prop]
            return removed.astype(int)
        return numpy.array([]).astype(int)

    def update(self, parameter_index_view, offset=0):
        for i, v in parameter_index_view.iteritems():
            self.add(i, v+offset)

    def copy(self):
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo):
        return ParameterIndexOperations(dict(self.iteritems()))

    def __getitem__(self, prop):
        return self._properties[prop]

    def __delitem__(self, prop):
        del self._properties[prop]

    def __str__(self, *args, **kwargs):
        import pprint
        return pprint.pformat(dict(self._properties))

def combine_indices(arr1, arr2):
    return numpy.union1d(arr1, arr2)

def remove_indices(arr, to_remove):
    return numpy.setdiff1d(arr, to_remove, True)

def index_empty(index):
    return numpy.size(index) == 0

class ParameterIndexOperationsView(object):
    def __init__(self, param_index_operations, offset, size):
        self._param_index_ops = param_index_operations
        self._offset = offset
        self._size = size

    def __getstate__(self):
        return [self._param_index_ops, self._offset, self._size]

    def __setstate__(self, state):
        self._param_index_ops = state[0]
        self._offset = state[1]
        self._size = state[2]

    def _filter_index(self, ind):
        return ind[(ind >= self._offset) * (ind < (self._offset + self._size))] - self._offset


    def iteritems(self):
        for i, ind in self._param_index_ops.iteritems():
            ind2 = self._filter_index(ind)
            if ind2.size > 0:
                yield i, ind2

    def items(self):
        return [[i,v] for i,v in self.iteritems()]

    def properties(self):
        return [i for i in self.iterproperties()]


    def iterproperties(self):
        for i, _ in self.iteritems():
            yield i


    def shift_right(self, start, size):
        self._param_index_ops.shift_right(start+self._offset, size)

    def shift_left(self, start, size):
        self._param_index_ops.shift_left(start+self._offset, size)
        self._offset -= size
        self._size -= size

    def clear(self):
        for i, ind in self.items():
            self._param_index_ops.remove(i, ind+self._offset)

    @property
    def size(self):
        return reduce(lambda a,b: a+b.size, self.iterindices(), 0)


    def iterindices(self):
        for _, ind in self.iteritems():
            yield ind


    def indices(self):
        return [ind for ind in self.iterindices()]


    def properties_for(self, index):
        return vectorize(lambda i: [prop for prop in self.iterproperties() if i in self[prop]], otypes=[list])(index)


    def add(self, prop, indices):
        self._param_index_ops.add(prop, indices+self._offset)


    def remove(self, prop, indices):
        removed = self._param_index_ops.remove(prop, numpy.array(indices)+self._offset)
        if removed.size > 0:
            return removed-self._offset
        return removed


    def __getitem__(self, prop):
        ind = self._filter_index(self._param_index_ops[prop])
        return ind

    def __delitem__(self, prop):
        self.remove(prop, self[prop])

    def __str__(self, *args, **kwargs):
        import pprint
        return pprint.pformat(dict(self.iteritems()))

    def update(self, parameter_index_view, offset=0):
        for i, v in parameter_index_view.iteritems():
            self.add(i, v+offset)


    def copy(self):
        return self.__deepcopy__(None)

    def __deepcopy__(self, memo):
        return ParameterIndexOperations(dict(self.iteritems()))
    pass

