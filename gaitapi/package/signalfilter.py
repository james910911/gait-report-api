from package.filter import bw_low,SG_filter,mean_filter_1d




class SignalFilter:
    """
    將 (1)校正訊號 經過濾波成兩種訊號：
    (2_1)濾波訊號
    1 accx  巴特沃斯低通濾波 15 Hz
    2 accy  巴特沃斯低通濾波 15 Hz
    3 accz  巴特沃斯低通濾波 15 Hz
    4 gyrox 巴特沃斯低通濾波 30 Hz
    5 gyroy 巴特沃斯低通濾波 30 Hz
    6 gyroz 巴特沃斯低通濾波 30 Hz

    (2_2)特徵濾波訊號
    1 accx  巴特沃斯低通濾波 15 Hz
    2 accy  巴特沃斯低通濾波 15 Hz
    3 accz  巴特沃斯低通濾波 15 Hz
    4 gyrox SG 濾波 window = 21,order = 3
    5 gyroy SG 濾波 window = 21,order = 3
    6 gyroz SG 濾波 window = 21,order = 3
    """
    def __init__(self,Signal):
        self.signal = Signal

        self.side = ['r','l']
        self.sig  = ['acc','gyro','mag']
        self.axis = ['x','y','z']

        self.filter1()
        self.filter2()
        self.filter3()

    def filter1(self):
        """
        (2_1)濾波訊號：
        1 accx  巴特沃斯低通濾波 15 Hz
        2 accy  巴特沃斯低通濾波 15 Hz
        3 accz  巴特沃斯低通濾波 15 Hz
        4 gyrox 巴特沃斯低通濾波 30 Hz
        5 gyroy 巴特沃斯低通濾波 30 Hz
        6 gyroz 巴特沃斯低通濾波 30 Hz
        """
        self.signal1 = {}

        for side in self.side:
            for sig in self.sig:
                for axis in self.axis:
                    if sig == 'acc':
                        self.signal1[f'{side}{sig}{axis}'] = bw_low(self.signal[f'{side}{sig}{axis}'],[5])
                    elif sig == 'gyro':
                        if sig == 'x':
                            self.signal1[f'{side}{sig}{axis}'] = bw_low(self.signal[f'{side}{sig}{axis}'],[3])
                        else:
                            self.signal1[f'{side}{sig}{axis}'] = bw_low(self.signal[f'{side}{sig}{axis}'],[3])
                    elif sig == 'mag':
                        self.signal1[f'{side}{sig}{axis}'] = self.signal[f'{side}{sig}{axis}']
                    else:
                        print('SignalFilter/filter1：ERROR')

    def filter2(self):
        """
        (2_2)特徵濾波訊號：
        1 accx  巴特沃斯低通濾波 15 Hz
        2 accy  巴特沃斯低通濾波 15 Hz
        3 accz  巴特沃斯低通濾波 15 Hz
        4 gyrox SG 濾波 window = 21,order = 3
        5 gyroy SG 濾波 window = 21,order = 3
        6 gyroz SG 濾波 window = 21,order = 3
        """
        self.signal2 = {}

        for side in self.side:
            for sig in self.sig:
                for axis in self.axis:
                    if sig == 'acc':
                        self.signal2[f'{side}{sig}{axis}'] = SG_filter(self.signal[f'{side}{sig}{axis}'])
                    elif sig == 'gyro':
                        self.signal2[f'{side}{sig}{axis}'] = SG_filter(self.signal[f'{side}{sig}{axis}'])
                    elif sig == 'mag':
                        self.signal2[f'{side}{sig}{axis}'] = self.signal[f'{side}{sig}{axis}']
                    else:
                        print('SignalFilter/filter1：ERROR')

    def filter3(self):
            """
            (2_1)濾波訊號：
            1 accx  巴特沃斯低通濾波 15 Hz
            2 accy  巴特沃斯低通濾波 15 Hz
            3 accz  巴特沃斯低通濾波 15 Hz
            4 gyrox 巴特沃斯低通濾波 30 Hz
            5 gyroy 巴特沃斯低通濾波 30 Hz
            6 gyroz 巴特沃斯低通濾波 30 Hz
            """
            self.signal3 = {}

            for side in self.side:
                for sig in self.sig:
                    for axis in self.axis:
                        if sig == 'acc':
                            self.signal3[f'{side}{sig}{axis}'] = mean_filter_1d(bw_low(self.signal[f'{side}{sig}{axis}'],[3]),kernel_size=121)
                        elif sig == 'gyro':
                            if axis == 'x':
                                self.signal3[f'{side}{sig}{axis}'] = bw_low(self.signal[f'{side}{sig}{axis}'],[3])
                            else:
                                self.signal3[f'{side}{sig}{axis}'] = bw_low(self.signal[f'{side}{sig}{axis}'],[2])
                        elif sig == 'mag':
                            self.signal3[f'{side}{sig}{axis}'] = self.signal[f'{side}{sig}{axis}']
                        else:
                            print('SignalFilter/filter3：ERROR')































