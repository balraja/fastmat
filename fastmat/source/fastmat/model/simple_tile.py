'''
Created on Jul 28, 2012

@author: Balraja Subbiah
'''
from fastmat.model.executable import Persistor
from fastmat.model.matrix import Tile,TileFactory

import pickle

class SimpleTile(Tile):
    '''Extends the definition of tile to have data in memory'''
    
    def __init__(self, rows, columns, value):
        Tile.__init__(self, rows, columns)
        self._filling_value = value
    
    def load_data(self):
        return  [[self._filling_value for y in range(self.columns)] \
                     for x in range(self.rows)]

class SimpleTileFactory(TileFactory):
    '''
    Extends TileFactory to create tiles prepopulated with a 
    particular value 
    '''
    
    def __init__(self, rows, columns, value):
        self.rows=rows
        self.columns=columns
        self._value=value
    
    def make_tile(self, i, j):
        tile = SimpleTile(self.rows, self.columns, self._value)
        return tile

class SimpleTilePersistor(Persistor):
    '''Overides persistor to persist SimpleTile using pickle '''
    
    def save(self, filename, instance):
        f = open(filename, 'wb');
        pickle.dump(f, instance)
    
    def load(self, filename):
        f = open(filename, 'rb');
        return pickle.load(f)