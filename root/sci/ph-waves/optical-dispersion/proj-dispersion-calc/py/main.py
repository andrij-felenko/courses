import math

class SellmeierSolver:
    def __init__(self, name: str, B: list[float], C: list[float]):
        self.name = name
        self.B = B
        self.C = C
        self.c_vacuum = 299792458.0

    def n(self, lambda_um: float) -> float:
        l2 = lambda_um ** 2
        n2 = 1.0 + sum((b * l2) / (l2 - c) for b, c in zip(self.B, self.C))
        return math.sqrt(n2)

    def dn_dlambda(self, lambda_um: float, h: float = 1e-4) -> float:
        return (self.n(lambda_um + h) - self.n(lambda_um - h)) / (2.0 * h)

    def d2n_dlambda2(self, lambda_um: float, h: float = 1e-4) -> float:
        return (self.n(lambda_um + h) - 2.0 * self.n(lambda_um) + self.n(lambda_um - h)) / (h * h)

    def group_index(self, lambda_um: float) -> float:
        return self.n(lambda_um) - lambda_um * self.dn_dlambda(lambda_um)

    def abbe_number(self) -> float:
        n_d = self.n(0.587562)
        n_F = self.n(0.486133)
        n_C = self.n(0.656273)
        return (n_d - 1.0) / (n_F - n_C)

    def material_dispersion(self, lambda_um: float) -> float:
        d2n = self.d2n_dlambda2(lambda_um)
        lambda_m = lambda_um * 1e-6
        d2n_m2 = d2n * 1e12
        D_val = -(lambda_m / self.c_vacuum) * d2n_m2
        return D_val * 1e6

glasses = [
    SellmeierSolver("N-BK7 (Крон)", [1.03961212, 0.231792344, 1.01046945], [0.00600069867, 0.0200179144, 103.560653]),
    SellmeierSolver("N-SF11 (Флінт)", [1.73759695, 0.313747346, 1.89878101], [0.013188707, 0.0623068142, 155.23629]),
    SellmeierSolver("Fused Silica", [0.6961663, 0.4079426, 0.8974794], [0.004679148, 0.01351206, 97.93400254])
]

print(f"{'Скло':<20} | {'n (d-лінія)':<12} | {'n_g (d-лінія)':<12} | {'V_d (Аббе)':<10} | {'D (1.55 мкм)':<15}")
print("-" * 75)
for g in glasses:
    n_d = g.n(0.587562)
    ng_d = g.group_index(0.587562)
    vd = g.abbe_number()
    D_155 = g.material_dispersion(1.55)
    print(f"{g.name:<20} | {n_d:<12.6f} | {ng_d:<12.6f} | {vd:<10.2f} | {D_155:<15.2f}")
