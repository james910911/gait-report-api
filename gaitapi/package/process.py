from package.tools import reverselist



class Process:
    def __init__(self,Signal):
        """
        將 (0)原始訊號 進行以下處理：
        1.相位校正
        2.
        """
        self.signal = Signal    # 訊號導入

        self.side = ['r','l']
        self.sig  = ['acc','gyro','mag']
        self.axis = ['x','y','z']

        self.phasecorr()        # 相位校正
        self.lengthcorr()       # 長度校正

    def phasecorr(self):
        """
        1.相位校正
            1_ accx  左右 反轉
            2_ accy  不變 (在 getdata 反轉過了)
            3_ accz  左右 反轉
            4_ gyrox 右   反轉
            5_ gyroy 不變
            6_ gyroz 右   反轉
        """
        # accx  左右 反轉
        # self.signal['raccx'] = reverselist(self.signal['raccx'])
        # self.signal['laccx'] = reverselist(self.signal['laccx'])
        # accy  不變 (在 getdata 反轉過了)
        self.signal['laccy'] = reverselist(self.signal['laccy'])
        # accz  左右 反轉
        # self.signal['raccz'] = reverselist(self.signal['raccz'])
        # self.signal['laccz'] = reverselist(self.signal['laccz'])
        # gyrox 右   反轉
        self.signal['lgyrox'] = reverselist(self.signal['lgyrox'])
        # gyroy 左右 反轉
        self.signal['rgyroy'] = reverselist(self.signal['rgyroy'])
        self.signal['lgyroy'] = reverselist(self.signal['lgyroy'])
        # gyroz 右   反轉
        self.signal['rgyroz'] = reverselist(self.signal['rgyroz'])

    def lengthcorr(self):
        """
        將訊號校正為等長
        """
        Rlen,Llen = len(self.signal['raccx']),len(self.signal['laccx'])
        if Rlen < Llen:     # 找到較短長度
            shortlen = Rlen
            self.longside = 'L'
            self.longlen  = Llen - Rlen
        else:
            shortlen = Llen
            self.longside = 'R'
            self.longlen  = Rlen - Llen

        for key in self.signal.keys():
            self.signal[key] = self.signal[key][:shortlen]




def angleprocess(Signal):
    """對轉動角度進行方位校正"""
    signal = {}
    
    for a in ['x','y','z']:
        sig = f'angle{a}'

        if a == 'x':
            signal[f'r{sig}'] = Signal[f'r{sig}']
            signal[f'l{sig}'] = reverselist(Signal[f'l{sig}'])
        elif a == 'y':
            signal[f'r{sig}'] = reverselist(Signal[f'r{sig}'])
            signal[f'l{sig}'] = reverselist(Signal[f'l{sig}'])
        else:
            signal[f'r{sig}'] = reverselist(Signal[f'r{sig}'])
            signal[f'l{sig}'] = Signal[f'l{sig}']
    return signal





























