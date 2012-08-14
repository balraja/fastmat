'''
Module for testing fastmat

Created on Jul 28, 2012

@author: dell
'''

from multiprocessing import Process

from fastmat.dag.builder import GraphBuilder,unwrap_matrix
from fastmat.distribute.task_executor import master,worker
from fastmat.model.graph import Graph
from fastmat.model.matrix import TiledMatrix
from fastmat.model.numpy_tile import NumpyTileFactory,NumpyTilePersistor

if __name__ == '__main__':
    g = Graph()
    graph_builder = GraphBuilder(g, NumpyTilePersistor(), "C://tmp")
    A = TiledMatrix(4, 4, NumpyTileFactory(100,100,1))
    B = TiledMatrix(4, 4, NumpyTileFactory(100,100,2))
    C = TiledMatrix(4, 4, NumpyTileFactory(100,100,0))
    
    A = graph_builder.add_src_matrix(A, "A")
    B = graph_builder.add_src_matrix(B, "B")
    C = graph_builder.add_src_matrix(C, "C")
    
    # Builds graph for performing matrix multiplication
    for i in range(A.rows): 
        for j in range(B.columns):
            for k in range(A.columns):
                C[(i,j)].assign(C[(i,j)] + (A[(i,k)] * B[(k,j)]))
    
    
    # Now we span workers to execute the graph.
    worker_pool = range(1,3)
    for wrk_num in range(len(worker_pool)):
        Process(target=worker, args=(wrk_num,)).start()
    
    # Start the master that controls the execution.
    master(g)
    
    #Unwrap the result after execution completion.
    result = unwrap_matrix(C)
    print result
    
    