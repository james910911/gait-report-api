import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
from mpl_toolkits.mplot3d import Axes3D

def FreSignal(sig:list = None,title:str=None,Sampling_frequency = 120,size=(20, 2)):
    """ 展示頻域訊號 """
    lensig = len(sig)//2
    x = np.linspace(0.0,Sampling_frequency,lensig);

    fig = plt.figure(figsize=size)
    fig.add_subplot(1,1,1)
    plt.title(f'{title}')
    plt.plot(x, sig[0:lensig])
    # plt.legend()
    plt.show()

def signalturn(signal, Pst,Pen,title='TurnArea',size=(10, 2)):
    """
    展示'轉彎區域'與'訊號'
    以觀察'轉彎區域'和'訊號'的關係
    """
    # 繪製信號
    plt.figure(figsize=size)  # 設置圖形大小
    plt.plot(signal, label='Signal')
    
    # 繪製每個peak位置的垂直虛線
    for pst in Pst:
        plt.axvline(x=pst, color='r', linestyle='--', label='Start' if pst == Pst[0] else "")
    for pen in Pen:
        plt.axvline(x=pen, color='g', linestyle='--', label='End' if pen == Pen[0] else "")
    
    # 添加圖例
    plt.legend()
    plt.title(title)
    plt.show()

def sigdisplay(sig:list = None,title:str = None,Sampling_frequency = 120,size=(20, 2)):
    """用於展示單獨訊號"""
    Len = len(sig);
    Min,Sec = int(round(Len/Sampling_frequency,2)//60),round(round(Len/Sampling_frequency,2)%50,2)
    y,x = np.array(sig),np.linspace(0.0,Len/Sampling_frequency,Len);

    fig = plt.figure(figsize=size)
    fig.add_subplot(1,1,1)
    plt.title(f'{title}')
    plt.plot(x, y, label='signal')
    plt.legend()
    plt.show()

def sigRL(Rsig:list = None,Lsig:list = None,title:str = None,Sampling_frequency = 120,size=(20, 2)):
    """用於展示左右腳訊號，並用於比較"""
    lenR,lenL = len(Rsig),len(Lsig);
    Min,Sec = int(round(lenR/Sampling_frequency,2)//60),round(round(lenR/Sampling_frequency,2)%60,2)
    Ry,Rx = np.array(Rsig),np.linspace(0.0,lenR/Sampling_frequency,lenR);
    Ly,Lx = np.array(Lsig),np.linspace(0.0,lenL/Sampling_frequency,lenL);

    fig = plt.figure(figsize=size)
    fig.add_subplot(1,1,1)
    plt.title(f'{title} ;time= {Min}m {Sec}s')
    plt.plot(Rx, Ry, label='Rsig')
    plt.plot(Lx, Ly, label='Lsig')
    plt.legend()
    plt.show()

def parapainRL(Rsig:list = None,Lsig:list = None,Pain:list = None,title:str = None,Sampling_frequency = 120,size=(20, 2),lenresize=200):
    """用於展示左右腳參數，並標記疼痛轉換點"""
    lenR,lenL = len(Rsig),len(Lsig);
    Ry,Rx = np.array(Rsig),np.linspace(0.0,lenR,lenR);
    Ly,Lx = np.array(Lsig),np.linspace(0.0,lenL,lenL);

    
    fig = plt.figure(figsize=size)
    fig.add_subplot(1,1,1)
    
    
    plt.plot(Rx, Ry, label='Rsig')
    plt.plot(Lx, Ly, label='Lsig')
    for p in Pain:
        plt.axvline(x=p, color='r', linestyle='--', label='Pain')
    plt.legend()
    plt.title(f'{title} ')
    plt.show()

def sigRL(Rsig:list = None,Lsig:list = None,title:str = None,Sampling_frequency = 120,size=(20, 2)):
    """用於展示左右腳訊號，並用於比較"""
    lenR,lenL = len(Rsig),len(Lsig);
    Min,Sec = int(round(lenR/Sampling_frequency,2)//60),round(round(lenR/Sampling_frequency,2)%50,2)
    Ry,Rx = np.array(Rsig),np.linspace(0.0,lenR/Sampling_frequency,lenR);
    Ly,Lx = np.array(Lsig),np.linspace(0.0,lenL/Sampling_frequency,lenL);

    fig = plt.figure(figsize=size)
    fig.add_subplot(1,1,1)
    plt.title(f'{title}')# ;time= {Min}m {Sec}s
    plt.plot(Rx, Ry, label='Rsig')
    plt.plot(Lx, Ly, label='Lsig')
    plt.legend()
    plt.show()

def sigpeaks(sig:list = None,Peaks:list = None,title:str = None,pointname:str = 'STep_point',Sampling_frequency = 120,size=(10, 2)):
    """用於展示特徵點位於訊號的位置"""
    peaks = np.array(Peaks)
    
    sigL = len(sig);
    Min,Sec = int(round(sigL/Sampling_frequency,2)//60),round(round(sigL/Sampling_frequency,2)%50,2)
    Sigy,Sigx = np.array(sig),np.linspace(0.0,sigL,sigL);

    fig = plt.figure(figsize=size)
    fig.add_subplot(1,1,1)
    plt.title(f'{title}')
    plt.plot(Sigx, Sigy, label='signal')
    plt.scatter(peaks, Sigy[peaks],s=15, color='r', marker='o', label=pointname)
    plt.legend()
    plt.show()

def print_3D(Displacement,title:str=None):
    displacement = np.array(Displacement)
    # 绘制3D轨迹图
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(displacement[:, 0], displacement[:, 1], displacement[:, 2], label='IMU Path')
    ax.set_zlabel('Z Displacement (m)')
    ax.set_ylabel('Y Displacement (m)')
    ax.set_xlabel('X Displacement (m)')
    
    
    ax.set_title(title)
    ax.legend()
    plt.show()