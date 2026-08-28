import cmath
from math import radians

# фазор — це просто вбудоване комплексне число

def phasor_from(amp, phase):
    """з амплітуди й фази (рад) — у складові"""
    return cmath.rect(amp, phase)          # amp·(cos φ + i·sin φ)

# використання: 3∠0° + 4∠90°
i1 = phasor_from(3.0, 0.0)
i2 = phasor_from(4.0, radians(90))
total = i1 + i2                            # складові додаються поосьово

amp = abs(total)                           # = 5.0 А
phase = cmath.phase(total)                 # ≈ 0.927 рад ≈ 53.13°
