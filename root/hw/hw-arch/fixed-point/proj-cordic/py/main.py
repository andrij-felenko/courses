def cordic_sincos(theta):               # theta у Q-форматі, |theta| ≤ ~99°
    x = ONE_OVER_K                       # = 1/K у Q-форматі (гасить посилення наперед)
    y = 0
    z = theta                            # лишок кута, женемо до нуля
    for i in range(N):
        if z >= 0:                       # знак z = напрям повороту
            x_new = x - (y >> i)         # псевдо-обертання вперед
            y_new = y + (x >> i)         #   (зсуви замість множень!)
            z     = z - ATAN[i]          # списали kᵢ з лишку
        else:
            x_new = x + (y >> i)         # псевдо-обертання назад
            y_new = y - (x >> i)
            z     = z + ATAN[i]
        x = x_new                        # ОНОВЛЮВАТИ РАЗОМ: y залежить від старого x
        y = y_new
    return (y, x)                        # y ≈ sin theta,  x ≈ cos theta
