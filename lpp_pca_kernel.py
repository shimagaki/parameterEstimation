import numpy as np
import numpy as np
from scipy import linalg
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt
import numpy.matlib
np.set_printoptions(precision=2)
np.random.seed(0)
N,hh,m=1000,35.0,2#sample,#width,#enbed
a=3.0*np.pi*np.random.rand(N)
x=np.array([a*np.cos(a),20*np.random.rand(N),a*np.sin(a)])
fig=plt.figure()
ax=Axes3D(fig)
ax.scatter3D(np.ravel(x[0]),np.ravel(x[1]),np.ravel(x[2]),c=a)
plt.show()
xx=np.dot(x.T,x)# =(60,60)
x2=np.matrix(np.diagonal(xx))
x2=np.matlib.repmat(x2,len(x2),1)+np.matlib.repmat(x2.T,1,len(x2))
K=np.matrix(np.exp(-(x2-2*xx)/hh))
H=np.matrix(np.ones((N,N))/N)
K=K - K*H - H*K + H*K*H
D,invD=np.ones(N),np.ones(N)
for i in range(N):D[i],invD[i]=np.sum(K[i]),1.0/(np.sum(K[i])+0.00000000001)#shuld I eliminate diagonal of K ?
sqrt_invD=np.matrix(np.sqrt(np.diag(np.array(invD))))
D=np.matrix(D)
L=np.matrix(D-K)
A=sqrt_invD*L*sqrt_invD
la,v=linalg.eigh(A)
idx=la.argsort()[::-1]
l1,l2=la[idx[0]],la[idx[1]]
v1,v2=v[:,idx[0]],v[:,idx[1]]#U,s,Vh=linalg.svd(K)
lamda=np.diag([l1,l2])
A=np.vstack((v1,v2))
print("shape A", np.shape(A))
#B=np.dot(lamda,np.dot(A,K))
plt.scatter(np.real(A[0]),np.real(A[1]),c=a)
plt.show()
