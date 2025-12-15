from scipy.integrate import cumtrapz

# 累進積分 #
def accumulated_1(signal, fs=120):
    """一階累進積分"""
    # 計算時間間隔
    dt = 1 / fs
    
    # 積分計算速度
    signal_ = cumtrapz(signal, dx=dt, initial=0)
    
    return signal_.tolist()
def accumulated_2(signal, fs=120):
    """二階累進積分"""
    # 計算時間間隔
    dt = 1 / fs
    
    # 積分計算速度
    signal_ = cumtrapz(signal, dx=dt, initial=0)
    signal__ = cumtrapz(signal_, dx=dt, initial=0)
    return signal__

# 累進積分 #

# 辛普森積分 #
import numpy as np
def simpson_1(data, fs=120):
    """
    應用辛普森規則對資料點列表進行累積積分。
    
    Args:
    data (list or np.array): List of data points representing function values.
    delta_x (float): The spacing between consecutive data points.
    
    Returns:
    list: 與輸入資料長度相同的累積積分值數組。
    """
    dt = 1 / fs
    n = len(data)
    cumulative_integral = np.zeros(n)  # 儲存累積積分值的數組
    
    if n < 3:
        return cumulative_integral  # 沒有足夠的數據來應用辛普森規則
    
    # 如果需要，初始化積分數組的第一個元素
    cumulative_integral[1] = (data[0] + data[1]) * dt / 2  # 
    
    for i in range(2, n):
        # 將辛普森法則應用於三點線段
        segment_integral = (data[i-2] + 4 * data[i-1] + data[i]) * dt / 3
        cumulative_integral[i] = cumulative_integral[i-2] + segment_integral
    
    # 在已知辛普森積分點之間進行線性內插以獲得更平滑的曲線
    for i in range(3, n, 2):
        cumulative_integral[i-1] = (cumulative_integral[i-2] + cumulative_integral[i]) / 2
    
    return cumulative_integral.tolist()
def simpson_2(data, fs=120):
    return simpson_1(simpson_1(data,fs),fs)

# 行進距離
def pathlength(signal,fs=120):
    pathlen = 0
    for sig in signal:
        pathlen += abs(sig)
    return pathlen/fs
