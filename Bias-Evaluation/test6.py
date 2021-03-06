#! /usr/bin/env python
#-*-coding:utf-8-*-
import random, math
import numpy as np
import time 
from scipy.optimize import fsolve
from scipy import linalg
import itertools
#import warnings
#warnings.filterwarnings('ignore', 'The iteration is not making good progress')
PI = math.pi

def logsumexp(a,b):
    output=0
    if(a==b):
        output = a+np.exp(2)
    else:
        x,y = max(a,b),min(a,b)
        output = x + np.log( 1+np.exp(y-x) ) # = log( exp(x) + exp(y) )
    return output 

def calc_model_mle(h=[],J=[]):
    d = len(h)
    z=0
    s_model=np.zeros(d)
    ss_model=np.zeros(d)
    state= list(itertools.product([1,-1],repeat=d))
    for s in state:
        exp_of=0.0
        for i in range(d):
            exp_of+=J[i]*s[i]*s[(i+1)%d]+h[i]*s[i]
        exp_s=np.exp(exp_of)
        for i in range(d):
            ss_model[i]+=s[i]*s[(i+1)%d]*exp_s
            s_model[i]+=s[i]*exp_s
        z += exp_s
    s_model = s_model/ z
    ss_model = ss_model/ z
    return (s_model,ss_model) 

# This function is used as the expectations of data, which close to the equilibrium.
def calc_model_mle_with_noise(h0=[],J0=[]):
    global alpha, mu
    d = len(h0)
    z0=0
    s_model=np.zeros(d)
    ss_model=np.zeros(d)
    state= list(itertools.product([1,-1],repeat=d))
    normalize_noise = 0.0
    for s in state:
        noise=np.exp(-0.5*np.dot((mu-s),(mu-s)))
        normalize_noise+=noise
        ene0=calc_energy(h0,J0,s)
        z0+=np.exp(ene0)
    for s in state:
        noise=np.exp(-0.5*np.dot((mu-s),(mu-s)))
        ene0=calc_energy(h0,J0,s)
        exp_s=np.exp(ene0-np.log(z0))
        for i in range(d):
            ss_model[i] += s[i]*s[(i+1)%d] * ( alpha*exp_s + (1.0-alpha)*noise/normalize_noise )
            s_model[i] += s[i]* ( alpha*exp_s + (1.0-alpha)*noise/normalize_noise )
    s_model = s_model
    ss_model = ss_model
    return (s_model,ss_model) 

def calc_mean_covariance(h=[],J=[]):
    d = len(h)
    z=0
    mu=np.zeros(d)
    cov=np.zeros((d,d))
    state= list(itertools.product([1,-1],repeat=d))
    for s in state:
        s = np.array(s) 
        exp_of=0.0
        for i in range(d):
            exp_of+=J[i]*s[i]*s[(i+1)%d]+h[i]*s[i]
        exp_s=np.exp(exp_of)
        z += exp_s
        mu = mu + s * exp_s
        smat= np.matrix(s)
        cov = cov + np.dot(smat.T,smat) * exp_s
    mu = mu/ z
    cov = cov/ z - np.dot(np.matrix(mu).T,np.matrix(mu))  
    return (mu,cov) 

def calc_data_hJ(sample=[[]]):
    N = len(sample)
    sdata = np.ones(d)
    ssdata = np.ones(d)
    for s in sample:
        temps = np.copy(s).tolist()
        head = temps.pop(0)
        temps.append(head)
        temps = np.array(temps)
        ss = np.array(s)*temps 
        sdata =sdata  + s
        ssdata  = ssdata  + ss 
    sdata  = sdata /N
    ssdata = ssdata /N
    return (sdata,ssdata) 

def gen_sample(N,h=[],J=[]):
    sample = []
    list_index=np.arange(d)
    t_min_max=300 #  maximum of minimum relaxation time
    s = np.random.choice([-1,1],d)
    t_wait= 50
    for t in range(t_min_max+t_wait*N+1):# or changing of the energy is smaller than epsilon. 
    # sequential update
        for i in list_index:
            r = random.uniform(0.0,1.0)
            p = np.exp(-2*(J[(i+d-1)%d]*s[i]*s[(i+d-1)%d]+J[(i+1)%d]*s[i]*s[(i+1)%d]+h[i]*s[i]))
            if(r<p):
                s[i]*=-1
        np.random.shuffle(list_index)
        if(t>t_min_max and (t-t_min_max)%t_wait==0):
            sample.append(np.copy(s))
    return sample

# Using modified log-sum-exp method. 
# The empirical is arleady an equilibrium.. 
def calc_model_cd1_HB_LSE(parameter=[],*args):
    global alpha,mu,Sigma,coef
    d = int(len(parameter)/2.0)
    mu=np.zeros(d) 
    h,J = parameter[:d],parameter[d:] 
    h0,J0=args
    state = list(itertools.product([1,-1],repeat=d))
    eq_of_cd1_h=np.zeros(d)
    eq_of_cd1_J=np.zeros(d)
    z0 = 0
    normalize_noise = 0.0
    ene_max=0
    g_expect = np.zeros(2*d)
    for s in state:
        energy = calc_energy(h,J,s)
        ene0 = calc_energy(h0,J0,s)
        z0 += np.exp(ene0)
        noise=np.exp(-0.5*np.dot((mu-s),(mu-s)))
        normalize_noise+=noise
        if(ene_max < energy):
            ene_max=energy
        ss_temp = np.copy(s).tolist()
        s_0 = ss_temp.pop(0)
        ss_temp.append(s_0)
        ss = np.array(ss_temp) * s 
        g = np.append(s,ss)
        g_expect =g_expect + g * np.exp(ene0)
    g_expect = g_expect / z0 
    expect_p_r_of_g = np.zeros(2*d) 
    expect_prim_s = np.zeros((2*d,2*d)) 
    for s in state:
        ene0 = calc_energy(h0,J0,s)
        ene = calc_energy(h,J,s)
        noise=np.exp(-0.5*np.dot((mu-s),(mu-s)))
        for i in range(d):
            si = np.copy(s)
            si1 = np.copy(s)
            si[i]*=-1
            si1[(i+1)%d]*=-1
            ene_i = calc_energy(h,J,si)
            ene_i1 = calc_energy(h,J,si1)
            A_si_s = np.exp(ene_i-ene_max) / (np.exp(ene-ene_max)+ np.exp(ene_i - ene_max))  * (alpha*np.exp(ene0)/z0 + (1.0-alpha)*noise/normalize_noise)
            A_si_s1 = np.exp(ene_i1-ene_max) / (np.exp(ene-ene_max)+ np.exp(ene_i1 - ene_max)) * (alpha*np.exp(ene0)/z0 + (1.0-alpha)*noise/normalize_noise)
            #A_si_s = np.exp(ene_i+ene0) / (np.exp(ene)+ np.exp(ene_i))
            eq_of_cd1_h[i]+=-2*s[i]*A_si_s
            eq_of_cd1_J[i]+=-2*s[i]*s[(i+1)%d]*(A_si_s + A_si_s1)
            #eq_of_cd1_J[(i+d-1)%d]+=-2*s[i]*s[(i+1)%d]*A_si_s
        ss_temp = np.copy(s).tolist()
        s_0 = ss_temp.pop(0)
        ss_temp.append(s_0)
        ss = np.array(ss_temp) * s 
        g = np.append(s,ss)
        expect_p_r_of_g = expect_p_r_of_g + g*(noise/normalize_noise-np.exp(ene0)/z0)
        expect_prim_s = expect_prim_s + np.dot(np.matrix(g).T,np.matrix(g-g_expect))*np.exp(ene0)/z0  
    sum_expect_p_r_of_g = sum(abs(expect_p_r_of_g))
    # once taking the sum(average) of the g_a, then sum of the inverse of (g-g_expect) 
    sum_expect_prim_s = sum(1.0/abs(sum(expect_prim_s)))
    coef = sum_expect_p_r_of_g * sum_expect_p_r_of_g / (2*d)
    eq_of_cd1_h=eq_of_cd1_h
    eq_of_cd1_J=eq_of_cd1_J
    para_out=np.append(eq_of_cd1_h,eq_of_cd1_J)
    return para_out 

def calc_energy(h=[],J=[],s=[]):
    temps = np.copy(s).tolist()
    head = temps.pop(0)
    temps.append(head)
    temps = np.array(temps)
    ss = np.array(s)*temps 
    energy = np.dot(h,np.array(s))+np.dot(J,np.array(ss)) 
    return energy

def eq_of_ml(parameter=[],*args):
    d = int(len(parameter)/2.0)
    h,J = parameter[:d],parameter[d:] 
    sdata,ssdata=args
    s_ml,ss_ml = calc_model_mle(h,J)
    para_out=np.append(sdata-s_ml, ssdata-ss_ml)
    return para_out 

def eq_of_cd(parameter=[],*args):
    d = int(len(parameter)/2.0)
    h,J = parameter[:d],parameter[d:] 
    sdata,ssdata=args
    s_cd,ss_cd = calc_model_cd1_HB_LSE(h,J)
    para_out=np.append(sdata-s_cd, ssdata-ss_cd)
    return para_out 

if __name__ == '__main__':
    N=30
    #h,J = np.ones(d) * 0.2,np.ones(d) * 0.2 
    h0,J0 =[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],[0.1,0.0,0.1,0.0,0.1,0.0,0.1,0.0,0.1] 
    #h0,J0 =[0.1,0.2,0.3],[0.1,0.0,0.1] 
    global alpha, mu, Sigma,coef
    mu,Sigma = calc_mean_covariance(h0,J0)  # Sima is not used.
    #sample = gen_sample(N,h,J)
    h_init,J_init= [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1],[0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1] 
    #h_init,J_init= [0.1,0.1,0.1],[0.1,0.1,0.1] 
    initial = (h_init,J_init)
    ans =np.append(h0,J0)
    #sdata,ssdata = calc_data_hJ(sample)
    alpha_list = [1.0,0.999,0.995,0.9925,0.99,0.95,0.9,0.85,0.8,0.75,0.7,0.65,0.6,0.55,0.5,0.45,0.4,0.35,0.3,0.25,0.2,0.15,0.1,0.5,0.01,0.0]
    #alpha_list = [1.0,0.25]
    print "#alpha, diff_ml, diff_cd, coef \n"
    for alpha in alpha_list:
        #MLE
        #sdata,ssdata = calc_model_mle(h0,J0)
        sdata,ssdata = calc_model_mle_with_noise(h0,J0)
        solv_ml=fsolve(eq_of_ml,initial,args=(sdata,ssdata))
        
        #CD1
        solv_cd=fsolve(calc_model_cd1_HB_LSE,initial,args=(h0,J0))

        diff_ml=solv_ml-ans
        diff_cd=solv_cd-ans
        d = len(h0)
        print alpha,sum(np.abs(diff_ml)/d),sum(np.abs(diff_cd)/d), coef




