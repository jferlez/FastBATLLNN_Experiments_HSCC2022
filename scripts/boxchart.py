import numpy as np 
import matplotlib.pyplot as plt
import re
import sys
import os 

class VerificationResults:
    def __init__(self,status,times):
        self.status = status
        self.times  = times

def parse_result(fname):
    results = {}
    with open(fname,'r') as f:
        lines = f.readlines()
        for line in lines:
            line = re.sub("\s+", "", line.strip())
            words = line.split(',')
            pb_name, prop, status, time = words
            if pb_name not in results:
                results[pb_name] = {}
                results[pb_name]['times'] = []
                results[pb_name]['status'] = []
                results[pb_name]['timeouts_cnt'] = 0
            if status != 'timeout':
                results[pb_name]['times'].append(float(time))
                results[pb_name]['status'].append(float(time))
            else:
                results[pb_name]['timeouts_cnt'] += 1
    return results

def plot_cactus(results,color = 'r'):
    proved_idxs = np.where(results.status != 'timeout')[0]
    times = sorted(results.times[proved_idxs])
    n_proved = np.ones_like(proved_idxs)
    n_proved = list(n_proved.cumsum())
    n_proved = [0] + n_proved + [n_proved[-1]]  
    times = [0] + times + [TIMEOUT]

    # plt.figure()
    plt.plot(n_proved,times,color = 'tab:'+color)

def adjustFigAspect(fig,aspect=1):
    '''
    Adjust the subplot parameters so that the figure has the correct
    aspect ratio.
    '''
    xsize,ysize = fig.get_size_inches()
    minsize = min(xsize,ysize)
    xlim = .4*minsize/xsize
    ylim = .4*minsize/ysize
    if aspect < 1:
        xlim *= aspect
    else:
        ylim /= aspect
    fig.subplots_adjust(left=.5-xlim,
                        right=.5+xlim,
                        bottom=.5-ylim,
                        top=.5+ylim)

TIMEOUT = 300
cores = 4

assert len(sys.argv) > 1, "Experiment number missing"
experiment  = int(sys.argv[1])

results_dir = '/home/hscc/tools/results/'
if(experiment == 1):
    fname = os.path.join(results_dir,f'experiment1_{cores}.txt')
else:
    fname = os.path.join(results_dir,f'experiment2_{cores}.txt')
ddict = parse_result(fname)
data = []
timeout_cnts = []
for key in ddict.keys():
    data.append(np.array(ddict[key]['times']))
    timeout_cnts.append(ddict[key]['timeouts_cnt'])

figure,ax = plt.subplots(dpi = 300)
# ax = plt.gca()
if(experiment == 1):
    ax.set_xlabel("Input dimension")
else:
    ax.set_xlabel("Number of local linear functions")
if experiment == 1:
    ax.tick_params(axis = 'x', labelsize=5)
else:
    ax.tick_params(axis = 'x', labelsize=8)
ax.tick_params(axis = 'y', labelsize=8)
ax.set_ylabel("Time(sec)")
ax.set_yscale('log')
labels = None
if experiment == 2:
    labels = ['16', '32','48','64','96','128' ,'160','192', '224', '256', '512']
ax.boxplot(data, showfliers= False, labels= labels)
if experiment == 2:
    ax2 = ax.twinx()
    ax2.tick_params(axis = 'y', labelsize=8)
    ax2.set_ylabel('Timeouts')
    ax2.bar(ax.get_xticks(), timeout_cnts, alpha =0.3, color='red')
adjustFigAspect(figure,aspect=1.7)
plt.savefig(os.path.join(results_dir, f'experiment_{experiment}.pdf'), dpi=301, transparent=True)  



# ax = plt.gca()
# ax.set_xlim(0, 240)
# #plt.title('Cactus plot for splitting heuristics')
# plt.xlabel("Proved cases")
# plt.ylabel("Timeout(sec)")
# plt.yscale('log')
# ax.set_ylim(-50,TIMEOUT)
# plt.grid()
# plt.legend(solvers,fontsize= 'x-small')
# # ax.set_aspect(1)
pass
