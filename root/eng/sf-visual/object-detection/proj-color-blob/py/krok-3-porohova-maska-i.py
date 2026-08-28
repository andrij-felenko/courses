import numpy as np
import cv2

# помаранчевий — один суцільний діапазон тону
def is_orange(hsv):                        # hsv: масив HxWx3, h2 у 0..179
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return (h >= 10) & (h <= 20) & (s >= 120) & (v >= 60)

# червоний — ДВА діапазони: біля 0 і біля 180 (h2), бо тон перетинає край кола
def is_red(hsv):
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    hue_ok = (h <= 8) | (h >= 172)         # 0..16° АБО 344..360°
    return hue_ok & (s >= 120) & (v >= 60)

def threshold_color(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)  # h2 у 0..179, як вище
    return np.where(is_red(hsv), 255, 0).astype(np.uint8)  # шукаємо червоний маркер
