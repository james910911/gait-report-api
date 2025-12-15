from package.calculus import accumulated_2,accumulated_1,simpson_2,simpson_1,pathlength
from package.tools import closestindex
import numpy as np

class Calculation:
    """
    透過輸入資料計算'步態參數'
    """
    def __init__(self,Position,Angle,Feature,Height,height=170,fs=120):
        # 輸入資料
        self.Feature = Feature    # 特徵時間_分類
        self.Position = Position  # 移動距離
        self.Angle = Angle        # 轉動角度 訊號
        self.fs = fs              # 採樣頻率
        self.Height = Height      # 受測者身高
        self.height = height      # 固定身高
        self.HeightRATE = height/Height # 身高比例

        self.create()

        self.gaitevent()

        ### 參數計算 ###
        # 時相參數 #
        self.SwingPhase()
        self.StancePhase()
        self.DoubleStancePhase()

        # 時間參數 #
        self.SwingTime()
        self.StanceTime()
        self.DoubleStanceTime()
        self.Cadence()
        self.GCI()
        self.GCP3()
        self.GCP5()

        # 空間參數 #
        self.StraightStride()
        self.StrideHeight()
        # self.Offsets()

        # 運動學參數 #
        self.SwingAngle()
        self.StanceAngle()
        ### 參數計算 ###

        self.classification()

    def create(self):
        self.output = {}

        self.output['r'] = {}
        self.output['l'] = {}

    def gaitevent(self):
        """步態事件標記"""
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2]['InitialContact'] = []
            self.output[side2]['ToeOff'] = []
            self.output[side2]['End'] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                self.output[side2]['InitialContact'].append(i)
                self.output[side2]['ToeOff'].append(t)
                self.output[side2]['End'].append(e)

    ### 參數計算 ###
    # 時相參數 #
    def SwingPhase(self):
        """計算擺盪時間比例"""
        name = 'SwingPhase'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                cycle,swing = e-i,e-t
                Swing = round(((swing)/(cycle))*100,2)
                self.output[side2][name].append(Swing)

    def StancePhase(self):
        """計算站立時間比例"""
        name = 'StancePhase'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                cycle,stance = e-i,t-i
                Stance = round((stance/cycle)*100,2)
                self.output[side2][name].append(Stance)

    def DoubleStancePhase(self):
        """計算雙重站立時間比例"""
        name = 'DoubleStancePhase'
        for side1,side2,side3 in zip(['Rfeature','Lfeature'],['Rfeature','Lfeature'],['r','l']):
            self.output[side3][name] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                closestep = closestindex(self.Feature[side2]['InitialContact'],i)
                closeswing = self.Feature[side2]['End'][closestep] - self.Feature[side2]['ToeOff'][closestep]
                cycle,swing = e-i,e-t
                stance = round(((cycle-swing-closeswing)/cycle)*100,2)
                self.output[side3][name].append(stance)
    # 時間參數 #
    def SwingTime(self):
        """計算擺盪時間"""
        name = 'SwingTime'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                swing = e-t
                Swing = round((swing/self.fs),2)
                self.output[side2][name].append(Swing)

    def StanceTime(self):
        """計算站立時間比例"""
        name = 'StanceTime'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                stance = t-i
                Stance = round((stance/self.fs),2)
                self.output[side2][name].append(Stance)
    def DoubleStanceTime(self):
        """計算雙重站立時間比例"""
        name = 'DoubleStanceTime'
        for side1,side2,side3 in zip(['Rfeature','Lfeature'],['Rfeature','Lfeature'],['r','l']):
            self.output[side3][name] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                closestep = closestindex(self.Feature[side2]['InitialContact'],i)
                closeswing = self.Feature[side2]['End'][closestep] - self.Feature[side2]['ToeOff'][closestep]
                cycle,swing = e-i,e-t
                stance = round(((cycle-swing-closeswing)/self.fs),2)
                self.output[side3][name].append(stance)
    def Cadence(self):
        """計算步頻"""
        name = 'Cadence'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            for i,e in zip( self.Feature[side1]['InitialContact'],
                            self.Feature[side1]['End']):
                cad = round(60*(self.fs/(e-i)),2)
                self.output[side2][name].append(cad)
    def GCI(self):
        """計算一步時長"""
        name = 'GCI'
        
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            LEN = len(self.Feature[side1]['Class'])
            for i,c in enumerate(self.Feature[side1]['Class']):
                p = self.Feature[side1]['End'][i] - self.Feature[side1]['InitialContact'][i]
                p = round(p / self.fs,2)
                self.output[side2][name].append(p) 
    def GCP3(self):
        """計算五步時長"""
        name = '3GCP'
        
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            LEN = len(self.Feature[side1]['Class'])
            for i,c in enumerate(self.Feature[side1]['Class']):
                p = 0
                for s in range(i-1,i+2):
                    if s < 0:
                        s_ = 0
                    if s < LEN:
                        s_ = s
                    else:
                        s_ = LEN - 1
                    p += (self.Feature[side1]['End'][s_] - self.Feature[side1]['InitialContact'][s_])
                p = round(p / self.fs,2)
                self.output[side2][name].append(p) 
    def GCP5(self):
        """計算五步時長"""
        name = '5GCP'
        
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][name] = []
            LEN = len(self.Feature[side1]['Class'])
            for i,c in enumerate(self.Feature[side1]['Class']):
                p = 0
                for s in range(i-2,i+3):
                    if s < 0:
                        s_ = 0
                    if s < LEN:
                        s_ = s
                    else:
                        s_ = LEN - 1
                    p += (self.Feature[side1]['End'][s_] - self.Feature[side1]['InitialContact'][s_])
                p = round(p / self.fs,2)
                self.output[side2][name].append(p) 
    # 空間參數 #
    # 直線距離
    def StraightStride(self):
        """計算直線步幅"""
        name = 'StraightStride'
        axis = 'x'
        
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][f'{name}'] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                if not(isinstance(t,int)):
                    t = int(t)
                if not(isinstance(e,int)):
                    e = int(e)
                
                p = [abs(self.Position[f'{side2}acc{axis}'][n+1] - self.Position[f'{side2}acc{axis}'][n]) for n in range(i,e)]
                para = sum(p)
                # para = sum(self.Position[f'{side2}acc{axis}'][i:e])
                # para = -(self.Position[f'{side2}acc{axis}'][e] - self.Position[f'{side2}acc{axis}'][t])
                # para = max(self.Position[f'{side2}acc{axis}'][i:e]) - min(self.Position[f'{side2}acc{axis}'][i:e])
                self.output[side2][f'{name}'].append(round(para*self.HeightRATE,2))
    def StrideHeight(self):
        """計算步伐高度"""
        name = 'StrideHeight'
        axis = 'y'
        
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][f'{name}'] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                if not(isinstance(t,int)):
                    t = int(t)
                if not(isinstance(e,int)):
                    e = int(e)
                
                # p = [abs(self.Position[f'{side2}acc{axis}'][n+1] - self.Position[f'{side2}acc{axis}'][n]) for n in range(i,e)]
                # para = sum(p)
                # para = sum(self.Position[f'{side2}acc{axis}'][i:e])
                para = max(self.Position[f'{side2}acc{axis}'][t:e]) - min(self.Position[f'{side2}acc{axis}'][t:e])
                self.output[side2][f'{name}'].append(round(para*self.HeightRATE,2))
    def Offsets(self):
        """計算左右方向偏移量"""
        name = 'Offsets'
        axis = 'y'
        
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2][f'{name}'] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                if not(isinstance(t,int)):
                    t = int(t)
                if not(isinstance(e,int)):
                    e = int(e)
                
                # p = [abs(self.Position[f'{side2}acc{axis}'][n+1] - self.Position[f'{side2}acc{axis}'][n]) for n in range(i,e)]
                # para = sum(p)
                # para = sum(self.Position[f'{side2}acc{axis}'][i:e])
                para = max(self.Position[f'{side2}acc{axis}'][t:e]) - min(self.Position[f'{side2}acc{axis}'][t:e])
                self.output[side2][f'{name}'].append(para)


    # 運動學參數 #
    def SwingAngle(self):
        """計算 擺盪時期 角度變化 """
        name = 'SwingAngle'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            for a in ['x','y','z']:
                self.output[side2][f'{name}{a}'] = []
            for t,e in zip( self.Feature[side1]['ToeOff'],
                            self.Feature[side1]['End']):
                if not(isinstance(t,int)):
                    t = int(t)
                if not(isinstance(e,int)):
                    e = int(e)
                
                for a in ['x','y','z']:
                    p = [abs(self.Angle[f'{side2}angle{a}'][n+1] - self.Angle[f'{side2}angle{a}'][n]) for n in range(t,e)]
                    angle = sum(p)
                    self.output[side2][f'{name}{a}'].append(angle) 
    def StanceAngle(self):
        """計算 擺盪時期 角度變化 """
        name = 'StanceAngle'
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            for a in ['x','y','z']:
                self.output[side2][f'{name}{a}'] = []
            for i,t,e in zip(self.Feature[side1]['InitialContact'],
                             self.Feature[side1]['ToeOff'],
                             self.Feature[side1]['End']):
                if not(isinstance(t,int)):
                    t = int(t)
                if not(isinstance(e,int)):
                    e = int(e)
                
                for a in ['x','y','z']:
                    # angle = self.Angle[f'{side2}angle{a}'][t] - self.Angle[f'{side2}angle{a}'][i]
                    p = [abs(self.Angle[f'{side2}angle{a}'][n+1] - self.Angle[f'{side2}angle{a}'][n]) for n in range(i,t)]
                    angle = sum(p)
                    self.output[side2][f'{name}{a}'].append(angle) 
    # 參數計算 #
    def classification(self):
        """輸入每步分類"""
        for side1,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            self.output[side2]['Class'] = []
            for c in self.Feature[side1]['Class']:
                self.output[side2]['Class'].append(c)
    
