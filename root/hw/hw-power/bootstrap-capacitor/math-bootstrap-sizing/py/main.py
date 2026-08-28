from dataclasses import dataclass

# Усі величини — у базових одиницях СІ: кулони, ампери, фаради, секунди, вольти.
@dataclass
class BootParams:
    Qg: float            # заряд затвора верхнього ключа, Кл (з даташита MOSFET)
    Qls: float           # заряд зсуву рівня за такт, Кл (з даташита драйвера)
    Qrr: float           # зворотний заряд відновлення діода, Кл (0 для Шотткі)
    Iqbs: float          # струм спокою верхнього боку, А (макс із даташита)
    Icbs_leak: float     # витік плаваючої шини драйвера + конденсатора, А
    Ig_leak: float       # витік затвора + зсуву рівня в статиці, А
    f: float             # частота ШІМ, Гц
    duty_max: float      # максимальна робоча шпаруватість, 0..1
    dV_allow: float      # дозволене просідання VB-VS, В
    R_charge: float      # сумарний послідовний опір доливу, Ом
    dcbias_derate: float # частка ємності, що лишається під напругою (напр. 0.5)
    margin: float        # додатковий запас (пуск, розкид), напр. 3.0


# Нижня межа: скільки ємності треба, щоб не просісти за найдовший відкритий такт.
def cbs_min(p):
    t_on   = p.duty_max / p.f                       # найдовший відкритий час
    q_once = p.Qg + p.Qls + p.Qrr                   # разові порції
    i_flow = p.Iqbs + p.Icbs_leak + p.Ig_leak
    q_flow = i_flow * t_on                          # цівки × час
    q_total = q_once + q_flow
    return q_total / p.dV_allow, q_total            # Cbs >= Qвитрат / ΔV


# Верхня межа: більше цієї ємності не встигне долитися за паузу t_off (5·τ).
def cbs_max(p):
    t_off = (1.0 - p.duty_max) / p.f                # закрита частина періоду
    tau_allow = t_off / 5.0                         # 5 сталих часу на долив
    return tau_allow / p.R_charge                   # Cbs_max = t_off / (5·R)


# Номінал, який реально ставимо: підлогу ділимо на DC-bias і множимо на запас.
def cbs_pick(p):
    lo, _ = cbs_min(p)
    return lo / p.dcbias_derate * p.margin          # компенсуємо DC-bias і запас


def main():
    p = BootParams(
        Qg=50e-9, Qls=5e-9, Qrr=2e-9,
        Iqbs=230e-6, Icbs_leak=50e-6, Ig_leak=0.3e-6,
        f=20e3, duty_max=0.90, dV_allow=0.5,
        R_charge=10.0, dcbias_derate=0.5, margin=3.0,
    )

    lo, q_total = cbs_min(p)
    hi = cbs_max(p)
    pick = cbs_pick(p)

    print(f"Qвитрат   = {q_total * 1e9:.1f} нКл")
    print(f"Cbs(min)  = {lo * 1e9:.0f} нФ   (нижня межа з балансу заряду)")
    print(f"Cbs(max)  = {hi * 1e9:.0f} нФ   (верхня межа з перезаряду)")
    print(f"ставимо   ~ {pick * 1e6:.2f} мкФ  (з DC-bias і запасом)")

    if pick > hi:
        print("УВАГА: потрібна ємність не долиється за паузу!")
        print("  → знизь R доливу, зменш стелю шпаруватості або візьми зарядову помпу.")


if __name__ == "__main__":
    main()
