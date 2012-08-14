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

Module for abstracting out the concepts of a matrix and tiles.

@author: Balraja Subbiah
'''

from abc import ABCMeta, abstractmethod

class MatrixOperationError(Exception):pass

class Matrix(object):
    '''Defines the abstraction of a matrix of two dimension'''
    
    def __init__(self, rows, columns):
        ''' CTOR '''
        self._rows = rows
        self._columns = columns
    
    @property
    def rows(self):
        return self._rows
    
    @property
    def columns(self):
        return self._columns
    
    @property
    def dim(self):
        return (self._rows, self._columns)
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, new_data):
        self._data = new_data
    
    def __getitem__(self, idx_tuple):
        '''Adds index to matrix to get element at a given row and column '''
        return self.data[idx_tuple[0]][idx_tuple[1]]
    
    @property
    def indices(self):
        return [(i,j) for i in range(self.rows) for j in range(self.columns)]

class Tile(Matrix):
    '''
     A tile is a submatrix that can be loaded into memory, perform
     operations and value can be persisted.
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, rows, columns):
        ''' CTOR '''
        Matrix.__init__(self, rows, columns)
    
    def __getattribute__(self, attr):
        ''' Overrides this method to load the data if it's not 
        loaded already'''
        if (attr == 'data'):
            try:
                result = object.__getattribute__(self, attr)
                return result
            except AttributeError:
                self.data = self.load_data()
                return self.data
        else:
            return object.__getattribute__(self, attr)
    
    @abstractmethod
    def load_data(self):
        pass

class TileFactory(object):
    __metaclass__ = ABCMeta
     
    @abstractmethod
    def make_tile(self, i, j):
        pass

class TiledMatrix(Matrix):
    '''
    Defines the basic abstraction of a matrix whose elements 
    are composed of tiles.
    '''
    
    def __init__(self, rows, columns, tile_factory):
        '''
        Constructor
        '''
        Matrix.__init__(self, rows, columns)
        self.data = [[tile_factory.make_tile(i,j) \
                      for j in range(columns)] for i in range(rows)]
    
    def __str__(self):
        tmp = "\n";
        for (i,j) in self.indices:
            tmp = tmp + "\n %s,%s = \n %s"%(i,j,self[(i,j)])
        tmp = tmp + "\n"
        return tmp
        