'''
Module for testing fastmat

Created on Jul 28, 2012

@author: dell
'''

from multiprocessing import Process

from fastmat.dag.builder import GraphBuilder
from fastmat.distribute.task_executor import master,worker
from fastmat.model.graph import Graph
from fastmat.model.matrix import TiledMatrix
from fastmat.model.simple_tile import SimpleTileFactory,SimpleTilePersistor

if __name__ == '__main__':
    g = Graph()
    graph_builder = GraphBuilder(g, SimpleTilePersistor(), "C:/tmp")
    A = TiledMatrix(2, 2, SimpleTileFactory(2,2,1))
    B = TiledMatrix(2, 2, SimpleTileFactory(2,2,2))
    C = TiledMatrix(2, 2, SimpleTileFactory(2,2,0))
    A = graph_builder.add_src_matrix(A, "A")
    B = graph_builder.add_src_matrix(B, "B")
    C = graph_builder.add_src_matrix(C, "C")
    
    for i in range(A.columns): 
        C[(0,0)].assign(C[(0,0)] + (A[(0,i)] * B[(i,0)]))
    
    worker_pool = range(1,3)
    for wrk_num in range(len(worker_pool)):
        Process(target=worker, args=(wrk_num,)).start()
 
    master(g)