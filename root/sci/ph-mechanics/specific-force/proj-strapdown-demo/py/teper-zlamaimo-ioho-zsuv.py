def vadd(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def run_static(seconds, acc_bias, gyro_bias, sample):
    q, v, p = (1.0, 0.0, 0.0, 0.0), (0., 0., 0.), (0., 0., 0.)
    acc0 = (0., 0., G)                            # нерухомо: лише опора
    fw = qrot(q, vadd(acc0, acc_bias)); a_prev = (fw[0], fw[1], fw[2] - G)
    nxt, rows = sample, []
    for k in range(round(seconds / DT)):
        gyro = gyro_bias                          # істинна ω = 0, лишається зсув
        acc  = vadd(acc0, acc_bias)               # істинна f + зсув
        q, v, p, a_prev = strapdown_step(q, v, p, a_prev, gyro, acc, DT)
        t = DT * (k + 1)
        if t >= nxt - 1e-9:
            rows.append((t, math.hypot(p[0], p[1]))); nxt += sample
    return rows
