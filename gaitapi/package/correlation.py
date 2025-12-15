"""
放置互相關運算之function
"""



import numpy as np
def correlation_array(signal1, signal2):
    try:
        correlation = np.correlate(signal1 - np.mean(signal1), signal2 - np.mean(signal2), mode='full')
        return correlation
    except:
        return []
    
def correlation_num(signal1, signal2):
    try:
        # 歸一化信號，移除均值
        signal1_normalized = signal1 - np.mean(signal1)
        signal2_normalized = signal2 - np.mean(signal2)
        
        # 計算互相關
        correlation = np.correlate(signal1_normalized, signal2_normalized, mode='full')
        # 歸一化互相關
        normalization_factor = np.sqrt(np.sum(signal1_normalized**2) * np.sum(signal2_normalized**2))
        normalized_correlation = correlation / normalization_factor
        
        # 找到最大的歸一化互相關值
        max_correlation = np.max(np.abs(normalized_correlation))
        return max_correlation
    except:
        return 0