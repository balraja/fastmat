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

This module defines a basic graph and related tools.

@author: Balraja Subbiah
'''
import collections
import copy

class GraphConstructionError(Exception):pass

class Edge(object):
    '''Abstracts the concept of an edge'''
    
    def __init__(self, src, destn):
        self.src=src
        self.destn=destn
        
class TopologicalSorter(object):
    '''A simple class to perform to topological sorting of graph'''
    
    def __init__(self, graph):
        self.graph = graph.clone()
    
    def __iter__(self):
        return self;
    
    def next(self):
        '''Performs the topological sort as an iteration protocol'''
        if len(self.graph.indegree_map) == 0:
            raise StopIteration
        
        for (vertex, indegree) in self.graph.indegree_map.items():
            if (indegree == 0):
                break;
        else:
            raise StopIteration
        
        self.graph.remove_vertex(vertex)
        return vertex

class Graph(object):
    '''Abstracts out the executable graph'''
    
    def __init__(self):
        '''CTOR'''
        self.adj_list = {}
        self.indegree_map = {}
    
    def vertices(self):
        '''Returns the vertices of graph'''
        return tuple(self.adj_list.keys())
    
    def indegree(self, vertex):
        '''returns the indegree of a vertex'''
        return self.indegree_map.get(vertex, -1)
    
    def __getitem__(self,vertex):
        '''Returns the adjlist of a vertex'''
        return tuple(self.adj_list.get(vertex, []))
    
    def clone(self):
        '''Clones the graph'''
        new_graph = Graph()
        new_graph.adj_list = copy.deepcopy(self.adj_list)
        new_graph.indegree_map = copy.deepcopy(self.indegree_map)
        return new_graph
    
    def top_sort(self):
        '''Returns topological sorter of the graph'''
        return TopologicalSorter(self)
    
    
    def __add__(self, element):
        '''Adds an element to the graph'''
        if (not isinstance(element,Edge)):
            if element not in self.adj_list:
                self.adj_list[element] = []
            if element not in self.indegree_map:
                self.indegree_map[element] = 0 
        else:
            if element.src in self.adj_list:
                self.adj_list[element.src].append(element.destn)
            else:
                self.adj_list[element.src] = [element.destn] 
            
            if not element.destn in self.adj_list:
                self.adj_list[element.destn] = []
                
            if element.destn in self.indegree_map:
                self.indegree_map[element.destn] += 1
            else:
                self.indegree_map[element.destn] = 1
            
            if not element.src in self.indegree_map:
                self.indegree_map[element.src] = 0
    
    def remove_vertex(self,vertex):
        '''Removes a vertex from the graph '''
        for nbr in self.adj_list.get(vertex, []):
            self.indegree_map[nbr] -= 1
        if vertex in self.adj_list:
            del self.adj_list[vertex]
        del self.indegree_map[vertex]
        
    def __contains__(self, param):
        ''' Checks whether an edge or vertex is present in the graph '''
        if isinstance(param, Edge):
            return param.src in self.adj_list and param.destn in self.adj_list[param.src]
        else: 
            return param in self.adj_list
        
def topological_generate(graph):
    '''performs the topological sort as a generator'''
    
    graph_copy = graph.clone()
    already_returned = []
    while True:
        if len(graph_copy.indegree_map) == 0:
            raise StopIteration
        
        for (vertex, indegree) in graph_copy.indegree_map.items():
            if (indegree == 0 and vertex not in already_returned):
                result = vertex
                break;
        else:
            result = None
            
        if (result is not None):
            already_returned.append(result)
            
        done = yield result
        if done is not None:
            if isinstance(done, collections.Iterable):
                for done_vertex in done:
                    already_returned.remove(done_vertex)
                    graph_copy.remove_vertex(done_vertex)
            else:
                already_returned.remove(done)
                graph_copy.remove_vertex(done)

if __name__ == "__main__":
    
    g = Graph()
    g + Edge(1,2)
    g + Edge(1,3)
    g + Edge(2,4)
    g + Edge(3,4)
    g + 5
    
    print g.adj_list
    print g.indegree_map
    
    for item in g.top_sort():
        print item
    
    print "*** GENERATOR **"
    mygen = topological_generate(g)
    print next(mygen)
    print next(mygen)
    print mygen.send(1)
    print next(mygen)
    print mygen.send([2,3])
    print next(mygen)
    print mygen.send(4)
    print mygen.send(5)
    
