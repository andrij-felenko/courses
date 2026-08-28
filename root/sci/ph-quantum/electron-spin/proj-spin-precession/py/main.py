import math
import cmath

class SpinorSimulator:
    def __init__(self, alpha: complex, beta: complex):
        norm = math.sqrt(abs(alpha)**2 + abs(beta)**2)
        self.alpha = alpha / norm
        self.beta = beta / norm

    def expectations(self):
        sx = (self.alpha.conjugate() * self.beta).real
        sy = (self.alpha.conjugate() * self.beta).imag
        sz = 0.5 * (abs(self.alpha)**2 - abs(self.beta)**2)
        return sx, sy, sz

    def rk4_step(self, B: tuple[float, float, float], gamma: float, dt: float):
        bx, by, bz = B
        
        def deriv(a: complex, b: complex):
            factor = -1j * (gamma / 2.0)
            da = factor * (bz * a + (bx - 1j * by) * b)
            db = factor * ((bx + 1j * by) * a - bz * b)
            return da, db

        da1, db1 = deriv(self.alpha, self.beta)
        da2, db2 = deriv(self.alpha + 0.5 * dt * da1, self.beta + 0.5 * dt * db1)
        da3, db3 = deriv(self.alpha + 0.5 * dt * da2, self.beta + 0.5 * dt * db2)
        da4, db4 = deriv(self.alpha + dt * da3, self.beta + dt * da3)

        self.alpha += (dt / 6.0) * (da1 + 2 * da2 + 2 * da3 + da4)
        self.beta += (dt / 6.0) * (db1 + 2 * db2 + 2 * db3 + db4)

        norm = math.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        self.alpha /= norm
        self.beta /= norm


if __name__ == "__main__":
    sim = SpinorSimulator(1.0 / math.sqrt(2), 1.0 / math.sqrt(2))
    B = (0.0, 0.0, 1.0)
    gamma_e = 1.7608596e11
    dt = 1e-13

    print("Time (ps) | <Sx>       | <Sy>       | <Sz>")
    print("-" * 45)
    for step in range(101):
        if step % 10 == 0:
            sx, sy, sz = sim.expectations()
            print(f"{step * dt * 1e12:9.3f} | {sx:10.6f} | {sy:10.6f} | {sz:10.6f}")
        sim.rk4_step(B, gamma_e, dt)
