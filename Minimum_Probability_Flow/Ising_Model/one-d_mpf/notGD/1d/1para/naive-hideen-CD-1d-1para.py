#! /usr/bin/env python
#-*-coding:utf-8-*-
import numpy as np
import time 
from scipy import linalg
from scipy.optimize import root 
import matplotlib.pyplot as plt
import math
n_estimation=3
np.random.seed(1)
t_interval = 30
#parameter ( System )
d, N_sample = 16,50 #124, 1000
dv=int(d/2)
N_remove=20
lr,eps =0.01,1.0e-20
t_gd_max=1000 
def gen_mcmc(J,x=[]):
    for i in range(d):
        #Heat Bath
        diff_E=2.0*x[i]*J*(x[(d+1+i)%d]+x[(i+d-1)%d])
        r=1.0/(1+np.exp(diff_E)) 
        R=np.random.uniform(0,1)
        if(R<=r):
            x[i]=x[i]*(-1)
    return x

def gen_mcmc_single(J,x=[]):
    index=np.random.randint(d)
    #Heat Bath
    diff_E=2.0*x[index]*J*(x[(d+1+index)%d]+x[(index+d-1)%d])
    r=1.0/(1+np.exp(diff_E)) 
    R=np.random.uniform(0,1)
    if(R<=r):
        x[index]=x[index]*(-1)
    return x

def sampling_phase(k_max,J_model,X_sample=[[]]):
    dJ=0.0
    for n in range(N_sample):
        x=np.copy(X_sample[n])
        v0=np.zeros(dv)
        h0=np.zeros(dv)
        # Set initial state of a chain
        for i in range(dv):
            v0[i]=x[2*i] 
            r=np.random.uniform(0,1)
            if(r<1.0/(1+np.exp(-2*J_model*(x[2*((i+1)%dv)]+x[2*i]))) ):
                h0[i]=1
            else:
                h0[i]=-1

        v=np.copy(v0)
        h=np.copy(h0)
        for k in range(k_max):
            for i in range(dv):
                r=np.random.uniform(0,1)
                if(r<1.0/(1+np.exp(-2*J_model*(h[(i-1+dv)%dv]+h[i]))) ):
                    v[i]=1
                else:
                    v[i]=-1
            for i in range(dv):
                r=np.random.uniform(0,1)
                if(r<1.0/(1+np.exp(-2*J_model*(v[(i+1)%dv]+v[i]))) ):
                    h[i]=1
                else:
                    h[i]=-1
        dJ+=(np.dot(v0,h0)-np.dot(v,h))/N_sample 
    return (dJ,np.copy(v),np.copy(h))

if __name__ == '__main__':
    sample_list=[200]
    k_list=[1]
    for k_max in k_list: 
        fname="sample"+"-naiveCD"+str(k_max)+".dat"
        f=open(fname,"w")
        for N_sample in sample_list:
            error_array=np.zeros(n_estimation)
            for nf in range(n_estimation):
                J_data=1.0
                x=np.random.choice([-1,1],d)
                for n in range(N_sample+N_remove):
                    for t in range(t_interval):
                        x = np.copy(gen_mcmc(J_data,x))
                    if(n==N_remove):X_sample = np.copy(x)
                    elif(n>N_remove):X_sample=np.vstack((X_sample,np.copy(x)))
               
                J_model=2.0
                for t in range(t_gd_max):
                    dJ,v,h=sampling_phase(k_max,J_model,X_sample)
                    J_model+=lr*dJ 
                    #lrt=lr/(np.log(t+1)+1)
                    #J_model+=lrt*dJ 
                    error=J_model-J_data
                    print(t,error)
                error_array[nf]=error
            f.write(str(N_sample)+"  " +str(np.mean(error_array) )+"  "+str(np.std(error_array)/np.sqrt(N_sample) )+"\n")
        f.close()
