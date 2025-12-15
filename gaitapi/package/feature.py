from scipy.signal import find_peaks
from package.tools import reverselist

def FindPeaks(sig = None,width = None,height = None,reverse=False):
    """尋找訊號的特徵"""
    if reverse: # 判斷訊號是否顛倒
        sig = reverselist(sig)
        height = -height
    return find_peaks(sig,width = width,height = height)[0]

def createfeaturedict():
    """創建放置特徵時間點的dict"""
    return {'InitialContact'        :[],
            'OppositeToeOff'        :[],
            'HeelRise'              :[],
            'OppositeInitialContact':[],
            'ToeOff'                :[],
            'FeetAdjacent'          :[],
            'TibiaVertical'         :[]}

def find_previous_peaks(signal, valleys,h):
    """
    尋找波谷前的第一個波峰
    開發時用於尋找 Gyro z軸 的特徵訊號
    """
    peak_indices = []
    for valley in valleys:
        for i in range(valley-1, 0, -1):
            # 检查是否为波峰：比前后点都大
            if signal[i] > signal[i+1] and signal[i] > signal[i-1] and signal[i] >= h:
                peak_indices.append(i)
                break
    return peak_indices
