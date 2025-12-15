from package.filter import *
from package.feature import *
# from package.tools import *

def TurnArea(signal:dict=None,points:dict=None,halfarea=480):
    """
    輸入轉彎時間點的中點
    已生成轉彎區域

    points(input):
        全部訊號 : 但在這個FUNCTION只是為了算訊號總長度
    points(input):
        轉彎時間點的中點
    halfarea(input):
        要在'轉彎時間點'往前往後多少點
        將其設為轉彎區域

    turnarea_check(output,dict):
        Rst(key) : 右腳轉彎起始點
        Ren(key) : 右腳轉彎結束點
        Lst(key) : 左腳轉彎起始點
        Len(key) : 左腳轉彎結束點
    """
    turnarea = {}           # 用來放置
    turnarea['Rst'],turnarea['Ren'] = [],[]
    turnarea['Lst'],turnarea['Len'] = [],[]

    for i,(r,l) in enumerate(zip(points['R'],points['L'])):
        turnarea['Rst'].append(r-halfarea)
        turnarea['Ren'].append(r+halfarea)

        turnarea['Lst'].append(l-halfarea)
        turnarea['Len'].append(l+halfarea)

    turnarea_check = {}     # 用來放置
    turnarea_check['Rst'],turnarea_check['Ren'] = [],[]
    turnarea_check['Lst'],turnarea_check['Len'] = [],[]

    count = True
    lenSIG = len(signal['raccx'])
    for side in ['R','L']:
        num = len(turnarea[f'{side}st'])
        for i,(st,en) in enumerate(zip(turnarea[f'{side}st'],turnarea[f'{side}en'])):
            # 判斷此回合是否需要填充數值
            if count:
                if i == num-1:
                    turnarea_check[f'{side}st'].append(st)
                    if en < lenSIG:
                        turnarea_check[f'{side}en'].append(en)
                    else:
                        turnarea_check[f'{side}en'].append(lenSIG)
                else:
                    if en > turnarea[f'{side}st'][i+1]:
                        turnarea_check[f'{side}st'].append(st)
                        turnarea_check[f'{side}en'].append(turnarea[f'{side}en'][i+1])
                        count = False
                    else:
                        turnarea_check[f'{side}st'].append(st)
                        turnarea_check[f'{side}en'].append(en)
                    
                    
            else:
                count = True
    return turnarea_check
