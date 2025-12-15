# 旋轉矩陣 #
import numpy as np
def __euler_to_rotation_matrix(yaw, pitch, roll):
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    R = Rz @ Ry @ Rx
    return R

def correct_accelerations(accelerations, yaws, pitches, rolls):
    corrected_accelerations = np.zeros_like(accelerations)
    for i in range(len(accelerations)):
        R = __euler_to_rotation_matrix(yaws[i], pitches[i], rolls[i])
        corrected_accelerations[i] = np.linalg.inv(R) @ accelerations[i]
    return corrected_accelerations
# 旋轉矩陣 #

# 四元數校正 # 
import numpy as np
import quaternion

def correct_acc(AccX,AccY,AccZ, Q):
    """
    使用四元數校正加速度向量。
    
    參數:
    acc_vector (array): 原始三軸加速度向量，格式為 [ax, ay, az]。
    q (quaternion): 用於校正的四元數。
    
    返回:
    array: 校正後的三軸加速度向量。
    """
    accx,accy,accz = [],[],[]
    for ax,ay,az,q_ in zip(AccX,AccY,AccZ,Q):
        acc_vector = [ax,ay,az]
        q0,q1,q2,q3 = q_
        q = np.quaternion(q0,q1,q2,q3)
        # 將加速度向量轉換為四元數
        acc_quat = np.quaternion(0, *acc_vector)
        
        # 計算校正後的加速度四元數
        corrected_acc_quat = q * acc_quat * q.conjugate()
        
        # 提取校正後的加速度向量
        corrected_acc_vector = quaternion.as_float_array(corrected_acc_quat)[1:]  # 只取虛部

        accx.append(corrected_acc_vector[0])
        accy.append(corrected_acc_vector[1])
        accz.append(corrected_acc_vector[2])
        
    return accx,accy,accz

def QuaternionCalculations(AngleX,AngleY,AngleZ):
    """
    通過陀螺儀旋轉角度獲得四元數

    輸入 : 
    AngleX  X 軸 陀螺儀 積分(Roll  Axis)
    AngleY  Y 軸 陀螺儀 積分(Yaw   Axis) 
    AngleZ  Z 軸 陀螺儀 積分(Pitch Axis)
    輸出 : 
    quaternion(list) : 
    訊號四元數
    """
    quaternions = []
    for ax,ay,az in zip(AngleX,AngleY,AngleZ):
        qx,qy,qz = genquaternion(ax,'x'),genquaternion(ay,'y'),genquaternion(az,'z')
        quaternions.append(multiply_quaternions(qx,multiply_quaternions(qy,qz)))
    return quaternions

def genquaternion(angle_deg,axis='x'):
    """輸入'角度'與'軸'計算四元數"""
    # 先將 '度數' 單位轉成 '弧度'
    angle_rad = np.radians(angle_deg)
    half_angle = angle_rad / 2
    
    # 計算半角的餘弦(cos)和正弦(sin)
    cos_half_angle = np.cos(half_angle)
    sin_half_angle = np.sin(half_angle)
    
    # 初始化四元數分量
    q0 = cos_half_angle
    q1 = q2 = q3 = 0
    
    # 確定軸並設定適當的四元數分量
    if axis == 'x':
        q1 = sin_half_angle
    elif axis == 'y':
        q2 = sin_half_angle
    elif axis == 'z':
        q3 = sin_half_angle
    else:
        raise ValueError("Invalid axis. Axis must be 'x', 'y', or 'z'.")
    
    return (q0, q1, q2, q3)

def multiply_quaternions(q1, q2):
    """
    兩個四元數相乘

    Args:
    q1 (tuple): 第一個四元數 (q0, q1, q2, q3).
    q2 (tuple): 第二個四元數 (q0, q1, q2, q3).

    Returns:
    tuple: 相乘後得到的四元數。
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    # 計算兩個四元數的乘積
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

    return (w, x, y, z)
# 四元數校正 # 