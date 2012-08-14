'''
Defines the constructs for executing the dag by distributing the 
load to workers.

@author: Balraja Subbiah

'''
import time
import zmq
import fastmat.model.graph as graph_lib

from fastmat.dag.builder import SourceVertex

def master(dag):
    '''
    Defines the server function. it fans out the graph, waiting for the workers
    to finish the task. It acts both as an ventilator and results manager.
    '''
    context = zmq.Context()
    print "\n *** STARITING MASTER"
    task_publisher = context.socket(zmq.PUSH)
    task_publisher.bind("tcp://127.0.0.1:5557")
    
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://127.0.0.1:5558")
    
    notifications_publisher = context.socket(zmq.PUB);
    notifications_publisher.bind("tcp://127.0.0.1:5559")

    # Give everything a second to spin up and connect
    time.sleep(1)
    top_gen = graph_lib.topological_generate(dag)
    poller = zmq.Poller()
    poller.register(task_publisher, zmq.POLLOUT)
    poller.register(results_receiver, zmq.POLLIN)
    
    completed_vertices = []
    while True:
        socks = dict(poller.poll())
        if task_publisher in socks and socks[task_publisher] == zmq.POLLOUT:
            try:
                if len(completed_vertices) > 0:
                    vertex = top_gen.send(completed_vertices)
                else:
                    vertex = next(top_gen)
                while vertex is not None and isinstance(vertex, SourceVertex):
                    print "\n Done processesing src vertex " + vertex.vertex_id
                    vertex = top_gen.send(vertex)
                
                if (vertex is not None):
                    print "Sending " + vertex.vertex_id
                    task_publisher.send_pyobj(vertex)
                    
            except StopIteration:
                break
        
        if results_receiver in socks and socks[results_receiver] == zmq.POLLIN:
            vertex = results_receiver.recv_pyobj()
            print "Completed processing the vertex "
            completed_vertices.append(vertex)
    
    notifications_publisher.send("FINISHED")

def worker(wrk_num):
    ''' 
    Defines the worker which receives tasks from the master and executes
    the same
    '''
    
    print "Starting WORKER"
    context = zmq.Context()
    work_receiver = context.socket(zmq.PULL)
    work_receiver.connect("tcp://127.0.0.1:5557")
    results_sender = context.socket(zmq.PUSH)
    results_sender.connect("tcp://127.0.0.1:5558")
    control_receiver = context.socket(zmq.SUB)
    control_receiver.connect("tcp://127.0.0.1:5559")
    control_receiver.setsockopt(zmq.SUBSCRIBE, "")
    
    poller = zmq.Poller()
    poller.register(work_receiver, zmq.POLLIN)
    poller.register(control_receiver, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())
        if work_receiver in socks and socks.get(work_receiver) == zmq.POLLIN:
            executable_vertex = work_receiver.recv_pyobj()
            print "RECEIVED %s vertex for execution"%(executable_vertex.id())
            results_sender.send_pyobj(executable_vertex)

        if control_receiver in socks and socks.get(control_receiver) == zmq.POLLIN:
            control_message = control_receiver.recv()
            if control_message == "FINISHED":
                print("Worker %i received FINSHED, quitting!" % wrk_num)
                break
