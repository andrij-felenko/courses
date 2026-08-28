import cmath, math

# фазор (I, Q) — це просто комплексне число: I = дійсна, Q = уявна частина
def to_iq(A, phi):                      # (A, φ у радіанах) → I + jQ
    return cmath.rect(A, phi)           # rect(r, φ) = r·cos φ + j·r·sin φ

# φ = 135° = 3π/4:  cos = −0.7071, sin = +0.7071
s = to_iq(1.0, 3.0 * math.pi / 4.0)     # s.real ≈ −0.707, s.imag ≈ +0.707

A   = abs(s)                            # → 1.000  (√(I² + Q²))
phi = math.degrees(cmath.phase(s))      # → 135.0° (atan2(Q, I))
