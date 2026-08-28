import numpy as np

# Інвертувати 3×3 (гомографію). Повертає None, якщо матриця вироджена.
def invert3x3(H):
    det = np.linalg.det(H)
    if abs(det) < 1e-12:
        return None
    return np.linalg.inv(H)

# Яскравість кадру в точці канонічного квадрата (Xc,Yc) — через обернену гомографію.
# Найближчий сусід (INTER_NEAREST, як у OpenCV-aruco); межі кадру перевіряємо.
# Повертає -1, якщо точка вилізла за кадр.
def sample_canonical(img, Hi, Xc, Yc):
    H_img, W = img.shape
    w = Hi[2, 0] * Xc + Hi[2, 1] * Yc + Hi[2, 2]
    if abs(w) < 1e-12:
        return 0
    sx = int((Hi[0, 0] * Xc + Hi[0, 1] * Yc + Hi[0, 2]) / w + 0.5)
    sy = int((Hi[1, 0] * Xc + Hi[1, 1] * Yc + Hi[1, 2]) / w + 0.5)
    if sx < 0 or sx >= W or sy < 0 or sy >= H_img:
        return -1                                   # вилізли за кадр
    return int(img[sy, sx])
