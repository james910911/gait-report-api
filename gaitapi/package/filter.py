from scipy.signal import butter,lfilter,savgol_filter
import numpy as np

Sampling_frequency = 120


def signal_to_frequency(signal_list):
    """
    將數位訊號轉換為頻域訊號。

    參數:
    - signal_list: 數位訊號 (list)

    回傳:
    - spectrum: 頻譜 (numpy array)
    """
    # 將 list 轉換為 numpy array
    signal = np.array(signal_list)
    
    # 計算 FFT，得到頻域訊號
    spectrum = np.fft.fft(signal)
    
    
    # 回傳頻率和頻譜
    return np.abs(spectrum).tolist()


# 巴特沃斯濾波器 '低通'濾波
def bw_low(signal:list = None,fre:list = [15],order:int = 5,Sampling_frequency = 120) -> list :
    fs = Sampling_frequency
    b, a = butter(N=order, Wn = fre[0] / (0.5 * fs), btype='lowpass', analog=False)
    # 應用濾波器
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal.tolist()

# 巴特沃斯濾波器 '帶通'濾波
def bw_band(signal:list = None,fre:list = None,order:int = 5,Sampling_frequency = 120) -> list :
    fs = Sampling_frequency
    b, a = butter(N=order, Wn=[fre[0] / (0.5 * fs),fre[1] / (0.5 * fs)], btype='bandpass', analog=False)
    # 應用濾波器
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal.tolist()

# 巴特沃斯濾波器 '高通'濾波
def bw_high(signal:list = None,fre:list = None,order:int = 5,Sampling_frequency = 120) -> list :
    fs = Sampling_frequency
    b, a = butter(N=order, Wn = fre[0] / (0.5 * fs), btype='highpass', analog=False)
    # 應用濾波器
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal.tolist()

# 一維中值濾波
def median_filter_1d(signal:list = None,order:int = None, kernel_size:int = 150) -> list :
    Signal = np.array(signal)
    for t in range(order):
        kernel_radius = kernel_size // 2
        extended_signal = np.pad(Signal, (kernel_radius, kernel_radius), mode='edge')
        filtered_signal = np.zeros(Signal.shape)
        for i,j in enumerate(Signal):
            filtered_signal[i] = np.median(extended_signal[i:i+kernel_size])
        Signal = filtered_signal.copy()
    signal,filtered_signal = np.array(signal),np.array(filtered_signal)
    return (signal-filtered_signal).tolist()

# 一維均值濾波
# def mean_filter_1d(signal:list = None,order:int = None, kernel_size:int = 150) -> list :
#     Signal = np.array(signal)
#     for t in range(order):
#         kernel_radius = kernel_size // 2
#         extended_signal = np.pad(Signal, (kernel_radius, kernel_radius), mode='edge')
#         filtered_signal = np.zeros(Signal.shape)
#         for i,j in enumerate(Signal):
#             filtered_signal[i] = np.mean(extended_signal[i:i+kernel_size])
#         Signal = filtered_signal.copy()
#     signal,filtered_signal = np.array(signal),np.array(filtered_signal)
#     return (signal-filtered_signal).tolist()

# 一維均值濾波
def mean_filter_1d(signal:list = None,order:int = 2, kernel_size:int = 151) -> list :
    Signal = np.array(signal)
    for t in range(order):
        kernel_radius = kernel_size // 2
        # 根據迴圈次數決定濾波方向
        if (t+1) % 2 == 0:
            # 奇數次迴圈：照原本濾波方式
            extended_signal = np.pad(Signal, (kernel_radius, kernel_radius), mode='edge')
            filtered_signal = np.zeros(Signal.shape)
            for i in range(len(Signal)):
                filtered_signal[i] = np.mean(extended_signal[i:i + kernel_size])
        else:
            # 偶數次迴圈：從後向前濾波
            extended_signal = np.pad(Signal, (kernel_radius, kernel_radius), mode='edge')
            filtered_signal = np.zeros(Signal.shape)
            for i in range(len(Signal)-1, -1, -1):
                filtered_signal[i] = np.mean(extended_signal[i:i + kernel_size])
    signal,filtered_signal = np.array(signal),np.array(filtered_signal)
    return (signal-filtered_signal).tolist()

def mean_filter_turn(signal: list = None, order: int = None, kernel_size: int = 151) -> list:
    Signal = np.array(signal)
    for t in range(order):
        kernel_radius = kernel_size // 2
        # 根據迴圈次數決定濾波方向
        if (t+1) % 2 == 0:
            # 奇數次迴圈：照原本濾波方式
            extended_signal = np.pad(Signal, (kernel_radius, kernel_radius), mode='edge')
            filtered_signal = np.zeros(Signal.shape)
            for i in range(len(Signal)):
                filtered_signal[i] = np.mean(extended_signal[i:i + kernel_size])
        else:
            # 偶數次迴圈：從後向前濾波
            extended_signal = np.pad(Signal, (kernel_radius, kernel_radius), mode='edge')
            filtered_signal = np.zeros(Signal.shape)
            for i in range(len(Signal)-1, -1, -1):
                filtered_signal[i] = np.mean(extended_signal[i:i + kernel_size])
        Signal = filtered_signal.copy()
    return filtered_signal.tolist()
# SG filter
def SG_filter(signal:list = None,window_length:int = 21,polyorder:int = 3) -> list:
    signal = np.array(signal);
    Signal = savgol_filter(x=signal,window_length=window_length,polyorder=polyorder)
    return Signal.tolist()

# 凸波濾波器
def Remove_surges(signal:list = None,Windows:int = 0.6,Gap:int = 250):
    signal = np.array(signal);
    asignal,windows = [],int(Windows*Sampling_frequency)
    ROUND = int(np.ceil(len(signal)/windows))
    for r in range(ROUND):
        if r+1 == ROUND:    Sp,Ep = r*windows,len(signal);
        else:               Sp,Ep = r*windows,(r+1)*windows;
        # 判斷 gap 是否大於 Gap值
        if np.max(signal[Sp:Ep]) - np.min(signal[Sp:Ep]) > Gap :
            if abs(np.max(signal[Sp:Ep]) - np.mean(signal[Sp:Ep])) > abs(np.mean(signal[Sp:Ep]) - np.min(signal[Sp:Ep])):
                asignal += np.where(signal[Sp:Ep] > np.min(signal[Sp:Ep]) + Gap//2, np.min(signal[Sp:Ep]), signal[Sp:Ep]).tolist()
            else:
                asignal += np.where(signal[Sp:Ep] < np.min(signal[Sp:Ep]) - Gap//2, np.max(signal[Sp:Ep]), signal[Sp:Ep]).tolist()
        else:
            asignal += signal[Sp:Ep].tolist()
    return np.array(asignal).tolist()