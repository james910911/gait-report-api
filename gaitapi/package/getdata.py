import os
from package.tools import openfile,savefile,GenName,reverselist,sublist

# 讀取 訊號檔
class getdata:
    def __init__(self,xlsxaddr,foldaddr,patient,gravity = True):
        # "輸入值" 複製
        self.xlsxaddr = xlsxaddr    # "病患狀況.xlsx" 的 path
        self.foldaddr = foldaddr    # josn 檔 的 path
        self.patient = patient      # 病患序號
        self.gravity = gravity      # 是否扣除重力加速度

        # 參數產生
        self.Genname()              # 訊號檔名 "self.excelfilename"、"self.jsonfilename"
        self.Jsonfilepath()         # 訊號path "self.sigpath"
        self.sigallget()            # 獲取訊號檔 "self.Signal"

        # 判斷是不是讀取 "(0)純訊號"；
        # 如果是"(0)純訊號"則無需處理
        if len(self.Signal) == 33:
            self.sigprocess()       # 提取訊號        "self.signal"
            self.PAINpoint()        # 提取疼痛時間點  "self.pain"
        else: 
            self.signal = self.Signal


    def Genname(self):
        name = GenName(xlsxaddr=self.xlsxaddr,patient=self.patient)
        self.excelfilename = name.excelfilename
        self.jsonfilename = name.jsonfilename


    def Jsonfilepath(self):
        """獲取 json檔 path"""
        self.sigpath = os.path.join(self.foldaddr,self.jsonfilename)

    def PAINpoint(self):
        """ 提取疼痛時間點 """
        self.pain = self.Signal['Pain']

    def sigallget(self):
        """讀取訊號檔"""
        data = openfile(folderpath=self.foldaddr)
        self.Signal = data.readjson(filename=self.jsonfilename)

    def sigprocess(self):
        """將訊號檔內的格式整理一下"""
        
        self.signal = {}
        for Key,Value in self.Signal.items():
            # 判別內含物是否為 dict
            if isinstance(Value, dict):
                for axis,sig in Value.items():
                    # 1. 將 Key 改成小寫
                    key = Key.lower()
                    # 2. 確認訊號方向
                    if key.startswith("right"):
                        key1 = "r"
                    elif key.startswith("left"):
                        key1 = "l"
                    else:
                        key1 = "x"
                    # 3. 確認訊號種類
                    if key.endswith("acc"):
                        key2 = "acc"
                    elif key.endswith("gyro"):
                        key2 = "gyro"
                    elif key.endswith("mag"):
                        key2 = "mag"
                    else:
                        key2 = "x"
                    
                    # 4. 將訊號放入新分類
                    if (key1 != "x") and (key2 != "x"):
                        self.signal[f"{key1}{key2}{axis}"] = [float(p) for p in sig]
        # 5.accy方位校正
        self.signal['laccy'] = reverselist(self.signal['laccy'])
        if self.gravity:
            self.signal['raccy'] = sublist(self.signal['raccy'],9.8)
            self.signal['laccy'] = sublist(self.signal['laccy'],9.8)
        self.signal['laccy'] = reverselist(self.signal['laccy'])


if __name__ == '__main__':
    for i in [0,1,2,3,4,5,6]:# 0,1,2,3,4,5,6,7,8,9,10
        # 參數宣告
        patient = i
        # 訊號讀取與處理
        Signal = getdata(xlsxaddr= "C:/Users/Ming Hong/Desktop/步態訊號/病患狀況.xlsx",
                        foldaddr= "C:/Users/Ming Hong/Desktop/訊號處理/訊號/(0)補點訊號/",
                        patient = patient)
        # 查看處理結果
        print(i,Signal.jsonfilename)

        # 存檔
        savef = savefile(folderpath="C:/Users/Ming Hong/Desktop/訊號處理/訊號/(0)純訊號/")
        savef.savejson(filename = Signal.jsonfilename,
                    new_signal = Signal.signal)