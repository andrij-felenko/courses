# Python реалізація аналізу Чабауті–Коулмана для гіпереліптичних кривих
import math

class FieldFp:
    def __init__(self, p):
        self.p = p

    def add(self, a, b): return (a + b) % self.p
    def sub(self, a, b): return (a - b) % self.p
    def mul(self, a, b): return (a * b) % self.p
    def power(self, base, exp): return pow(base, exp, self.p)

class HyperellipticCurveGenus2:
    def __init__(self, poly_coeffs):
        # poly_coeffs: [a0, a1, a2, a3, a4, a5, a6]
        self.coeffs = poly_coeffs

    def eval_f(self, x, F):
        res = 0
        x_pow = 1
        for c in self.coeffs:
            res = F.add(res, F.mul(c, x_pow))
            x_pow = F.mul(x_pow, x)
        return res

    def find_points_Fp(self, F):
        pts = []
        for x in range(F.p):
            rhs = self.eval_f(x, F)
            for y in range(F.p):
                if F.mul(y, y) == rhs:
                    pts.append((x, y))
        return pts

def chabauty_coleman_bound(coeffs, p, c1=1.0, c2=-0.5):
    F = FieldFp(p)
    curve = HyperellipticCurveGenus2(coeffs)
    pts = curve.find_points_Fp(F)
    
    bound = len(pts) + 2  # |C(F_p)| + 2g - 2 при g=2
    print(f"=== Модуль p = {p} ===")
    print(f"Точки редукції над F_{p}: {pts}")
    print(f"Оцінка Коулмана: |C(Q)| <= {bound} раціональних точок.")
    
    print("\nАналіз рядів Тейлора Коулмана:")
    for pt in pts:
        x0, y0 = pt
        if y0 != 0:
            inv_2y0 = 1.0 / (2.0 * y0)
            alpha0 = (c1 + c2 * x0) * inv_2y0
            alpha1 = c2 * inv_2y0
            print(f" Точка {pt} -> I(t) = {alpha0:.4f}*t + {alpha1/2.0:.4f}*t^2 + ...")
        else:
            print(f" Точка Вієрштрасса {pt} -> I(t) = {c1:.4f}*t + ...")
    print("-" * 50)
    return pts, bound

if __name__ == "__main__":
    # y^2 = x^6 + 1
    coeffs = [1, 0, 0, 0, 0, 0, 1]
    chabauty_coleman_bound(coeffs, p=5)
    chabauty_coleman_bound(coeffs, p=7)
