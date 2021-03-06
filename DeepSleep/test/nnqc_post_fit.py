import sys
if __name__ == '__main__':
    import subprocess as sb
    sys.path.insert(1, sb.check_output(
        'echo $(git rev-parse --show-cdup)', 
        shell=True).decode().strip('\n')+'DeepSleep/')
from modules.plotAna import Plotter, StackedHist, Hist
import operator as op
import pandas as pd
import numpy as np
import re
import uproot
import seaborn as sns
import config.ana_cff as cfg
from lib.fun_library import save_pdf
from post_fit import PostFit
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import AutoMinorLocator, FixedLocator, FormatStrFormatter
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch, Rectangle
from matplotlib import rc

rc("savefig",dpi=250)
rc("figure", figsize=(8, 6*(6./8.)), dpi=200)                                                            

@save_pdf('qc_nn_postfits.pdf')
def main():
    dnn_vars = set(cfg.dnn_ZH_vars)
    print(len(dnn_vars))
    for v in dnn_vars:
        froo = f'fitDiagnostics_{v}_NNcuts_run2.root'
        print(froo)
        qc= QCNNPostFit(froo,v)
        qc.makeplots(doPull=True)

class QCNNPostFit(PostFit):
    '''
    steal some of the functionality 
    from already existing class
    '''

    def __init__(self, fitroo, kinem):
        super().__init__(fitroo, kinem=kinem)
        

    def do_stack(self, d, top_axs, ch):

        ycumm = None
        # stack portion
        ordered_list = re.findall(rf'tt[H,Z]', ' '.join(list(d.keys()))) + ['other','Vjets','ttX','tt_2b','tt_bb','TTBar']
        #colors =  plt.cm.gist_rainbow(np.linspace(0,1,len(ordered_list)))
        colors =  plt.cm.tab10(np.linspace(0,1,10))[0:2]
        colors = np.append(colors, plt.cm.gist_rainbow(np.linspace(0,1,6)), axis=0)
        #
        #for j,k in enumerate(d):
        for j,k in enumerate(ordered_list):
            #if 'data' in k or 'total' in k: continue
            if k not in d: continue
            y = np.append(d[k]['values'],0)
            if ycumm is not None:
                ycumm += y
            else:
                ycumm = y 
            c = colors[j]
            #c = colors[j + (len(colors)//2)*(j % 2) - 1*((j+1)%2)]
            top_axs.fill_between(self.edges[ch],ycumm,ycumm-y,step="post", 
                                 linewidth=0, color=c, label=k)
            # add total error and data points
        top_axs.errorbar(x=(self.edges[ch][1:]+self.edges[ch][:-1])/2, y=d['data']['values'],
                     xerr=(self.edges[ch][1:]-self.edges[ch][:-1])/2 ,yerr=[d['data']['errdw'],d['data']['errup']], 
                     fmt='.', label='data', color='k')
        self.make_error_boxes(top_axs, (self.edges[ch][1:]+self.edges[ch][:-1])/2, d['total']['values'],
                              xerror=(self.edges[ch][1:]-self.edges[ch][:-1])/2, yerror=d['total']['err'], label='stat+sys')
    


if __name__ == '__main__':
    main()
