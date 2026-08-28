plate = Film(L=200e-6, W=200e-6, h0=2e-6)
c0, beta          = damping_incompressible(plate)
c, k, f_c, sigma  = split(plate, 10e3)
mass              = 200e-6 * 200e-6 * 2e-6 * 2330   # кремній, товщина 2 мкм → 0.19 мкг
Q, zeta, _        = q_ceiling(plate, mass, 10e3)

print(f"μ_eff/μ = {eff_viscosity(plate)[0]/plate.mu:.3f}   (Kn = {plate.lam/plate.h0:.3f})")
print(f"β       = {beta:.3f}")
print(f"c₀      = {c0:.3e} Н·с/м    c(10кГц) = {c:.3e}   k = {k:.2f} Н/м")
print(f"σ       = {sigma:.2f}    f_c = {f_c/1e3:.0f} кГц")
print(f"Q_film  = {Q:.4f}   (ζ = {zeta:.1f})")
