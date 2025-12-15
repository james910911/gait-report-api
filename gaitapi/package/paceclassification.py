

class PaceClassification:
    """
    處理以下功能：
    1.判別步伐類別
        (1) 不痛                      ( 0 級)
        (2) 些微疼痛                  ( 1 級)
        (3) 劇烈疼痛                  ( 2 級)
        (4) 位於疼痛轉換期            ( 3 級)
        (5) 轉彎步態、起始步態:不採用 ( 4 級)
    """
    def __init__(self,Gait,TurnArea,Pain):
        self.gait = Gait            # 步態特徵點 (資訊/特徵時間)
        self.turnarea = TurnArea    # 特徵訊號   (資訊/轉彎時段)
        self.pain = Pain            # 疼痛起始時間點

        self.assort = []            # 紀錄步伐種類
        self.create_DICT()          # 創建 dict 放置 : 'Rfeature' 'Lfeature' -> 'InitialContact'、'ToeOff'、'End'、'Classification'
        self.classification()       # 進行分類

    def create_DICT(self):
        """
        生成 self.assort
        紀錄左右腳的'InitialContact'、'ToeOff'、'End'、'Class'
        """
        self.assort = {}
        self.assort['r'],self.assort['l'] = {},{}

        self.assort['r']['InitialContact'] = self.gait['Rfeature']['InitialContact']
        self.assort['l']['InitialContact'] = self.gait['Lfeature']['InitialContact']

        self.assort['r']['ToeOff'] = self.gait['Rfeature']['ToeOff']
        self.assort['l']['ToeOff'] = self.gait['Lfeature']['ToeOff']
        
        self.assort['r']['End'] = self.gait['Rfeature']['End']
        self.assort['l']['End'] = self.gait['Lfeature']['End']

        self.assort['r']['Class'] = []
        self.assort['l']['Class'] = []


    def classification(self):
        """將每步進行分類"""
        # 疼痛分級
        for side,side2 in zip(['Rfeature','Lfeature'],['r','l']):
            for n,(i,e) in enumerate(zip(self.gait[side]['InitialContact'],
                                        self.gait[side]['End'])):
                # 疼痛分類
                if i >= self.pain['Start'][0] and e <= self.pain['End'][0]:
                    self.assort[side2]['Class'].append(0) # ( 0 級)

                elif i >= self.pain['Start'][1] and e <= self.pain['End'][1]:
                    self.assort[side2]['Class'].append(1) # ( 1 級)

                elif i >= self.pain['Start'][2] and e <= self.pain['End'][2]:
                    self.assort[side2]['Class'].append(2) # ( 2 級)
                    
                else:
                    self.assort[side2]['Class'].append(3) # ( 3 級)
        # 轉彎分類
        for side,side2,side3 in zip(['Rfeature','Lfeature'],['R','L'],['r','l']):
            for n,(i,e) in enumerate(zip(self.gait[side]['InitialContact'],
                                         self.gait[side]['End'])):
                # 轉彎分類
                for st,en in zip(self.turnarea[f'{side2}st'],self.turnarea[f'{side2}en']):
                    if i >= st and e <= en:
                        # 步伐全在轉彎區域
                        self.assort[side3]['Class'][n] = 4 # ( 4 級)
                        break

                    elif i >= st and i <= en:
                        # 步伐前面在轉彎區域
                        self.assort[side3]['Class'][n] = 4 # ( 4 級)
                        break
                    
                    elif e >= st and e <= en:
                        # 步伐後面在轉彎區域
                        self.assort[side3]['Class'][n] = 4 # ( 4 級)
                        break



def removeturn(para:dict = None,value = 4,status = True):
    """去除被分類在轉彎性質的參數"""
    output = {}
    if status:
        Side = ['r','l']
    else:
        Side = ['Rfeature','Lfeature']
    for side,side2 in zip(['Rfeature','Lfeature'],Side):
        output[side2] = {}
        indices_to_keep = [i for i, val in enumerate(para[side]['Class']) if val != value]
        
        for key in para[side].keys():
            output[side2][key] = [para[side][key][i] for i in indices_to_keep]
    
    return output