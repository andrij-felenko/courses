# -*- coding: utf-8 -*-
# Чи справді одна уявна частинка маси μ рухається за двох?
# Два прогони тим самим методом з тим самим кроком — і порівняння.
import math

# 2D-вектор тут — комплексне число: різниця, множення на скаляр і abs() уже є.

class Pair:
    """Чесна пара: два тіла, дві сили, третій закон Ньютона.
       g — стороннє однорідне поле, однакове для обох тіл."""
    def __init__(self, m1, m2, r1, r2, v1, v2, force, g=0j):
        self.m1, self.m2, self.force, self.g = m1, m2, force, g
        self.r1, self.r2, self.v1, self.v2 = r1, r2, v1, v2
        self._accel()

    def _accel(self):
        F = self.force(self.r1 - self.r2)      # сила на тіло 1 з боку тіла 2
        self.a1 = F / self.m1 + self.g
        self.a2 = -F / self.m2 + self.g        # третій закон: рівно й назустріч

    def step(self, h):                         # швидкісний Верле
        self.v1 += 0.5 * h * self.a1
        self.v2 += 0.5 * h * self.a2
        self.r1 += h * self.v1
        self.r2 += h * self.v2
        self._accel()
        self.v1 += 0.5 * h * self.a1
        self.v2 += 0.5 * h * self.a2

    @property
    def r(self):
        return self.r1 - self.r2


class Reduced:
    """Зведена задача: одна уявна частинка маси mu у точці r.
       Про друге тіло, про центр мас і про стороннє поле не знає нічого."""
    def __init__(self, mu, r, v, force):
        self.mu, self.force, self.r, self.v = mu, force, r, v
        self.a = force(r) / mu

    def step(self, h):
        self.v += 0.5 * h * self.a
        self.r += h * self.v
        self.a = self.force(self.r) / self.mu
        self.v += 0.5 * h * self.a


def compare(name, m1, m2, r0, v0, force, energy, h, steps,
            unit="", R0=0j, V0=0j, g=0j, exact=None):
    M = m1 + m2
    mu = m1 * m2 / M
    pair = Pair(m1, m2,
                R0 + (m2 / M) * r0, R0 - (m1 / M) * r0,     # r₁ = R + (m₂/M)·r
                V0 + (m2 / M) * v0, V0 - (m1 / M) * v0,     # r₂ = R − (m₁/M)·r
                force, g)
    red = Reduced(mu, r0, v0, force)

    E0 = 0.5 * mu * abs(v0) ** 2 + energy(abs(r0))
    mark = max(1, steps // 4)
    scale = abs(r0)
    d_rel = d_body = d_E = d_exact = 0.0
    growth = []
    for n in range(1, steps + 1):
        pair.step(h)
        red.step(h)
        t = n * h
        d_rel = max(d_rel, abs(pair.r - red.r))
        # відновлення справжнього тіла 1: зведений розв'язок + рух центра мас
        Rt = R0 + V0 * t + 0.5 * g * t * t
        d_body = max(d_body, abs((Rt + (m2 / M) * red.r) - pair.r1))
        E = 0.5 * mu * abs(red.v) ** 2 + energy(abs(red.r))
        d_E = max(d_E, abs(E - E0))
        scale = max(scale, abs(red.r))
        if exact:
            d_exact = max(d_exact, abs(red.r - exact(t)))
        if n % mark == 0:
            growth.append("%.3g→%.1e" % (t, d_rel))

    print("[%s]  h=%g, кроків=%d, μ=%.6g" % (name, h, steps, mu))
    print("  розбіжність двох способів  max|Δr| = %.3e %s  (%.1e від масштабу)"
          % (d_rel, unit, d_rel / scale))
    print("  відновлене тіло 1 проти чесного    = %.3e %s" % (d_body, unit))
    print("  власна похибка Верле (розмах по енергії) = %.2e відносних" % abs(d_E / E0))
    if exact:
        print("  зведений прогін проти точного ω = √(k/μ) = %.3e %s" % (d_exact, unit))
    print("  як росте |Δr|:  " + "   ".join(growth))
    print()


# ── 1. Сонце + Юпітер: AU, рік, маса Сонця; G = 4π² ─────────────────────────
G = 4 * math.pi ** 2
mS, mJ = 1.0, 9.5479e-4                 # M☉/M♃ = 1047.35
a, e = 5.2038, 0.0489                   # велика піввісь і ексцентриситет Юпітера
kepler = lambda r: -G * mS * mJ * r / abs(r) ** 3
kepler_U = lambda d: -G * mS * mJ / d
T = 2 * math.pi * math.sqrt(a ** 3 / (G * (mS + mJ)))
r0 = complex(a * (1 + e), 0)            # старт в афелії
v0 = complex(0, math.sqrt(G * (mS + mJ) / a * (1 - e) / (1 + e)))
print("період з формули = %.4f року (таблиця: 11.862)\n" % T)

compare("Кеплер: Сонце + Юпітер, 10 обертів", mJ, mS, r0, v0, kepler, kepler_U,
        1e-3, int(10 * T / 1e-3), unit="AU",
        R0=complex(0.3, -0.7), V0=complex(0.11, 0.05))

compare("Те саме + стороннє однорідне поле (лише в чесному прогоні)",
        mJ, mS, r0, v0, kepler, kepler_U, 1e-3, int(10 * T / 1e-3), unit="AU",
        R0=complex(0.3, -0.7), V0=complex(0.11, 0.05), g=complex(0.02, -0.01))

# ── 2. Два вантажі на пружині: СІ ───────────────────────────────────────────
m1, m2, k, L, A = 0.4, 1.1, 30.0, 0.25, 0.05
w = math.sqrt(k / (m1 * m2 / (m1 + m2)))
spring = lambda r: -k * (abs(r) - L) * r / abs(r)
spring_U = lambda d: 0.5 * k * (d - L) ** 2
compare("Пружина: проти точного ω = √(k/μ), 20 періодів", m1, m2,
        complex(L + A, 0), 0j, spring, spring_U, 1e-5, int(20 * 2 * math.pi / w / 1e-5),
        unit="м", R0=complex(0, 0.1), V0=complex(1.5, 0),
        exact=lambda t: complex(L + A * math.cos(w * t), 0))

# ── 3. Витягнута орбіта: той самий крок уже нікуди не годиться ──────────────
for h in (1e-3, 1e-5):
    e2 = 0.95
    compare("Кеплер e=0.95, 3 оберти, h=%g" % h, mJ, mS,
            complex(a * (1 + e2), 0),
            complex(0, math.sqrt(G * (mS + mJ) / a * (1 - e2) / (1 + e2))),
            kepler, kepler_U, h, int(3 * T / h), unit="AU")
