import TLLnet
import numpy as np
import pickle
import sys
import os
import re
import copy
from vnnlib import read_vnnlib_simple


if __name__ == '__main__':

    if len(sys.argv) == 2:
        baseDir = sys.argv[1]
    else:
        raise ImportError('No directory specified.')
    
    os.chdir(sys.argv[1])

    fileListIn = os.listdir()
    fileOrder = list(map(lambda x: (tuple(list(map(lambda y: int(y),re.sub(r'[^\d]+',',',x[1]).split(',')[1:-1]))), x[0]), enumerate(fileListIn)))
    fileOrder.sort()

    fileList = []
    for it in fileOrder:
        if re.search(r'\.tll$',fileListIn[it[1]]):
            fileList.append((fileListIn[it[1]],it[0][-2],it[0][-1]))
    
    fileListIn = os.listdir('./vnnlib')
    fileOrder = list(map(lambda x: (tuple(list(map(lambda y: int(y),re.sub(r'[^\d]+',',',x[1]).split(',')[1:-1]))), x[0]), enumerate(fileListIn)))
    fileOrder.sort()

    fileListVNNLIB = []
    for it in fileOrder:
        if re.search(r'\.vnnlib$',fileListIn[it[1]]):
            fileListVNNLIB.append((fileListIn[it[1]],it[0][-2],it[0][-1]))

    # print(fileList)

    experimentList = []
    experIdx = 0
    for f_item in enumerate(fileList):
        fname = f_item[1][0]
        # if not re.search(r'\.tll$',fname):
        #     continue

        print(f'Working on {fname}')
        
        problemName = re.sub(r'\.vnnlib$','',fileListVNNLIB[f_item[0]][0])
        # print(instDict)
        baseFileName = re.sub(r'\.tll$', '', fname)

        assert fileList[f_item[0]][1] == fileListVNNLIB[f_item[0]][1] and fileList[f_item[0]][2] == fileListVNNLIB[f_item[0]][2], 'Mismatch of file indexes'

        print((fname,problemName,baseFileName))

        # raise ValueError()

        tll = TLLnet.TLLnet.fromTLLFormat(fname)
        tll.createKeras()

        n = tll.n
        A_in = np.zeros((2*n,n))
        np.fill_diagonal(A_in[:n], 1)
        np.fill_diagonal(A_in[n:], -1)
        b_in = -2 * np.ones((2*n,))

        inputFileName = f'input_property_n={n}_0.p'
        inputSamples = (2*2*np.random.random_sample(size=(5000,n)) - 2)
        with open(inputFileName, 'wb') as fp:
            pickle.dump({'A':A_in, 'b':b_in, 'type':'Ax >= b', 'samples':inputSamples}, fp)

        spec = read_vnnlib_simple(os.path.join('./vnnlib',fileListVNNLIB[f_item[0]][0]), 2, 1) #Violation of the property
        print(os.path.join('./vnnlib',fileListVNNLIB[f_item[0]][0]))
        A_out, b_out = spec[0][1][0]
        A_out = float(A_out)
        b_out= float(b_out)

        outputFileName = f'outputProperty_{problemName}_m={tll.m}_{f_item[1][1]}_{f_item[1][2]}.p'
        with open(outputFileName,'wb') as fp:
            pickle.dump({'A':A_out,'b':b_out,'type':'Ax >= b'}, fp)
        print(outputFileName)
        outputSamples = tll.model.predict(inputSamples)
        experimentList.append( \
                    { \
                        'tllBaseName':baseFileName, \
                        'inputSpecFile':inputFileName, \
                        'outputSpecFile':outputFileName, \
                        'outputSamples':outputSamples \
                    } \
            )
        experIdx += 1
    
    with open('experiment.p', 'wb') as fp:
        pickle.dump(experimentList,fp)