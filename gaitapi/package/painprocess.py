


class PainPointProcess:
    def __init__(self,Points,Signal):
        """
        將疼痛時段進行預處理
        """
        self.points = Points
        self.lenSIG = len(Signal['raccx'])

        self.p1 = self.anydata(Points['one']) # 判斷有無一級疼痛
        self.p2 = self.anydata(Points['two']) # 判斷有無二級疼痛

        self.precess()          # 修正資料錯誤
        self.levelfirstpoint()  # 找到每個等級的第一個時間點,self.firstpoint

        

    def anydata(self,data):
        """ 判斷data內有無資料 """
        if len(data) > 0:
            return True
        else:
            return False

    def precess(self):
        """
        判斷是否有資料錯誤
        如果有就將其修正
        """
        points = {}
        points['one'],points['two'] = [],[]

        if self.p1:
            if self.points['one'][0] < 0:
                points['one'] = [p + 600  for p in self.points['one'] if p > 0]
            else:
                points['one'] = self.points['one']
        
        if self.p2:
            if self.points['two'][0] < 0:
                points['two'] = [p + 600  for p in self.points['one'] if p > 0]
            else:
                points['two'] = self.points['two']

        self.points = points

    def levelfirstpoint(self):
        """找到每個等級的第一個時間點"""
        self.painarea = {}
        self.painarea['Start'] = []
        self.painarea['End'] = []

        for level in range(3):
            if level == 0:
                # 起始時間點為0
                self.painarea['Start'].append(0)
                if self.p1:
                    self.painarea['End'].append(min(self.points['one']))
                elif self.p2:
                    self.painarea['End'].append(min(self.points['two']))
                else:
                    self.painarea['End'].append(self.lenSIG)
            elif level == 1:
                if self.p1:
                    self.painarea['Start'].append(min(self.points['one']))
                    if self.p2:
                        self.painarea['End'].append(min(self.points['two']))
                    else:
                        self.painarea['End'].append(self.lenSIG)
                else:
                    self.painarea['Start'].append(0)
                    self.painarea['End'].append(0)
            elif level == 2:
                if self.p2:
                    self.painarea['Start'].append(min(self.points['two']))
                    self.painarea['End'].append(self.lenSIG)
                else:
                    self.painarea['Start'].append(0)
                    self.painarea['End'].append(0)
            else:
                print('painprocess/PainPointProcess/levelfirstpoint ->-> ERROR')
