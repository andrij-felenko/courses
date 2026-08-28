def deriv(state):
    """Похідна вектора стану (x, y, vx, vy) в обертовій системі."""
    x, y, vx, vy = state
    ax = omega**2 * x + 2*omega*vy      # відцентрове + коріолісове,
    ay = omega**2 * y - 2*omega*vx      # покомпонентно
    return np.array([vx, vy, ax, ay])

def rk4(dt, T):
    state = np.array([0.0, 0.0, v, 0.0])          # x, y, vx, vy у момент t = 0
    xs, ys = [0.0], [0.0]
    for _ in range(round(T/dt)):
        k1 = deriv(state)
        k2 = deriv(state + 0.5*dt*k1)
        k3 = deriv(state + 0.5*dt*k2)
        k4 = deriv(state + dt*k3)
        state = state + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        xs.append(state[0]); ys.append(state[1])
    return np.array(xs), np.array(ys)

xi, yi = rk4(0.001, T)
print(f"кінець інтеграла:  ({xi[-1]:+.4f}, {yi[-1]:+.4f})")   # (+4.0000, +0.0000)
print(f"кінець спіралі:    ({xr[-1]:+.4f}, {yr[-1]:+.4f})")   # (+4.0000, +0.0000)
