import math
import numpy as np

def rcsj_derivatives(tau, phi, v, i_dc, i_ac, omega, beta_c):
    gamma = 1.0 / math.sqrt(beta_c)
    dphi = v
    dv = i_dc + i_ac * math.sin(omega * tau) - math.sin(phi) - gamma * v
    return dphi, dv

def rk4_step(tau, phi, v, h, i_dc, i_ac, omega, beta_c):
    k1_phi, k1_v = rcsj_derivatives(tau, phi, v, i_dc, i_ac, omega, beta_c)
    
    tau_mid = tau + 0.5 * h
    k2_phi, k2_v = rcsj_derivatives(tau_mid, phi + 0.5 * h * k1_phi, v + 0.5 * h * k1_v, i_dc, i_ac, omega, beta_c)
    k3_phi, k3_v = rcsj_derivatives(tau_mid, phi + 0.5 * h * k2_phi, v + 0.5 * h * k2_v, i_dc, i_ac, omega, beta_c)
    
    tau_end = tau + h
    k4_phi, k4_v = rcsj_derivatives(tau_end, phi + h * k3_phi, v + h * k3_v, i_dc, i_ac, omega, beta_c)
    
    new_phi = phi + (h / 6.0) * (k1_phi + 2.0 * k2_phi + 2.0 * k3_phi + k4_phi)
    new_v = v + (h / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
    return new_phi, new_v

def compute_iv_curve(i_dc_array, i_ac=0.5, omega=0.6, beta_c=25.0, h=0.02):
    period = 2.0 * math.pi / omega
    steps_per_period = int(period / h)
    transient_steps = steps_per_period * 200
    eval_steps = steps_per_period * 500
    
    results = []
    phi, v = 0.0, 0.0
    
    for i_dc in i_dc_array:
        tau = 0.0
        # Перехідний процес
        for _ in range(transient_steps):
            phi, v = rk4_step(tau, phi, v, h, i_dc, i_ac, omega, beta_c)
            tau += h
            
        # Усереднення напруги
        v_sum = 0.0
        for _ in range(eval_steps):
            phi, v = rk4_step(tau, phi, v, h, i_dc, i_ac, omega, beta_c)
            tau += h
            v_sum += v
            
        v_avg = v_sum / eval_steps
        results.append((i_dc, v_avg))
        
    return results

if __name__ == "__main__":
    currents = np.linspace(0.0, 2.5, 100)
    iv_data = compute_iv_curve(currents)
    print("i_dc \t\t ⟨v⟩ / omega")
    for i_dc, v_avg in iv_data[::10]:
        print(f"{i_dc:.3f} \t {v_avg / 0.6:.4f}")
