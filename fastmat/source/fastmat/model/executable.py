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

This module captures the executable parts of the system

@author: Balraja Subbiah
'''
from abc import ABCMeta, abstractmethod 

class Persistor(object):
    '''
    Defines the abstraction for persisting tile to a file 
    and restoring the same
    ''' 
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def save(self, filename, instance):
        pass
    
    @abstractmethod
    def load(self, filename):
        pass

class PersistedArgument(object):
    '''
    Defines the concept of an argument that can be shipped to the remote host.
    '''
    __metaclass__ = ABCMeta
    
    def __init__(self, persistor, file_name):
        '''CTOR'''
        self._persistor = persistor
        self._file_name = file_name
    
    def load_arg(self):
        '''loads the argument from the file using persistor'''
        return self._persistor.load(self._file_name)

class Executable(object):
    '''
    Defines the concept of executable that can be shipped to a remove vertex
    and executed there.
    '''

    def __init__(self, persistor, file_name, function, *args):
        '''
        CTOR
        '''
        self._function = function
        self._args = args
        self._file_name = file_name
        self._persistor = persistor
    
    def execute(self):
        '''
        A helper method to execute the function in a vertex and saves the 
        result to file
        '''
        args = [x.load_arg() if isinstance(x, PersistedArgument) else x \
                for x in self._args]
        result = self._function(*args)
        self._persistor.save(self._file_name, result)
