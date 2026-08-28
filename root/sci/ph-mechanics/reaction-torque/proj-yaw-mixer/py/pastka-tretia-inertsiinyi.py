# Обмежувач наростання газу: гасить непотрібні J·α-ривки.
# max_step — максимальна зміна газу за один цикл керування.
# state — список зі станом на місці; повертаємо новий out.
def slew_limit(target, state, max_step):
    out = [0.0] * 4
    for i in range(4):
        delta = target[i] - state[i]
        if delta > max_step:
            delta = max_step
        elif delta < -max_step:
            delta = -max_step
        state[i] += delta
        out[i] = state[i]
    return out
