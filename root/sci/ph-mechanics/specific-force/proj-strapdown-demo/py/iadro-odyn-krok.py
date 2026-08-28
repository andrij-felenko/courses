G_WORLD = (0.0, 0.0, -9.81)           # гравітація вниз, вісь Z угору

def strapdown_step(q, v, p, a_prev, gyro, acc, dt):
    # 1. Орієнтація: докрутити точним приростом і ОБОВ'ЯЗКОВО нормувати.
    q = qunit(qmul(q, quat_delta((gyro[0]*dt, gyro[1]*dt, gyro[2]*dt))))

    # 2. Питому силу у світ.   3. Додати гравітацію.
    fw = qrot(q, acc)
    aw = (fw[0], fw[1], fw[2] + G_WORLD[2])

    # 4. Трапеція: швидкість — середнім прискоренням, позиція — середньою швидкістю.
    vn = tuple(v[i] + 0.5*(a_prev[i] + aw[i])*dt for i in range(3))
    p  = tuple(p[i] + 0.5*(v[i]     + vn[i])*dt for i in range(3))
    return q, vn, p, aw
