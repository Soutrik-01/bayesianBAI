import numpy as np
import math
from StochasticBanditsModules2 import GaussianArm
from bayesElim import BanditInstance, makeBandits


def ALUM(bandits, budget):
    L = math.floor(math.log((bandits.K)/3)/math.log(3/2))
    #print(L
    numSamp = [2**(L-2)*budget//3**(L-1) for i in range(1,3)]
    for l in range(3,L+2):
        numSamp.append(2**(L-(l-1))*budget//3**(L-(l-2)))
    #print(numSamp)
    for l in range(1, L+1):
        sampledBandits = bandits.four_samples()
        sampledMean = np.array([])
        for bandit in sampledBandits:
            sampledMean = np.append(sampledMean, bandit.pullArm_sum(numSamp[l-1]//4))
        #print('Sampled means at round ' ,sampledMean/(numSamp[l-1]//4))
        bestind = np.argmax(sampledMean)
        if bestind == 0 or bestind == 1:
            bandits.deact_in_series(2*bandits.numact()//3, bandits.numact())
        else:
            bandits.deact_in_series(0, math.ceil(bandits.numact()/3))
        
    active = bandits.active_indices()
    #print('Active at end', active)
    sampledMeans = np.array([bandits.banditlist[ind].pullArm_sum(numSamp[-1]) for ind in active])/(numSamp[L]//4)
    #print('Sampled mean end', sampledMeans)
    maxInd = active[np.argmax(sampledMeans)]
    #print('max', maxInd)

    for j in range(bandits.K):
        bandits.reset(j)

    return bandits.banditlist[maxInd]
    





    
