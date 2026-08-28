import numpy as np

a, b = np.radians(30), np.radians(45)      # кути тросів до горизонту
W = 200.0                                   # вага вивіски, Н

A = np.array([[-np.cos(a), np.cos(b)],      # рядок ΣFx = 0
              [ np.sin(a), np.sin(b)]])     # рядок ΣFy = 0
rhs = np.array([0.0, W])

T1, T2 = np.linalg.solve(A, rhs)
print(f"T1 = {T1:.1f} Н,  T2 = {T2:.1f} Н")   # → T1 = 146.4 Н,  T2 = 179.3 Н

# перевірка: чи справді сили гасяться?
Fx = -T1*np.cos(a) + T2*np.cos(b)
Fy =  T1*np.sin(a) + T2*np.sin(b) - W
print(f"ΣFx = {Fx:.2e},  ΣFy = {Fy:.2e}")     # → ≈ 0, ≈ 0
