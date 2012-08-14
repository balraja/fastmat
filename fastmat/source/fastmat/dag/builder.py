'''
Defines the basic constructs for building a graph
for execution.

@author: Balraja Subbiah
'''

from fastmat.model.executable import Executable, PersistedArgument
from fastmat.model.graph import Edge
from fastmat.model.matrix import TileFactory,TiledMatrix

import os.path

class GraphBuilderException(Exception): pass

def tile_addition(arg1, arg2):
    ''' A simple function to add the arguments '''
    return arg1 + arg2

def tile_multiplication(arg1, arg2):
    '''A simple function to multiply the arguments '''
    return arg1 * arg2

def tile_assignment(arg1, arg2):
    arg1.data = arg2.data
    return arg1;

class Vertex(object):
    ''' Defines the basic abstraction of a vertex '''
    
    def __init__(self, vertex_id, result):
        self._vertex_id = vertex_id
        self._result = result
    
    @property
    def vertex_id(self):
        return self._vertex_id
    
    @property
    def result(self):
        return self._result
    
    def __hash__(self):
        return hash(self.vertex_id)
    
    def __eq__(self,other):
        return self.vertex_id == other.vertex_id
    
    def __repr__(self):
        return self.vertex_id

class SourceVertex(Vertex):
    '''Abstracts out a vertex in the graph where the data is already available'''
    
    def __init__(self, vertex_id, tile):
        Vertex.__init__(self, vertex_id, tile)
        self._tile = tile
        
    @property
    def tile(self):
        return self._tile

class ExecutableVertex(Vertex):
    ''' 
    Defines the concept of executable vertex. A vertex that's holds the 
    executable operation.
    '''
    
    def __init__(self, vertex_id, executable, result):
        '''CTOR'''
        Vertex.__init__(self, vertex_id, result)
        self._executable = executable
    
    @property
    def executable(self):
        return self._executable

class WrappedTileFactory(TileFactory):
    '''Extends TileFactory to return WrappedTile when populating the matrix'''
    
    def __init__(self,tile_map):
        self._tile_map = tile_map
    
    def make_tile(self, i, j):
        return self._tile_map[(i,j)]
    
class GraphBuilder(object):
    ''' Class that acts as a builder for dag '''
    
    def __init__(self, graph, persistor, run_dir):
        self._graph = graph
        self._persistor = persistor
        self._run_dir = run_dir
        self._mat_index = {}

    @property
    def graph(self):
        return self._graph
    
    @property
    def persistor(self):
        return self._persistor
    
    @property
    def run_dir(self):
        return self._run_dir
    
    def matrix(self, name):
        return self._mat_index.get(name, None)
    
    def add_src_matrix(self, matrix, name):
        ''' 
        Wraps a source matrix with a new matrix that returns WrappedTIles
        that supports graph building
        '''
        if not isinstance(matrix, TiledMatrix):
            raise GraphBuilderException("Expected TiledMatrix but got " + 
                                        matrix.__class__.__name__)
        else:
            wrapped_tiles = {}
            for (i,j) in matrix.indices:
                vertex_id = name + " _"  + str(i) + "," + str(j)
                src_vertex = SourceVertex(vertex_id, matrix[(i,j)])
                self.graph + src_vertex
                wrapped_tiles[(i,j)] =\
                    WrappedTile(name, i, j, matrix[(i,j)], self, src_vertex)
            result = TiledMatrix(matrix.rows, matrix.columns,\
                                WrappedTileFactory(wrapped_tiles))
            self._mat_index[name] = result
            return result

class WrappedTile(object):
    ''' 
    A simple class that wraps the tile object to be used for building the
    graph. It translates the operations performed between the tiles as 
    edges on the graph.
    '''
    def __init__(self, matrix_name, row_idx, col_idx, tile,\
                 graph_builder, vertex):
        ''' CTOR '''
        self._matrix_name = matrix_name
        self._row_idx = row_idx
        self._col_idx = col_idx
        self._tile = tile
        self._graph_builder = graph_builder
        self._vertex = vertex
        self._assign_count = 0
    
    @property
    def matrix_name(self):
        return self._matrix_name
    
    @property
    def row_idx(self):
        return self._row_idx
    
    @property
    def col_idx(self):
        return self._col_idx
    
    @property
    def tile(self):
        if isinstance(self._tyle, PersistedArgument):
            self._tyle = self._tyle.load_arg()
        return self._tile
    
    @property
    def graph_builder(self):
        return self._graph_builder
    
    @property
    def vertex(self):
        return self._vertex
    
    @property
    def assign_count(self):
        return self._assign_count
    
    @assign_count.setter
    def assign_count(self, value):
        self._assign_count = value
    
    def __mul__(self, other):
        
        vertex_id =\
           self.matrix_name + "_" + str(self.row_idx) + "," \
           + str(self.col_idx) + "_ mult_ "\
           + other.matrix_name + "_" + str(other.row_idx)\
           + ","  + str(other.col_idx)
            
        file_name = os.path.join(self.graph_builder.run_dir, vertex_id)
        
        executable = Executable(self.graph_builder.persistor,
                                file_name,
                                tile_multiplication, 
                                self.vertex.result, 
                                other.vertex.result)
        execution_result =\
            PersistedArgument(self.graph_builder.persistor, file_name)
        vertex = ExecutableVertex(vertex_id, executable, execution_result)
        self._graph_builder.graph + Edge(self.vertex, vertex)
        self._graph_builder.graph + Edge(other.vertex, vertex)
        result = WrappedTile("Intermediate mult" + self.matrix_name + " "\
                             + other.matrix_name, 
                             self.row_idx,
                             self.col_idx, 
                             None, 
                             self.graph_builder, 
                             vertex)
        return result
    
    def __add__(self, other):
        
        vertex_id =\
           self.matrix_name + "_" + str(self.row_idx) + "," \
           + str(self.col_idx) + "_ add_ "\
           + other.matrix_name + "_" + str(other.row_idx)\
            + ","  + str(other.col_idx)
            
        file_name = os.path.join(self.graph_builder.run_dir, vertex_id)
        executable = Executable(self.graph_builder.persistor,\
                                file_name,
                                tile_addition, 
                                self.vertex.result, 
                                other.vertex.result)
        execution_result =\
            PersistedArgument(self.graph_builder.persistor, file_name)
        vertex = ExecutableVertex(vertex_id, executable, execution_result)
        self._graph_builder.graph + Edge(self.vertex, vertex)
        self._graph_builder.graph + Edge(other.vertex, vertex)
        result = WrappedTile("Intermediate add" + self.matrix_name + " "\
                             + other.matrix_name, 
                             self.row_idx,
                             self.col_idx, 
                             None, 
                             self.graph_builder, 
                             vertex)
        return result
     
    def assign(self, other):
        assign_cnt = self.assign_count + 1
        
        vertex_id =\
               self.matrix_name + "_" + str(self.row_idx) + ","\
                + str(self.col_idx) + "_" + str(assign_cnt)
                
        file_name = os.path.join(self.graph_builder.run_dir, vertex_id)
        
        execution_result =\
            PersistedArgument(self.graph_builder.persistor, file_name)
            
        executable = Executable(self.graph_builder.persistor,\
                                file_name,\
                                tile_assignment, 
                                self.vertex.result, 
                                other.vertex.result)
        
        vertex = ExecutableVertex(vertex_id, executable, execution_result)
        self._graph_builder.graph + Edge(other.vertex, vertex)
        result = WrappedTile(self.matrix_name, 
                             self.row_idx,
                             self.col_idx, 
                             execution_result,
                             self.graph_builder, 
                             vertex)
        result.assign_count = assign_cnt
        self.graph_builder.matrix(self.matrix_name).data[self.row_idx][self.col_idx] = result
    
if __name__ == '__main__':
    pass