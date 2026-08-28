import math

class MemristorHP:
    def __init__(self, r_on=100.0, r_off=16000.0, d=10e-9, mu_v=1e-14, p_window=2):
        self.r_on = r_on
        self.r_off = r_off
        self.d = d
        self.mu_v = mu_v
        self.p_window = p_window

    def biolek_window(self, x, current):
        stp = 1.0 if current < 0.0 else 0.0
        return 1.0 - math.pow(x - stp, 2 * self.p_window)

    def resistance(self, x):
        return self.r_on * x + self.r_off * (1.0 - x)

    def state_derivative(self, x, current):
        k = (self.mu_v * self.r_on) / (self.d ** 2)
        return k * current * self.biolek_window(x, current)

def simulate_memristor(v_amplitude, frequency, total_time, dt, x_init=0.1):
    mem = MemristorHP()
    x = x_init
    omega = 2.0 * math.pi * frequency
    steps = int(total_time / dt)
    
    history = []
    
    for i in range(steps):
        t = i * dt
        v = v_amplitude * math.sin(omega * t)
        r = mem.resistance(x)
        current = v / r
        
        history.append((t, v, current, r, x))
        
        # Рунге-Кутта 4-го порядку (RK4) для високої точності інтегрування
        k1 = mem.state_derivative(x, current)
        
        x_mid1 = max(0.0, min(1.0, x + 0.5 * dt * k1))
        r_mid1 = mem.resistance(x_mid1)
        i_mid1 = v / r_mid1
        k2 = mem.state_derivative(x_mid1, i_mid1)
        
        x_mid2 = max(0.0, min(1.0, x + 0.5 * dt * k2))
        r_mid2 = mem.resistance(x_mid2)
        i_mid2 = v / r_mid2
        k3 = mem.state_derivative(x_mid2, i_mid2)
        
        x_end = max(0.0, min(1.0, x + dt * k3))
        r_end = mem.resistance(x_end)
        i_end = v / r_end
        k4 = mem.state_derivative(x_end, i_end)
        
        x += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        x = max(0.0, min(1.0, x))
        
    return history

if __name__ == "__main__":
    trace = simulate_memristor(v_amplitude=1.2, frequency=2.0, total_time=1.0, dt=0.0001)
    print(f"{'t (s)':<8}{'V (V)':<10}{'I (mA)':<10}{'R (kOhm)':<10}{'x (w/D)':<10}")
    print("-" * 50)
    for pt in trace[::500]:
        t, v, i, r, x = pt
        print(f"{t:<8.4f}{v:<10.4f}{i*1e3:<10.4f}{r/1e3:<10.4f}{x:<10.4f}")
