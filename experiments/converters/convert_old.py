import TLLnet
import numpy as np
import pickle
import sys
import os
import re
import copy


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
        if re.search(r'\.p$',fileListIn[it[1]]):
            fileList.append(fileListIn[it[1]])

    experimentList = []
    experIdx = 0
    for fname in fileList:

        if not re.search(r'\.p$',fname):
            continue

        print(f'Working on {fname}')

        with open(fname,'rb') as fp:
            instDict = pickle.load(fp)
        # print(instDict)
        baseFileName = re.sub(r'\.p$', '', fname)

        tll = TLLnet.TLLnet(input_dim=instDict['n'], output_dim=instDict['m'], linear_fns=instDict['N'], uo_regions=instDict['M'])

        tll.setLocalLinearFns( \
                [ \
                    [llf[0].T, llf[1]]
                    for llf in instDict['TLLparameters']['localLinearFunctions'] \
                ]
            )
        tll.setSelectorSets( \
                [ \
                    [ set(np.nonzero(sMat)[0]) for sMat in sMats ]
                    for sMats in instDict['TLLparameters']['selectorMatrices'] \
                ]
            )

        tll.save(baseFileName + '.tll')

        n = instDict['n']
        A_in = np.zeros((2*n,n))
        np.fill_diagonal(A_in[:n], 1)
        np.fill_diagonal(A_in[n:], -1)
        b_in = -2 * np.ones((2*n,))

        inputFileName = f'input_property_n={instDict["n"]}_0.p'

        with open(inputFileName, 'wb') as fp:
            pickle.dump({'A':A_in, 'b':b_in, 'type':'Ax >= b', 'samples':instDict['samples']['input']}, fp)

        for outputProperty in enumerate(instDict['spec']):
            outputFileName = f'output_property_m={instDict["m"]}_{experIdx}_{outputProperty[0]}.p'
            with open(outputFileName,'wb') as fp:
                pickle.dump({'A':outputProperty[1]['A'],'b':outputProperty[1]['b'],'type':outputProperty[1]['desc']}, fp)
            
            experimentList.append( \
                        { \
                            'tllBaseName':baseFileName, \
                            'inputSpecFile':inputFileName, \
                            'outputSpecFile':outputFileName, \
                            'outputSamples':instDict['samples']['output'] \
                        } \
                )
            experIdx += 1
    
    with open('experiment.p', 'wb') as fp:
        pickle.dump(experimentList,fp)