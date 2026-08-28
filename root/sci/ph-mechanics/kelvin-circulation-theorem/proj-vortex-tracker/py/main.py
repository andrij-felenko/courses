import numpy as np

def velocity_field(x, y, t):
    """Поле швидкостей двовимірного потоку."""
    u_x = -np.sin(np.pi * x) * np.cos(np.pi * y) * np.exp(-0.01 * t)
    u_y =  np.cos(np.pi * x) * np.sin(np.pi * y) * np.exp(-0.01 * t)
    return u_x, u_y

def advance_rk4(x, y, t, dt):
    """Інтегрування координат маркетингових частинок методом RK4."""
    k1_x, k1_y = velocity_field(x, y, t)
    k2_x, k2_y = velocity_field(x + 0.5 * dt * k1_x, y + 0.5 * dt * k1_y, t + 0.5 * dt)
    k3_x, k3_y = velocity_field(x + 0.5 * dt * k2_x, y + 0.5 * dt * k2_y, t + 0.5 * dt)
    k4_x, k4_y = velocity_field(x + dt * k3_x, y + dt * k3_y, t + dt)
    
    x_new = x + (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
    y_new = y + (dt / 6.0) * (k1_y + 2.0 * k2_y + 2.0 * k3_y + k4_y)
    return x_new, y_new

def compute_circulation(x, y, t):
    """Обчислення замкненого контурного інтеграла ∮ u · dr."""
    dx = 0.5 * (np.roll(x, -1) - np.roll(x, 1))
    dy = 0.5 * (np.roll(y, -1) - np.roll(y, 1))
    u_x, u_y = velocity_field(x, y, t)
    return np.sum(u_x * dx + u_y * dy)

# Параметри розрахунку
N = 100
dt = 0.01
steps = 500

theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
x = 0.5 + 0.25 * np.cos(theta)
y = 0.5 + 0.25 * np.sin(theta)

t = 0.0
gamma_0 = compute_circulation(x, y, t)
print(f"t = {t:.2f} | Gamma = {gamma_0:.8f}")

for step in range(1, steps + 1):
    x, y = advance_rk4(x, y, t, dt)
    t += dt
    if step % 100 == 0:
        gamma = compute_circulation(x, y, t)
        err = abs(gamma - gamma_0) / gamma_0
        print(f"t = {t:.2f} | Gamma = {gamma:.8f} | Rel Error = {err:.2e}")
