import numpy as np

def histogram2d(x, y, kx, ky):
    """Спільна гістограма пар (x, y): цілі мітки 0…kx−1, 0…ky−1."""
    joint = np.zeros((kx, ky))
    np.add.at(joint, (x, y), 1)        # +1 у клітину (xᵢ, yᵢ) для кожної пари
    return joint

def mutual_information(joint):
    """Плаг-ін оцінка I(X;Y) зі спільної гістограми лічильників, біт."""
    N = joint.sum()
    pxy = joint / N                    # p̂(x, y)
    px = pxy.sum(axis=1, keepdims=True)  # p̂(x) — сума по рядку
    py = pxy.sum(axis=0, keepdims=True)  # p̂(y) — сума по стовпцю
    indep = px @ py                    # p̂(x)·p̂(y) для кожної клітини
    mask = pxy > 0                     # 0·log0 = 0 — порожні клітини пропускаємо
    return float((pxy[mask] * np.log2(pxy[mask] / indep[mask])).sum())
