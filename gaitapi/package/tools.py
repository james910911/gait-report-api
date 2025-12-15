import json,os
import math
import pandas as pd
import numpy as np

from scipy.interpolate import interp1d

### 檔案(讀取/存檔) ###
class openfile:
    """ 
    讀取 (檔案 / 資料) 
    file = openfile(folderpath = '可以先輸入檔案所處的資料夾；也可以不輸入')
    也可以在 function 直接輸入檔案位置
    """
    def __init__(self,folderpath = None):
        self.folderpath = folderpath
        self.__Judge()                  # 判斷資料夾位置是否與檔名分開輸入

    def __Judge(self):
        """
        判斷資料夾位置是否與檔名分開輸入
        self.judge = True  # 分開輸入

        self.judge = False # 在 function 中一起輸入
        """
        if self.folderpath != None:
            self.judge = True
        else:
            self.judge = False

    def readexcel(self, filename:str=None):
        """ 
        讀取 excel 資料：

        當工作表只有一個時 ->
        dict = {feature1：[],feature2：[],feature3：[]}

        當工作表有多個時 ->
        dict = {工作表1：{},工作表2：{},工作表3：{}}
        """
        if self.judge:  # 判斷資料夾位置是否與檔名分開輸入
            path = os.path.join(self.folderpath, filename)
        else:
            path = filename

        
        xls = pd.ExcelFile(path, engine='openpyxl') # 判斷Excel檔中工作表數量
        number_of_sheets = len(xls.sheet_names)

        if number_of_sheets == 1:       # 判斷 Excel 中有幾個工作表
            # 如果只有一個工作表，使用原有方法讀取
            Data_f = pd.read_excel(path)
            data_dict = Data_f.to_dict('list')
            data = {k: [x for x in v if pd.notna(x)] for k, v in data_dict.items()}
            return data
        else:
            # 如果有多於一個工作表，讀取所有工作表到一個字典
            sheets_dict = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
            for key,value in sheets_dict.items():

                data_dict = value.to_dict('list')
                sheet = {k: [x for x in v if pd.notna(x)] for k, v in data_dict.items()}
                sheet.pop('Unnamed: 0')
                sheets_dict[key] = sheet
                
            return sheets_dict
    
    def readjson(self,filename:str = None):
        """ 讀取 json 訊號 """
        if self.judge == True:
            path = os.path.join(self.folderpath,filename)
        else:
            path = filename
        
        with open(path, 'r') as file:# 讀檔
            signal = json.load(file)
        return signal
    
class savefile:
    """ 存取 (檔案 / 資料) """
    def __init__(self,folderpath):
        self.folderpath = folderpath

    def saveexcel(self,filename:str = None,new_signal:dict = None):
        """將 dict 存成 xlsx 檔"""
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in new_signal.items()]))
        path = os.path.join(self.folderpath,filename)
        df.to_excel(path, index=False)
    
    def saveexcelRL(self,filename:str = None,signal:dict = None):
        """
        將 dict 存成 xlsx 檔
        將 dict 分為兩個(左右)工作表 進行存檔
        """
        dfr = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in signal['r'].items()]))
        dfl = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in signal['l'].items()]))
        path = os.path.join(self.folderpath,filename)
        with pd.ExcelWriter(path) as writer:
            dfr.to_excel(writer,sheet_name='Rfeature')
            dfl.to_excel(writer,sheet_name='Lfeature')

    def savejson(self,filename:str = None,new_signal:dict = None):
        """將 dict 存成 json 檔"""
        path = os.path.join(self.folderpath,filename)
        with open(path, "w") as json_file:
            json.dump(new_signal, json_file)
### 檔案(讀取/存檔) ###

# 讀取病患基本資料 #
def basicdata(xlsxaddr,patient,types: list = None) -> list:
    """ 讀取病患基本資料 """
    # patient 報錯
    if patient is None:
        raise ValueError("The 'patient' parameter is required and must be an integer.")
    
    ## 正式運作
    try:
        data_ = openfile()
        data = data_.readexcel(xlsxaddr)
        output = [data[n][patient] for n in types]
    except Exception as e:
        print(f"Error reading basic patient data: {e}")
        data = {}
    return output

def Number_of_Data(information):
    """獲取當前資料筆數"""
    data_ = openfile()
    data = data_.readexcel(information)
    return len(data['time'])
# 讀取病患基本資料 #

### 生成資料檔名 ###
class GenName:
    def __init__(self,xlsxaddr,patient):
        self.xlsxaddr = xlsxaddr
        self.patient = patient

        if self.patient is None:    # patient 報錯
            raise ValueError("The 'patient' parameter is required and must be an integer.")
        
        # 所需獲取參數值
        types = ['Name','time']
        self.data = basicdata(self.xlsxaddr,self.patient,types)

        # 生成檔名
        self.Filename()
        self.Excelfilename()
        self.Jsonfilename()

    def Filename(self):
        """ 給出對應病患的 xlsx檔名 """
        self.filename = f"{self.data[0]}_{self.data[1]}"

    def Excelfilename(self):
        """ 給出對應病患的 xlsx檔名 """
        self.excelfilename = f"{self.data[0]}_{self.data[1]}.xlsx"

    def Jsonfilename(self):
        """ 給出對應病患的 json檔名 """
        self.jsonfilename = f"{self.data[0]}_{self.data[1]}.json"

### 生成資料檔名 ###



### list 處理工具 ###
def reverselist(list_:list=None):
    """將輸入的list乘上(-1)"""
    return (-np.array(list_)).tolist()
def sublist(list_:list=None,num = None):
    """將輸入的list減num"""
    return (np.array(list_) - num).tolist()
def multlist(list_:list=None,num = None):
    """將輸入的list乘num"""
    return (np.array(list_) * num).tolist()
def dividelist(list_:list=None,num = None):
    """將輸入的list乘num"""
    return (np.array(list_) / num).tolist()
def list_str2float(list_:list=None):
    """將輸入的list中的str轉為float"""
    return [float(p) for p in list_]
def list_float2str(list_:list=None):
    """將輸入的list中的float轉為str"""
    return [str(p) for p in list_]
def find_transitions(data:list=None):
    """尋找list中與上一個數值不同的位置"""
    # 判斷空列表的情況
    if not data:
        return []
    
    # 初始化存儲變化位置的列表
    transitions = []
    
    # 遍歷列表，從第二個元素開始比較
    for i in range(1, len(data)):
        if i == 0:
            pass
        elif data[i] != data[i-1]:
            transitions.append(i)
    
    return transitions
def closestindex(list_: list = None, num = None):
    """找到 list_(已完成排序) 中最靠近 num 的值的 index"""
    if (list_ is None) or (num is None):
        raise ValueError("list_ and num must be provided")
    if not list_:
        raise ValueError("list_ cannot be empty")

    # 初始化左右邊界
    left, right = 0, len(list_) - 1

    # 二分搜索
    while left < right:
        mid = (left + right) // 2
        if list_[mid] < num:
            left = mid + 1
        else:
            right = mid

    # 比較左右兩個值，找到最接近 num 的索引
    if left == 0:
        return 0
    if left == len(list_):
        return len(list_) - 1

    if abs(list_[left] - num) < abs(list_[left - 1] - num):
        return left
    else:
        return left - 1

    
    
### list 處理工具 ###

### 將陣列resize成目標大小 ###
def resize_array(original_array, target_length):
    # 創建原始陣列的索引
    original_indices = np.arange(0, len(original_array))
    
    # 創建目標長度的新索引
    target_indices = np.linspace(0, len(original_array) - 1, num=target_length)
    
    # 創建插值函數
    interpolation_function = interp1d(original_indices, original_array, kind='linear')
    
    # 使用插值函數得到新的陣列
    resized_array = interpolation_function(target_indices)
    
    return resized_array.tolist()
### 將陣列resize成目標大小 ###



def sizejudgment(r,l):
    """判別左右數值大小"""
    if r < l:
        return 'r'
    elif r > l:
        return 'l'
    else:
        return 'same'
    
def ACC_list2list(X:list=None,Y:list=None,Z:list=None):
    """把Acc 的 dict 轉為list """
    acc = []
    for x,y,z in zip(X,Y,Z):
        acc.append([x,y,z])
    return acc

def deg2rad(Signal):
    """把角速度由(角度/s)變成(弧度/s)"""
    signal = np.array(Signal) * (math.pi / 180)
    return signal.tolist()

## os path 處理 ##
import os
def PreviousDirectory(path:str=None,
                      pre :int=0):
    """尋找當前路徑的上幾層"""
    p = path
    for i in range(pre):
        p = os.path.dirname(p)
    return p
## os path 處理 ##

# 讀取excel的值 #
def finddata(file:dict=None,
             type:str=None,
             position:str=None):
    """
    讀取excel的值
    input
    file：所要讀取的檔案
    type：橫軸座標
    position：縱軸座標

    """
    vertical_name = list(file.keys())[0]
    p = file[vertical_name].index(position)
    return file[type][p]