'''
#################################################################
Copyright (C) 2012  Balraja Subbiah

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
#####################################################################

THis module contains classes tha model a tile as numpy array

@author: Balraja Subbiah
'''

from fastmat.model.executable import Persistor
from fastmat.model.matrix import Tile,TileFactory

import numpy as np

import pickle

class TileException(Exception):
    pass

class NumpyTile(Tile):
    '''Extends the definition of tile to have data in memory'''
    
    def __init__(self, rows, columns, array):
        Tile.__init__(self, rows, columns)
        self.data = array
    
    def load_data(self):
        return None
    
    def __mul__(self, other):
        if not isinstance(other, NumpyTile):
            raise TileException
        result = self.data.dot(other.data)
        return NumpyTile(result.shape[0], result.shape[1], result)
    
    def __add__(self, other):
        if not isinstance(other, NumpyTile):
            raise TileException
        result = self.data + other.data
        return NumpyTile(result.shape[0], result.shape[1], result)

    def __str__(self):
        return self.data.__repr__()
    
class NumpyTileFactory(TileFactory):
    '''
    Extends TileFactory to create tiles prepopulated with a 
    particular value 
    '''
    
    def __init__(self, rows, columns, value):
        self.rows=rows
        self.columns=columns
        self._value=value
    
    def make_tile(self, i, j):
        data = np.empty(shape=[self.rows, self.columns])
        data.fill(self._value)
        tile = NumpyTile(self.rows, self.columns, data)
        return tile

class NumpyTilePersistor(Persistor):
    '''Overides persistor to persist SimpleTile using pickle '''
    
    def save(self, filename, instance):
        f = open(filename, "wb")
        instance.data.dump(f)
    
    def load(self, filename):
        f = file(filename, "rb")
        result = pickle.load(f)
        return NumpyTile(result.shape[0], result.shape[1], result)

if __name__ == '__main__':
    
    factory = NumpyTileFactory(3, 3, 3)
    a = factory.make_tile(1,1)
    print a.data
    
    b = factory.make_tile(1,1)
    print b.data
    
    c = a * b
    print c.data
    
    e = a + b
    print e.data
    
    p = NumpyTilePersistor()
    p.save("C:\\tmp\\numpytest", c);
    d = p.load("C:\\tmp\\numpytest")
    print d.data
    
    