This is a python library for speeding up matrix computation by splitting the matrix into tiles and distributing the operations on tiles to multiple workers. 

This project is inspired by the paper,

http://research.microsoft.com/apps/pubs/default.aspx?id=158914

I have tried to implement the ideas in python using numpy as the linear algebra library for my computations. Used zeomq as the middleware. 