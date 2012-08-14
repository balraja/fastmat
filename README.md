This is a python library for speeding up matrix computation by splitting the matrix into tiles and distributing the operations on tiles to multiple workers. 

This project is inspired by the paper,

http://research.microsoft.com/apps/pubs/default.aspx?id=158914

I have tried to implement the ideas in python using numpy as the linear algebra library for my computations. Used zeomq as the middleware. 

Consider the simple example as follows. This example can be found in fastmat.test.test_dag.py

We want to multiply two 400 * 400 matrices.  Each matrix is divided into 100 * 100 tiles. With tiling the matrix size is now 
shrinked to (4 * 4) matrix and each element of this matrix is a (100 * 100) tile.

The simple step for matrix operations are as follows,

1. Wrap the tiled matrices under the context of graph builder.
2. Perform the operations on the wrapped graph, which will eventually build the 
   DAG that determines the dataflow for execution.
3. Fireup a set of workers and execute the DAG built in 2. We are done.

Following is the examply for multiplying the matrices

    # Create the tiled matrices.    
    A = TiledMatrix(4, 4, NumpyTileFactory(100,100,1))
    B = TiledMatrix(4, 4, NumpyTileFactory(100,100,2))
    C = TiledMatrix(4, 4, NumpyTileFactory(100,100,0))
    
	# Create a graph builder and add the source matrices to the 
	# context of a graph.
	g = Graph()
	graph_builder = GraphBuilder(g, NumpyTilePersistor(), "C://tmp")
    A = graph_builder.add_src_matrix(A, "A")
    B = graph_builder.add_src_matrix(B, "B")
    C = graph_builder.add_src_matrix(C, "C")
    
    # Now do the operations on the wrapped matrices, which will be 
	# transformed into a DAG that determines the data flow for 
	# execution
    for i in range(A.rows): 
        for j in range(B.columns):
            for k in range(A.columns):
                C[(i,j)].assign(C[(i,j)] + (A[(i,k)] * B[(k,j)]))
    
    
    # Now span workers to execute the graph.
    worker_pool = range(1,3)
    for wrk_num in range(len(worker_pool)):
        Process(target=worker, args=(wrk_num,)).start()
    
    # Start the master that controls the execution.
    master(g)
    
    #Unwrap the result after execution completion.
    result = unwrap_matrix(C)
    print result