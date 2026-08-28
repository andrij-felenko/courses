import cmath
import math

def calculate_reflection(z_load: complex, z0: float = 50.0, freq_hz: float = 2.4e9,
                         length_m: float = 0.05, vf: float = 0.60, atten_db_m: float = 1.5):
    """
    Обчислює комплексний коефіцієнт відбиття та лінійні параметри ВЧ-тракту.
    """
    if z0 <= 0 or freq_hz <= 0 or vf <= 0 or vf > 1.0 or length_m < 0:
        raise ValueError("Некоректні вхідні параметри лінії передачі")

    c0 = 299792458.0
    v_phase = c0 * vf
    wavelength = v_phase / freq_hz
    beta = 2.0 * math.pi / wavelength
    alpha_np_m = atten_db_m / 8.685889638

    # 1. Γ на навантаженні
    gamma_l = (z_load - z0) / (z_load + z0)
    mag = abs(gamma_l)
    phase_deg = math.degrees(cmath.phase(gamma_l))

    # 2. КСХ та Return Loss
    vswr = (1.0 + mag) / (1.0 - mag) if mag < 0.99999 else 999.99
    return_loss = -20.0 * math.log10(mag) if mag > 1e-12 else 240.0
    p_trans_pct = (1.0 - mag**2) * 100.0
    p_ref_pct = mag**2 * 100.0
    mismatch_loss = -10.0 * math.log10(1.0 - mag**2) if mag < 0.99999 else 99.99

    # 3. Трансформація вздовж лінії
    gamma_in = gamma_l * cmath.exp(complex(-2.0 * alpha_np_m * length_m, -2.0 * beta * length_m))
    z_in = z0 * (1.0 + gamma_in) / (1.0 - gamma_in)

    return {
        "gamma_load": gamma_l,
        "gamma_mag": mag,
        "gamma_phase_deg": phase_deg,
        "vswr": vswr,
        "return_loss_db": return_loss,
        "mismatch_loss_db": mismatch_loss,
        "power_trans_pct": p_trans_pct,
        "power_ref_pct": p_ref_pct,
        "gamma_in": gamma_in,
        "z_in": z_in
    }

if __name__ == "__main__":
    res = calculate_reflection(complex(75, 25))
    print("=== PYTHON РЕЗУЛЬТАТИ ===")
    print(f"Γ_L = {res['gamma_load'].real:.4f} + {res['gamma_load'].imag:.4f}j")
    print(f"|Γ| = {res['gamma_mag']:.4f}, Фаза = {res['gamma_phase_deg']:.2f}°")
    print(f"VSWR = {res['vswr']:.2f}:1, Return Loss = {res['return_loss_db']:.2f} dB")
    print(f"Передано потужності = {res['power_trans_pct']:.2f}%")
    print(f"Z_in = {res['z_in'].real:.2f} + {res['z_in'].imag:.2f}j Ом")
