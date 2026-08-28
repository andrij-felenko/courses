# RL-фільтр нижніх частот: підбір L за частотою зламу
# і перевірка послаблення на частоті завади.
import math

def rl_inductance(R, fc):                   # потрібна L з f꜀ = R/(2πL)
    return R / (2.0 * math.pi * fc)         # у генрі

# Частка амплітуди, що проходить крізь ФНЧ на частоті f:  R / √(R² + (ωL)²)
def rl_lowpass_gain(R, L, f):
    XL = 2.0 * math.pi * f * L              # реактивний опір котушки на f
    return R / math.sqrt(R * R + XL * XL)   # 1.0 у смузі, →0 високо
