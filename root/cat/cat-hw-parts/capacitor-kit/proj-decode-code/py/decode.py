# decode.py — розкодовувач маркування конденсатора
# вхід: те, що надруковано на корпусі; вихід: ємність у пФ + допуск + напруга
import re

# літера-допуск → відсоток (тільки для довідки, у число ємності НЕ входить)
TOLERANCE = {
    "B": 0.1, "C": 0.25, "D": 0.5, "F": 1, "G": 2,
    "J": 5, "K": 10, "M": 20, "Z": None,  # Z = +80/−20 %, несиметричний
}
# суфікс одиниці → у скільки пікофарад (ключі — уже у верхньому регістрі)
UNIT_PF = {"P": 1, "N": 1_000, "U": 1_000_000, "M": 1_000_000_000}


def to_picofarads(mark: str) -> tuple[float, float | None, float | None]:
    """Повертає (ємність у пФ, допуск у % або None, робоча напруга у В або None)."""
    # мікрознак µ/μ звести до ASCII "u" ДО uppercase: інакше .upper() дасть Ω-подібну
    # грецьку «Μ» і збіг з одиницею загубиться. Далі весь рядок — у верхньому регістрі.
    s = mark.strip().replace("µ", "u").replace("μ", "u").upper().replace(" ", "")

    # 1. Відрізати робочу напругу, якщо вона приклеєна: "104/50V", "0.1uF 63V"
    voltage = None
    vm = re.search(r"(\d+(?:\.\d+)?)\s*V\b", s)
    if vm:
        voltage = float(vm.group(1))
        s = (s[: vm.start()] + s[vm.end():]).strip("/ ")

    # 2. Відрізати літеру-допуск у кінці: "104J" → код "104", допуск ±5 %
    tol = None
    tm = re.search(r"([BCDFGJKMZ])$", s)
    if tm and not s[: tm.start()].endswith(("U", "N", "P")):  # не сплутати з одиницею
        tol = TOLERANCE[tm.group(1)]
        s = s[: tm.start()]

    # 3. Гілка ПРЯМОГО маркування: є крапка, кома або буква-одиниця
    #    "0.1", "4n7", "470UF", "100N", "2U2"  (µ уже зведено до U вище)
    dm = re.fullmatch(r"(\d*)([PNUM]?)(\d*)F?", s)
    if ("." in s) or ("," in s) or (dm and dm.group(2)):
        s = s.replace(",", ".")
        # форма "4n7"/"2u2": буква-одиниця стоїть замість десяткової крапки
        m = re.fullmatch(r"(\d*)([PNUM])(\d+)", s)
        if m:
            whole, unit, frac = m.group(1) or "0", m.group(2), m.group(3)
            value = float(f"{whole}.{frac}")
            return value * UNIT_PF[unit], tol, voltage
        # форма "470UF"/"100N"/"0.1": число + необовʼязкова одиниця
        m = re.fullmatch(r"(\d+(?:\.\d+)?)([PNUM]?)F?", s)
        if m:
            value = float(m.group(1))
            unit = m.group(2) or "U"   # без одиниці велика деталь = мкФ
            return value * UNIT_PF[unit], tol, voltage

    # 4. Гілка ТРИЦИФРОВОГО коду: рівно 3 цифри "XYZ" → XY × 10^Z пФ
    if re.fullmatch(r"\d{3}", s):
        significant = int(s[:2])
        exponent = int(s[2])
        return significant * (10 ** exponent), tol, voltage

    # 5. Двоцифровий/одноцифровий запис — це вже пФ як є ("47" = 47 пФ)
    if re.fullmatch(r"\d{1,2}", s):
        return float(s), tol, voltage

    raise ValueError(f"не розпізнав маркування: {mark!r}")


def human(pf: float) -> str:
    """Пікофаради → найзручніша одиниця без зайвих нулів чи дробів."""
    if pf >= 1_000_000:
        return f"{_trim(pf / 1_000_000)} мкФ"
    if pf >= 1_000:
        return f"{_trim(pf / 1_000)} нФ"
    return f"{_trim(pf)} пФ"


def _trim(x: float) -> str:
    return f"{x:.6f}".rstrip("0").rstrip(".")


if __name__ == "__main__":
    for mark in ["104", "223", "474", "0.1", "470uF 25V", "4n7", "104J", "100", "47"]:
        pf, tol, v = to_picofarads(mark)
        extra = (f", ±{tol:g}%" if tol else "") + (f", {v:g} В" if v else "")
        print(f"{mark:>10}  →  {human(pf):>10}   ({pf:.0f} пФ{extra})")
