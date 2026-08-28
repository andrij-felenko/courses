def block_damage(reversals, sn):
    closed, residue = rainflow(reversals)
    damage = 0.0
    # повні замкнені цикли
    for amp, mean in closed:
        sar = sn.goodman_equiv(amp, mean)
        damage += 1.0 / sn.cycles_to_failure(sar)
    # залишок: кожна ланка — пів-циклу
    for i in range(len(residue) - 1):
        amp  = abs(residue[i + 1] - residue[i]) / 2.0
        mean = (residue[i + 1] + residue[i]) / 2.0
        sar  = sn.goodman_equiv(amp, mean)
        damage += 0.5 / sn.cycles_to_failure(sar)
    return damage
