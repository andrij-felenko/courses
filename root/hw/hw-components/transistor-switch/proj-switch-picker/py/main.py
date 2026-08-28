import math
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Circuit:
    """Коло, у якому працює ключ, і бюджет, у який він мусить улізти."""
    v_bus: float      # напруга шини, В
    i_load: float     # струм навантаження, А
    duty: float       # шпаруватість — частка часу у відкритому стані
    t_amb: float      # температура довкілля всередині корпусу, °C
    t_j_max: float    # проєктна межа температури кристала, °C
    v_drive: float    # амплітуда керування затвором, В
    i_drive: float    # струм драйвера затвора, А


@dataclass(frozen=True)
class Losses:
    """Чотири рахунки нарізно — щоб бачити, хто саме гріє."""
    cond: float
    sw: float
    drive: float
    leak: float

    @property
    def total(self) -> float:
        return self.cond + self.sw + self.drive + self.leak


@dataclass(frozen=True)
class Mosfet:
    name: str
    r_on_25: float    # опір відкритого каналу при 25 °C, Ω
    r_on_k: float     # R_ON(125 °C)/R_ON(25 °C) — з нормованого графіка даташита
    q_g: float        # повний заряд затвора, Кл
    q_gd: float       # заряд Міллера (затвор–стік), Кл
    i_leak_25: float  # витік закритого ключа при 25 °C, А
    leak_k: float     # I_вит(125 °C)/I_вит(25 °C) — теж із графіка даташита
    r_th: float       # тепловий опір кристал → довкілля, K/Вт

    def edge_time(self, c: Circuit) -> float:
        # Фронт триває рівно стільки, скільки драйвер вигрібає заряд Міллера.
        return self.q_gd / c.i_drive

    def losses(self, c: Circuit, f: float, t_j: float) -> Losses:
        r_on = self.r_on_25 * self.r_on_k ** ((t_j - 25.0) / 100.0)
        e_edge = 0.5 * c.v_bus * c.i_load * self.edge_time(c)
        i_leak = self.i_leak_25 * self.leak_k ** ((t_j - 25.0) / 100.0)
        return Losses(cond=c.i_load ** 2 * r_on * c.duty,
                      sw=2.0 * f * e_edge,
                      drive=self.q_g * c.v_drive * f,
                      leak=c.v_bus * i_leak * (1.0 - c.duty))


@dataclass(frozen=True)
class Bjt:
    name: str
    v_sat_25: float   # напруга насичення при 25 °C і робочому струмі, В
    v_sat_tc: float   # температурний коефіцієнт напруги насичення, В/°C
    i_base: float     # струм бази за форсованого β, А
    v_be: float       # напруга база–емітер у насиченні, В
    t_edge: float     # фронт: у біполярного його задає розсмоктування, с
    i_leak_25: float
    leak_k: float
    r_th: float

    def edge_time(self, c: Circuit) -> float:
        return self.t_edge

    def losses(self, c: Circuit, f: float, t_j: float) -> Losses:
        v_sat = self.v_sat_25 + self.v_sat_tc * (t_j - 25.0)
        e_edge = 0.5 * c.v_bus * c.i_load * self.t_edge
        i_leak = self.i_leak_25 * self.leak_k ** ((t_j - 25.0) / 100.0)
        return Losses(cond=v_sat * c.i_load * c.duty,
                      sw=2.0 * f * e_edge,
                      drive=self.i_base * self.v_be * c.duty,   # база просить струм увесь час
                      leak=c.v_bus * i_leak * (1.0 - c.duty))


class Verdict(Enum):
    OK = "вкладається"
    TOO_HOT = "перегрів"
    RUNAWAY = "розгін"
    NOT_A_SWITCH = "вже не ключ"


@dataclass(frozen=True)
class Result:
    verdict: Verdict
    t_j: float
    gain: float       # підсилення петлі, зчитане з самої ітерації
    losses: Losses


MAX_STEPS = 10_000
TOL = 1e-4          # K — дрібніше дробити температуру немає сенсу
T_CEILING = 300.0   # °C — вище кремнію не буває, там модель уже казка
EDGE_LIMIT = 0.2    # найбільша частка періоду, яку можна віддати фронтам


def transition_share(sw, c: Circuit, f: float) -> float:
    """Яку частку періоду з'їдають обидва фронти."""
    return 2.0 * sw.edge_time(c) * f


def settle(sw, c: Circuit, f: float) -> Result:
    """Стала температура кристала з рівняння T = T_amb + Rθ·P(f, T).

    Ітеруємо ВІД ДОВКІЛЛЯ ВГОРУ — це не «обраний за зручністю метод», а модель
    самого нагріву: холодний кристал вмикають, він гріється, нагрів піднімає
    втрати, більші втрати піднімають нагрів. Кожен крок — оберт справжньої петлі.
    """
    if transition_share(sw, c, f) > EDGE_LIMIT:
        return Result(Verdict.NOT_A_SWITCH, math.nan, math.nan,
                      Losses(math.nan, math.nan, math.nan, math.nan))

    t, prev_step, gain = c.t_amb, None, 0.0
    p = sw.losses(c, f, t)
    for _ in range(MAX_STEPS):
        p = sw.losses(c, f, t)
        t_next = c.t_amb + sw.r_th * p.total
        if t_next > T_CEILING:
            return Result(Verdict.RUNAWAY, math.inf, max(gain, 1.0), p)
        step = t_next - t
        if prev_step is not None and prev_step > TOL:
            gain = step / prev_step        # підсилення петлі — задарма, з самих кроків
            if gain >= 1.0:
                return Result(Verdict.RUNAWAY, math.inf, gain, p)
        if step < TOL:
            v = Verdict.OK if t_next <= c.t_j_max else Verdict.TOO_HOT
            return Result(v, t_next, gain, sw.losses(c, f, t_next))
        prev_step, t = step, t_next
    return Result(Verdict.RUNAWAY, math.inf, gain, p)


def f_ceiling(sw, c: Circuit, f_hi: float = 20e6, tol_hz: float = 100.0) -> float:
    """Найбільша частота, за якої ключ ще вкладається в бюджет.

    Утрати ростуть із частотою, температура — з утрат, тож «вкладається»
    вимикається раз і назавжди: предикат монотонний, його можна ділити навпіл.
    """
    if settle(sw, c, 0.0).verdict is not Verdict.OK:
        return 0.0                     # не тягне вже на постійному струмі
    if settle(sw, c, f_hi).verdict is Verdict.OK:
        return f_hi                    # стеля вища за діапазон пошуку
    lo, hi = 0.0, f_hi
    while hi - lo > tol_hz:
        mid = 0.5 * (lo + hi)
        if settle(sw, c, mid).verdict is Verdict.OK:
            lo = mid
        else:
            hi = mid
    return lo


BOX = Circuit(v_bus=12.0, i_load=3.0, duty=0.5, t_amb=40.0,
              t_j_max=125.0, v_drive=10.0, i_drive=0.5)

SHELF = [
    Mosfet("SOT-23, дрібний", 68e-3, 1.7, 8e-9, 2.5e-9, 1e-6, 50.0, 250.0),
    Mosfet("SO-8, середній", 25e-3, 1.7, 20e-9, 6e-9, 1e-6, 50.0, 62.0),
    Mosfet("SO-8, міліомний", 6e-3, 1.9, 65e-9, 20e-9, 5e-6, 50.0, 62.0),
    Bjt("DPAK, біполярний", 0.25, 0.6e-3, 0.15, 1.0, 400e-9, 1e-6, 50.0, 70.0),
]

for sw in SHELF:
    pencil = BOX.t_amb + sw.r_th * sw.losses(BOX, 20e3, 25.0).total
    r = settle(sw, BOX, 20e3)
    f = f_ceiling(sw, BOX)
    print(sw.name)
    print(f"  олівцем при 25 °C : T_j = {pencil:.0f} °C")
    print(f"  чесно на 20 кГц   : {r.verdict.value:<12} M = {r.gain:.3f}"
          + ("" if math.isinf(r.t_j) else f"   T_j = {r.t_j:.0f} °C"))
    print("  стеля частоти     : "
          + ("немає жодної придатної" if f == 0.0 else f"{f/1e3:.0f} кГц"))
    if r.verdict is Verdict.OK:
        p = r.losses
        print(f"  розклад, Вт       : провідність {p.cond:.3f} · перехід {p.sw:.3f}"
              f" · керування {p.drive:.3f} · витік {p.leak:.4f}"
              f"  →  разом {p.total:.3f}")
