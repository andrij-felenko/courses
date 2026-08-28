# duffing_sim.py — Чисельне інтегрування та візуалізація мовою Python
import numpy as np
import matplotlib.pyplot as plt

def duffing_derivatives(state, t, alpha, beta, delta, gamma, omega):
    x, v = state
    dxdt = v
    dvdt = -delta * v - alpha * x - beta * x**3 + gamma * np.cos(omega * t)
    return np.array([dxdt, dvdt])

def rk4_step(state, t, h, params):
    k1 = duffing_derivatives(state, t, *params)
    k2 = duffing_derivatives(state + 0.5 * h * k1, t + 0.5 * h, *params)
    k3 = duffing_derivatives(state + 0.5 * h * k2, t + 0.5 * h, *params)
    k4 = duffing_derivatives(state + h * k3, t + h, *params)
    return state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

# Параметри системи
params = (-1.0, 1.0, 0.2, 0.3, 1.2)  # alpha, beta, delta, gamma, omega
alpha, beta, delta, gamma, omega = params

period = 2.0 * np.pi / omega
steps_per_period = 400
h = period / steps_per_period

state = np.array([0.1, 0.0])
t = 0.0

# 1. Пропуск перехідного процесу
for _ in range(200 * steps_per_period):
    state = rk4_step(state, t, h, params)
    t += h

# 2. Збір точок перерізу Пуанкаре
poincare_pts = []
for _ in range(3000):
    poincare_pts.append(state.copy())
    for _ in range(steps_per_period):
        state = rk4_step(state, t, h, params)
        t += h

poincare_pts = np.array(poincare_pts)

# Побудова графіка
plt.figure(figsize=(8, 6))
plt.scatter(poincare_pts[:, 0], poincare_pts[:, 1], s=0.8, color='crimson', alpha=0.7)
plt.title("Переріз Пуанкаре для хаотичного осцилятора Дуффінга")
plt.xlabel("Координата x")
plt.ylabel("Швидкість v")
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig("poincare_python.png", dpi=300)
print("Графік збережено як poincare_python.png")
