import math

class ShieldLayer:
    def __init__(self, r_in: float, r_out: float, mu_max: float, b_sat: float, n_power: float = 3.0):
        self.r_in = r_in
        self.r_out = r_out
        self.mu_max = mu_max
        self.b_sat = b_sat
        self.n_power = n_power

    def get_effective_mu(self, b_field: float) -> float:
        if b_field <= 0:
            return self.mu_max
        ratio = b_field / self.b_sat
        if ratio >= 1.0:
            return 1.05
        non_linear = max(0.0, 1.0 - (ratio ** self.n_power))
        return max(1.0, 1.0 + (self.mu_max - 1.0) * non_linear)

def simulate_shield(layers: list[ShieldLayer], b_ext: float):
    current_b = b_ext
    total_s = 1.0
    saturated = False

    for i in range(len(layers) - 1, -1, -1):
        layer = layers[i]
        concentration = layer.r_out / (layer.r_out - layer.r_in)
        b_wall = current_b * concentration

        if b_wall >= layer.b_sat * 0.9:
            saturated = True

        mu_r = layer.get_effective_mu(b_wall)
        r_sq = (layer.r_in / layer.r_out) ** 2
        s_i = 1.0 + 0.25 * (((mu_r - 1.0) ** 2) / mu_r) * (1.0 - r_sq)

        if i < len(layers) - 1:
            gap_factor = 1.0 - (layer.r_out / layers[i + 1].r_in) ** 2
            total_s *= s_i * gap_factor
        else:
            total_s *= s_i

        current_b /= s_i

    b_int = b_ext / total_s
    s_db = 20.0 * math.log10(total_s)
    return b_int, total_s, s_db, saturated

if __name__ == "__main__":
    layers = [
        ShieldLayer(r_in=0.050, r_out=0.051, mu_max=150000, b_sat=0.75),
        ShieldLayer(r_in=0.080, r_out=0.082, mu_max=10000, b_sat=2.00)
    ]
    
    print("=== Чисельне моделювання магнітного екрана (Python) ===")
    for b_ext in [50e-6, 1e-3, 10e-3]:
        b_int, s, s_db, sat = simulate_shield(layers, b_ext)
        print(f"B_ext = {b_ext:.2e} T | B_int = {b_int:.2e} T | S = {s:.2e} ({s_db:.1f} dB) | Sat: {sat}")
