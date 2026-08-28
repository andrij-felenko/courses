import numpy as np

# node[0..N], node[N] == node[0] (замкнено); струм I; точка P
def biot_savart(node, I, P):
    node = np.asarray(node, dtype=float)
    P = np.asarray(P, dtype=float)
    k = 1e-7                            # μ₀ / 4π
    r_min = 1e-4                        # захист від ділення на ~0 (див. пастки)
    B = np.zeros(3)
    for i in range(len(node) - 1):
        a, b = node[i], node[i + 1]
        dL  = b - a                     # вектор відрізка (напрям = напрям струму)
        mid = (a + b) / 2               # точка прикладання — середина
        r   = P - mid                   # вектор від дроту до P
        rmag = np.linalg.norm(r)        # довжина r
        if rmag < r_min:                # пропустити відрізок біля дроту
            continue
        c = np.cross(dL, r)             # векторний добуток dL × r
        B += k * I * c / rmag**3        # = k·I·(dL × r̂)/r²,  бо r̂/r² = r/r³
    return B                            # вектор (Bx, By, Bz) у теслах
