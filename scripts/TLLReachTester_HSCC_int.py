
import numpy as np
import charm4py
from charm4py import charm, Chare, coro, Reducer, Group, Future, Array, Channel
import scipy.optimize
# import cdd
import TLLnet
# from HyperplaneRegionEnum import posetFastCharm
import TLLHypercubeReach
#import NodeCheckerLowerBdVerify
import time
import pickle
import os
import signal
import re
import pickle



charm.options.local_msg_buf_size = 10000
# Enable profiling
charm.options.profiling = False


N_CORES = os.cpu_count()

def main(args):
    
    # global prop_idx, pb_name, out_fname, TIMEOUT
    assert len(args) == 5, "Incorrect args: experiment.p out_fname num_cores timeout"
    experimentFile = args[1]
    out_fname = args[2]
    NUM_CORES = int(args[3])
    TIMEOUT = int(args[4])
    
    with open(experimentFile,'rb') as fp:
        experiment = pickle.load(fp)
    
    dirName = os.path.dirname(experimentFile)

    pes = {'poset':[(0,NUM_CORES,1)],'hash':[(0,NUM_CORES,1)]}
    total_time = time.time()
    tllReach = Chare(TLLHypercubeReach.TLLHypercubeReach, args=[pes])
    print('Constructor time', str(time.time() - total_time))
    charm.awaitCreation(tllReach)
    # charm.sleep(1)
    for idx, experDict in enumerate(experiment):
        
        tll = TLLnet.TLLnet.fromTLLFormat(os.path.join(dirName, experDict['tllBaseName'] + '.tll'))

        with open(os.path.join(dirName, experDict['inputSpecFile']),'rb') as fp:
            inputSpecDict = pickle.load(fp)
        
        with open(os.path.join(dirName, experDict['outputSpecFile']),'rb') as fp:
            outputSpecDict = pickle.load(fp)


        n = tll.n
        constraints = [inputSpecDict['A'] , inputSpecDict['b']]
        
        useQuery = False
        useBounding = False

        A_out = outputSpecDict['A']
        b_out = outputSpecDict['b']
        total_time = time.time()

        print(f'{experDict["tllBaseName"]}\t,{idx}')

        tllReach.initialize(tll, constraints, 100, useQuery, useBounding,awaitable=True).get()
        print('Initializer time', str(time.time() - total_time))
        # charm.awaitCreation(tllReach)
        total_time = time.time()

        #Assume prop is Ax >= b
        if(A_out < 0):
            # x <= -b
            print(f'-----Verifying  NN <= {-b_out}-----')
            lbFut = tllReach.verifyUB(-b_out,timeout=(None if TIMEOUT == 0 else TIMEOUT),ret=True) # verify NN <= b negated
            res = lbFut.get()
            if res is not None: res = not bool(res)
        else:
            # x >= b
            print(f'-----Verifying  NN >= {b_out}-----')
            lbFut = tllReach.verifyLB(b_out,timeout=(None if TIMEOUT == 0 else TIMEOUT),method='fastLP',ret=True) # verify NN >= b not negated
            res = lbFut.get()
            if res is not None: res = bool(res)
        if res is None:
            res = 'timeout'
        else:
            res = 'safe' if res != False else 'unsafe'
        total_time = time.time()-total_time
        # charm.sleep(1)

        print(' ')
        print(res)
        print('Total time elapsed: ' + str(total_time) + ' (sec)')
        print(' ')
        print('Minimum of samples: ' + str(np.min(experDict['outputSamples'])))
        print('Maximum of samples: ' + str(np.max(experDict['outputSamples'])))
        print('--------------------------------------------------')
        print(' ')

        if out_fname:
            with open(out_fname, 'a') as f:
                f.write(f'{experDict["tllBaseName"]}\t,{idx}\t,{res}\t,{total_time:.4f}\n')
                f.close()
    if charm.options.profiling:
        charm.printStats()
        for pe in range(charm.numPes()):
            charm.thisProxy[pe].printStats()
    charm.exit()


charm.start(main,modules=['posetFastCharm','TLLHypercubeReach','DistributedHash'])