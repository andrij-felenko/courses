import math

def generate_field_grid(freq_hz, current_a, dl_m, r_max_m, grid_size=50):
    c = 299792458.0
    eps0 = 8.8541878128e-12
    omega = 2.0 * math.pi * freq_hz
    k = omega / c
    lambda_m = c / freq_hz

    grid = []
    for i in range(1, grid_size + 1):
        r = (i / grid_size) * r_max_m
        for j in range(grid_size + 1):
            theta = (j / grid_size) * math.pi
            
            r2, r3 = r * r, r * r * r
            E_coeff = (current_a * dl_m) / (4.0 * math.pi * eps0 * omega)
            H_coeff = (current_a * dl_m) / (4.0 * math.pi)
            
            E_theta = E_coeff * math.sin(theta) * (1.0 / r3 - (k * k) / r)
            H_phi = H_coeff * math.sin(theta) * (k / r)
            S_r = E_theta * H_phi
            
            grid.append((r / lambda_m, theta * 180.0 / math.pi, E_theta, H_phi, S_r))
    return grid

if __name__ == "__main__":
    data = generate_field_grid(100e6, 1.0, 0.03, 6.0, 5)
    print("r/lambda, theta_deg, E_theta, H_phi, S_r")
    for row in data[:5]:
        print(f"{row[0]:.3f}, {row[1]:.1f}, {row[2]:.3e}, {row[3]:.3e}, {row[4]:.3e}")
