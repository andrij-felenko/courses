import numpy as np
import matplotlib.pyplot as plt

# Завантаження даних з файлу
data = np.loadtxt("poincare_section.dat")
x_coords = data[:, 0]
v_coords = data[:, 1]

plt.figure(figsize=(8, 6), dpi=150)
plt.scatter(x_coords, v_coords, s=0.5, c='#8e44ad', alpha=0.7, marker='.')
plt.title("Переріз Пуанкаре осцилятора Дуффінга", fontsize=14, fontweight='bold')
plt.xlabel("Координата зміщення x", fontsize=12)
plt.ylabel("Швидкість v = dx/dt", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("poincare_plot.png")
plt.show()
