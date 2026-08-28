def collide(m1, m2, u1, u2, e=1.0):
    """1D-удар із коефіцієнтом відновлення e (0…1). Повертає (v₁, v₂)."""
    vcm = (m1*u1 + m2*u2) / (m1 + m2)        # швидкість центра мас — її фіксує імпульс
    return (1 + e)*vcm - e*u1, (1 + e)*vcm - e*u2

def momentum(m1, m2, w1, w2):
    return m1*w1 + m2*w2

def kinetic(m1, m2, w1, w2):
    return 0.5*m1*w1*w1 + 0.5*m2*w2*w2
