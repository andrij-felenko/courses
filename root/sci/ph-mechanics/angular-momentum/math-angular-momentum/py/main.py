import numpy as np

m, a, theta, w = 0.5, 0.3, np.radians(30), 20.0
u = np.array([np.sin(theta), 0.0, np.cos(theta)])    # напрям стрижня
positions = [a * u, -a * u]                           # дві маси на кінцях

# тензор інерції:  I_ab = Σ m (r²·δ_ab − x_a·x_b)
I = np.zeros((3, 3))
for r in positions:
    I += m * (np.dot(r, r) * np.eye(3) - np.outer(r, r))

omega = np.array([0.0, 0.0, w])                       # крутимо навколо ẑ
L = I @ omega
angle = np.degrees(np.arccos(L @ omega / (np.linalg.norm(L) * w)))
print("L =", L.round(3))                              # [-0.779  0.     0.45 ]
print("кут(L, ω) =", round(angle, 1), "°")            # 60.0 °

vals, vecs = np.linalg.eigh(I)                         # головні моменти й осі
print("головні моменти:", vals.round(4))              # [0.  0.09  0.09]
print("вісь при I=0:", vecs[:, 0].round(3))           # напрям стрижня (sin30,0,cos30)
