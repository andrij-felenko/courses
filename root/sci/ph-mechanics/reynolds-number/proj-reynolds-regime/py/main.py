import math
from dataclasses import dataclass

# Пороги переходу — саме для КРУГЛОЇ ТРУБИ (характерний розмір = діаметр).
RE_LAMINAR_MAX   = 2300.0
RE_TURBULENT_MIN = 4000.0

@dataclass
class Result:
    Re: float
    regime: str          # 'ламінарний' | 'перехідний' | 'турбулентний'
    f: float             # коефіцієнт тертя Дарсі
    dp: float            # втрата тиску, Па
    head: float          # втрата напору, м
    note: str = ''       # застереження, якщо є

def reynolds(rho, v, D, mu):
    return rho * v * D / mu               # Re = ρ·v·D/μ; D — ДІАМЕТР, не радіус

def classify(Re):
    if Re < RE_LAMINAR_MAX:   return 'ламінарний'
    if Re < RE_TURBULENT_MIN: return 'перехідний'
    return 'турбулентний'

def friction_factor(Re, eps, D):
    if Re < RE_LAMINAR_MAX:
        return 64.0 / Re                  # ламінар: точно, з Пуазейля; ε байдужа
    # турбулент — явна формула Гааланда (наближення неявного Коулбрука):
    # 1/√f = −1.8·log₁₀[ (ε/D / 3.7)^1.11 + 6.9/Re ]
    inv_sqrt_f = -1.8 * math.log10((eps / D / 3.7) ** 1.11 + 6.9 / Re)
    return 1.0 / inv_sqrt_f ** 2

def pipe_loss(rho, v, D, mu, L, eps=1.5e-6, g=9.81):
    Re = reynolds(rho, v, D, mu)
    regime = classify(Re)
    f = friction_factor(Re, eps, D)
    dp = f * (L / D) * (rho * v ** 2 / 2)     # Дарсі–Вайсбах; ρv²/2 — динамічний тиск
    note = '' if regime != 'перехідний' else 'перехідна смуга: f — груба оцінка'
    return Result(Re, regime, f, dp, dp / (rho * g), note)

if __name__ == '__main__':
    r = pipe_loss(rho=1000, v=1.0, D=0.015, mu=1e-3, L=10.0, eps=1.5e-6)
    print(f'Re     = {r.Re:.0f}  ({r.regime})')
    print(f'f      = {r.f:.4f}')
    print(f'Δp     = {r.dp/1000:.2f} кПа  на 10 м труби')
    print(f'напір  = {r.head:.2f} м')
    if r.note:
        print('⚠ ', r.note)
