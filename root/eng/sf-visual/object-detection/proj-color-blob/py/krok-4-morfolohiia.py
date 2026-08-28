import cv2
import numpy as np

kernel = np.ones((3, 3), np.uint8)         # найдешевше ядро 3x3

def erode3(src):
    return cv2.erode(src, kernel)          # білий лише якщо ВСІ сусіди білі

def dilate3(src):
    return cv2.dilate(src, kernel)         # білий якщо ХОЧ ОДИН сусід білий
