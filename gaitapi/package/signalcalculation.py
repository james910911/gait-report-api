"""
輸入訊號進行計算
1.角度

"""
from package.calculus import simpson_1
from package.filter import mean_filter_1d
import numpy as np
def angle(gyrox:dict=None,gyroy:dict=None,gyroz:dict=None,order=2,kernel_size=1001):
    """輸入訊號計算角度"""
    if not(gyrox == None) and not(gyroy == None) and not(gyroz == None):
        anglex,angley,anglez = np.array(gyrox),np.array(gyroy),np.array(gyroz)
        # 累進積分
        anglex,angley,anglez = simpson_1(anglex),simpson_1(angley),simpson_1(anglez)
        # 均值濾波
        anglex,angley,anglez = mean_filter_1d(anglex,order=order,kernel_size=kernel_size),mean_filter_1d(angley,order=order,kernel_size=kernel_size),mean_filter_1d(anglez,order=order,kernel_size=kernel_size)
        # 回傳角度訊號
        return anglex,angley,anglez
    else:
        print("package/signalcalculation/angle/無訊號輸入")
        return [],[],[]



