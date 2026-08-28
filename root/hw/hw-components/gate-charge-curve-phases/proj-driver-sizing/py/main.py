from dataclasses import dataclass


@dataclass
class Mosfet:
    Qgd: float        # Кл — заряд плато Міллера (з паспорта, при робочій Vds)
    Qg: float         # Кл — повний заряд затвора при Vgs = Vdrive
    Vth: float        # В  — поріг
    gm: float         # См — крутість gfs у робочій точці
    Rg_int: float = 0.0   # Ω — внутрішній опір затвора приладу


@dataclass
class Driver:
    Vdrive: float     # В  — рівень ввімкнення
    Voff: float       # В  — рівень вимкнення (0 або від'ємний)
    Rsrc: float       # Ω  — вихідний опір, джерело (pull-up)
    Rsnk: float       # Ω  — вихідний опір, стік (pull-down)
    Isrc_max: float   # А  — паспортний піковий струм, джерело
    Isnk_max: float   # А  — паспортний піковий струм, стік


@dataclass
class Load:
    Id: float         # А  — комутований струм
    Vbus: float       # В  — напруга шини (повний розмах Vds)
    fsw: float        # Гц — частота перемикання


def size_gate_drive(m: Mosfet, drv: Driver, ld: Load,
                    *, t_fv: float = None, dvdt: float = None) -> dict:
    """Підбирає Rg_ext під цільовий час перекидання напруги t_fv (або dV/dt)
    і перевіряє, чи вкладається піковий струм у стелю драйвера — заряд І розряд."""
    Vpl = m.Vth + ld.Id / m.gm                 # напруга плато Міллера
    push = drv.Vdrive - Vpl                     # рушійна напруга на плато (заряд)
    pull = Vpl - drv.Voff                       # рушійна напруга на плато (розряд)
    swing = drv.Vdrive - drv.Voff               # повний розмах на затворі
    if push <= 0:
        raise ValueError("Vdrive нижча за плато — канал не відкриється повністю")

    # ціль → потрібний час перекидання напруги
    if dvdt is not None:
        t_fv = ld.Vbus / dvdt
    elif t_fv is None:
        raise ValueError("задай t_fv або dvdt")

    # 1. який сумарний опір кола дасть цей час на плато
    Ig_need = m.Qgd / t_fv                       # потрібний струм затвора на плато
    Rtot_need = push / Ig_need
    Rg_ext = Rtot_need - drv.Rsrc - m.Rg_int
    feasible = Rg_ext >= 0.0                      # від'ємний → драйвер сам засильний опір
    Rg_ext = max(Rg_ext, 0.0)

    # 2. фактичні часи й dV/dt з обраним (клемпленим) Rg_ext
    Rtot_on = drv.Rsrc + Rg_ext + m.Rg_int
    Rtot_off = drv.Rsnk + Rg_ext + m.Rg_int
    t_on = m.Qgd / (push / Rtot_on)
    t_off = m.Qgd / (pull / Rtot_off)
    dvdt_on = ld.Vbus / t_on
    dvdt_off = ld.Vbus / t_off

    # 3. піковий струм на СТАРТІ переходу (повний розмах на Rtot — найгірша мить)
    Ipk_on = swing / Rtot_on
    Ipk_off = swing / Rtot_off

    # 4. потужність керування (уся з драйверного живлення) і її розклад
    P_drive = m.Qg * swing * ld.fsw
    half = 0.5 * m.Qg * swing * ld.fsw
    P_Rg = half * (Rg_ext / Rtot_on + Rg_ext / Rtot_off)
    P_drv = half * (drv.Rsrc / Rtot_on + drv.Rsnk / Rtot_off)

    # 5. прикидка стрибка затвора сусіда від нашого dV/dt (Cgd ≈ Qgd/Vbus)
    Cgd = m.Qgd / ld.Vbus
    Vgs_bump = Cgd * dvdt_on * Rtot_off

    return dict(Vpl=Vpl, Rg_ext=Rg_ext, feasible=feasible,
                t_on=t_on, t_off=t_off, dvdt_on=dvdt_on, dvdt_off=dvdt_off,
                Ipk_on=Ipk_on, Ipk_off=Ipk_off,
                ok_src=Ipk_on <= drv.Isrc_max, ok_snk=Ipk_off <= drv.Isnk_max,
                P_drive=P_drive, P_Rg=P_Rg, P_drv=P_drv,
                Cgd=Cgd, Vgs_bump=Vgs_bump)


def report(m: Mosfet, drv: Driver, ld: Load, r: dict) -> None:
    verdict = "" if r["feasible"] else "  ← драйвер задорого повільний"
    print(f"Vpl (плато)        = {r['Vpl']:.2f} В")
    print(f"Rg_ext             = {r['Rg_ext']:.2f} Ω{verdict}")
    print(f"t_fv  вмик / вимк  = {r['t_on']*1e9:.1f} / {r['t_off']*1e9:.1f} нс")
    print(f"dV/dt вмик / вимк  = {r['dvdt_on']/1e9:.2f} / {r['dvdt_off']/1e9:.2f} В/нс")
    src = "ok" if r["ok_src"] else "ЗАМАЛА СТЕЛЯ"
    snk = "ok" if r["ok_snk"] else "ЗАМАЛА СТЕЛЯ"
    print(f"Iпік  джерело      = {r['Ipk_on']:.2f} А  (стеля {drv.Isrc_max:.1f} А — {src})")
    print(f"Iпік  стік         = {r['Ipk_off']:.2f} А  (стеля {drv.Isnk_max:.1f} А — {snk})")
    print(f"Потужність керув.  = {r['P_drive']*1e3:.0f} мВт "
          f"(у Rg_ext {r['P_Rg']*1e3:.0f}, у драйвері {r['P_drv']*1e3:.0f})")
    warn = "  ← ПАРАЗИТНЕ ВМИКАННЯ" if r["Vgs_bump"] > m.Vth else ""
    print(f"Стрибок Vgs сусіда = {r['Vgs_bump']:.2f} В  (проти Vth {m.Vth:.1f} В){warn}")


if __name__ == "__main__":
    fet = Mosfet(Qgd=15e-9, Qg=30e-9, Vth=3.0, gm=10.0, Rg_int=1.0)
    drv = Driver(Vdrive=10.0, Voff=0.0, Rsrc=2.0, Rsnk=2.0, Isrc_max=2.0, Isnk_max=2.0)
    ld = Load(Id=10.0, Vbus=48.0, fsw=200e3)

    print("── ціль: t_fv = 20 нс ──")
    report(fet, drv, ld, size_gate_drive(fet, drv, ld, t_fv=20e-9))
    print("\n── ціль: t_fv = 5 нс ──")
    report(fet, drv, ld, size_gate_drive(fet, drv, ld, t_fv=5e-9))
    print("\n── ціль: dV/dt = 5 В/нс ──")
    report(fet, drv, ld, size_gate_drive(fet, drv, ld, dvdt=5e9))
