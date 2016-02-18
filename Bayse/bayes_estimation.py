import numpy as np
from scipy import linalg 
import matplotlib.pyplot as plt
np.random.seed(0)
d,T,N,heatN,J=16,1000,1000,20,1
theta=[[1 if i==(j+1+d)%d or i==(j-1+d)%d else 0 for i in range(d)] for j in range(d)]
alpha=1.0
prior_A=alpha*matrix(np.eye(d**2))
def gen_mcmc(t_wait, x=[],theta=[[]]):
    for t in range(t_wait):
        for i in range(d):
            valu=J*(np.dot(theta[:][i],x)-x[i]*theta[i][i])
            r=np.exp(-valu)/(np.exp(-valu)+np.exp(valu))
            R=np.random.uniform(0,1)
            if(R<=r):
                x[i]=1
            else:
                x[i]=-1
    return x

def sum_xixj(n_sample,theta=[[]]):
    xixj=np.zeros((d,d))
    y=np.ones(d)
    y=gen_mcmc(100,y,theta)
    for n in range(n_sample):
        y=gen_mcmc(3,y,theta)
        xixj=xixj+np.tensordot(y,y,axes=([0][0]))/n_sample
    for l in range(d):xixj[l][l]=0
    return xixj

def heat_exixj(indexi,indexj,t_wait,sample,x=[],theta=[[]]):#note!, this function is sequence of x sampling 
    sum_expxixj=0
    x=gen_mcmc(t_wait*10,x,theta)# this waiting time of sampling is relatively short
    for t in range(sample):
        x=gen_mcmc(t_wait,x,theta)
        sum_expxixj+=np.exp(-x[i]*x[j])
        sum_expxixj/=sample
    return sum_expxixj

def ratio_of_p_of_theta(indexi,indexj,sum_of_xixj,delta_ij,theta,valu_heat_exixj):
    vec_theta=np.array(np.reshape(theta,(1,d**2)))
    a=1.0/valu_heat_exixj
    b=sum_of_xixj+2*np.dot(A[d*indexi+indexj,:],vec_theta)+A[d*indexi+indexj][d*indexi+indexj]*delta_ij
    b*=delta_ij
    b=np.exp(-b)
    ratio=a*b
    return ratio


#################### MAIN #########################
dl_sample=sum_xixj(N,theta)
# initial theta
theta_est=0.1*np.random.rand(d,d)
theta_est=0.5*(theta_est + theta_est.T)
sample_x=20
ideling,waiting,sample,count=200,2,100,0
theta_mean=np.zeros((d,d))
for t in range(ideling+waiting*sample):
    for i in range(d):
        for j in range(i+1,d):
            delta_theta=np.random.uniform(-1,1)*0.5
            valu_heat_exixj=heat_exixj(i,j,3,sample_x,x,theta_est)
            r=ratio_of_p_of_theta(i,j,dl_sample[i][j],delta_theta,theta_est,valu_heat_exixj)
            R=np.random.uniform(0,1)
            if(r<R):
                theta_est[i][j]+=delta_theta
                theta_est[j][i]+=delta_theta
            if(ideling<=t and t%waiting==0 ):
                theta_mean=theta_mean+theta_est
                count+=1
theta_mean=theta_mean/count


loss,delta=np.zeros(T),np.zeros(T)
for l in range(d):theta_est[l][l]=0
#using AdaGrad
r,a,epc=0,1,0.001
for k in range(T):
    dl_model=sum_xixj(heatN,theta_est)
    #r+=np.sum(dl_model*dl_model)
    #lr=a/(np.sqrt(r)+epc)
    lr=1.0/np.log(2+k)
    grad=dl_sample - dl_model
    theta_est=theta_est-lr*grad
    loss[k]=np.absolute(theta-theta_est).sum()
    delta[k]=np.absolute(grad).sum()

result=[gen_mcmc(1000,np.ones(d),theta_est)]
print("theta_est=",theta_est)
plt.subplot(321)
plt.imshow(theta)
plt.colorbar()
plt.title('true theta')
plt.subplot(322)
plt.imshow(theta_est)
plt.colorbar()
plt.title('estimated theta ')
plt.subplot(323)
plt.plot(loss)
plt.title('loss function')
plt.subplot(324)
plt.plot(delta)
plt.title('grad')
plt.subplot(325)
plt.imshow(result)
plt.title('generated config')
plt.show()
