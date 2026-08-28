tau0 = 15.15e-9
f = np.linspace(0, 6e9, 1601)
H = np.exp(-2j * np.pi * f * tau0)          # ідеальна лінія затримки

_, tau = group_delay(f, H)
print(np.max(np.abs(tau - tau0)))           # ~1e-21 — машинний нуль

phi = np.angle(H)                           # той самий розрахунок «в лоб»
naive = -np.diff(phi) / (2 * np.pi * np.diff(f))
print(np.sum(np.abs(naive - tau0) > 1e-12)) # 91 зіпсована точка
print(naive.min())                          # −2.515e-07, тобто τ₀ − 1/Δf
