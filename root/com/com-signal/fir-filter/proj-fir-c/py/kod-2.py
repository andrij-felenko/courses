def firf_sym_step(f, x):
    """лінійно-фазовий КІХ: buf[0] — найновіший, buf[NTAPS-1] — найстаріший"""
    f.buf[1:] = f.buf[:-1]           # зсув на один (короткий фільтр)
    f.buf[0] = x

    acc = 0.0
    half = NTAPS // 2
    for k in range(half):
        acc += f.b[k] * (f.buf[k] + f.buf[NTAPS - 1 - k])   # пара на один множник
    acc += f.b[half] * f.buf[half]   # центральний відвід — окремо
    return acc
