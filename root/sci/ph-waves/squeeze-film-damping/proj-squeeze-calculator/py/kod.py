import numpy as np
from dataclasses import dataclass

@dataclass
class Film:
    L:  float                # довша сторона пластини, м
    W:  float                # коротша сторона, м
    h0: float                # зазор, м
    mu:  float = 1.8e-5      # в'язкість газу, Па·с        (повітря ≈ 1.8·10⁻⁵)
    lam: float = 68e-9       # довжина вільного пробігу, м (повітря ≈ 68 нм)
    p0:  float = 101_325.0   # навколишній тиск, Па

def _odd(N=40):
    o = np.arange(1, 2*N, 2)                 # 1, 3, 5, …
    return np.meshgrid(o, o, indexing="ij")

def eff_viscosity(f):
    """μ_eff за Veijola: прослизання біля стінок зменшує ефективну в'язкість."""
    Kn = f.lam / f.h0
    return f.mu / (1.0 + 9.638 * Kn**1.159), Kn

def damping_incompressible(f, N=40):
    """Нестисливий коеф.  c₀ = β·μ_eff·L·W³/h₀³  через суму squeeze-мод."""
    mu, _ = eff_viscosity(f)
    m, n  = _odd(N)
    S  = np.sum(1.0 / ((m*n)**2 * (m**2/f.L**2 + n**2/f.W**2)))
    c0 = 768.0 * mu * f.L * f.W * S / (np.pi**6 * f.h0**3)
    beta = c0 * f.h0**3 / (mu * f.L * f.W**3)      # 0.42 квадрат, →1 смуга
    return c0, beta

def split(f, freq, N=40):
    """Стисливий поділ:  c(ω) — демпфер,  k(ω) — газова пружина."""
    w    = 2*np.pi*freq
    mu, _ = eff_viscosity(f)
    m, n = _odd(N)
    w_mn = (np.pi**2 * f.p0 * f.h0**2 / (12*mu)) * (m**2/f.L**2 + n**2/f.W**2)
    pref = 64.0 * f.p0 * f.L * f.W / (np.pi**4 * f.h0)
    inv  = 1.0 / (m*n)**2
    c = pref * np.sum(inv * w_mn / (w_mn**2 + w**2))    # Н·с/м
    k = pref * np.sum(inv * w**2  / (w_mn**2 + w**2))    # Н/м
    f_c   = w_mn.min() / (2*np.pi)         # зріз — кутова першої моди ω₁₁
    a     = min(f.L, f.W)                  # коротша сторона задає час втечі
    sigma = 12*mu*w*a**2 / (f.p0 * f.h0**2)
    return c, k, f_c, sigma

def q_ceiling(f, mass, f0, N=40):
    """Стеля Q, яку прошарок накидає резонаторові маси mass із частотою f0."""
    c, k, f_c, sigma = split(f, f0, N)
    w0 = 2*np.pi*f0
    return mass*w0/c, c/(2*mass*w0), c     # Q, ζ, c(ω₀)
