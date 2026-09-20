"""
Модуль аналітичного інженерного розрахунку схеми гальмівного чопера (brake chopper)
для інтегральних безколекторних (BLDC/PMSM) сервоконтролерів.

Розраховує кінетичну енергію механічної системи, пікову рекуперативну потужність,
опір і номінальну потужність баластного резистора, а також номінали резистивного
дільника схеми компаратора з гістерезисом (тригера Шмітта) з підбором
найближчих стандартних номіналів ряду E96/E24.
"""

from dataclasses import dataclass
import math
from typing import Dict, Tuple, List, Optional


# Стандартні ряди номіналів резисторів (мантиси)
E12_SERIES = (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)

E24_SERIES = (
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
)

E96_SERIES = (
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,
    1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58,
    1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
    2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
    2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
    3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23,
    5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
    6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
    8.66, 8.87, 9.09, 9.31, 9.53, 9.76
)


def find_nearest_standard_resistor(
    value: float,
    series: str = "E96",
    prefer_smaller: bool = False
) -> float:
    """
    Підбирає найближчий стандартний номінал резистора з ряду E12, E24 або E96.
    
    :param value: Розрахункове значення опору, Ом.
    :param series: Ряд номіналів ('E12', 'E24', 'E96').
    :param prefer_smaller: Якщо True, вибирає найближчий стандартний номінал <= value
                           (критично для баластного резистора, щоб гарантувати відведення потужності).
    :return: Стандартне значення опору, Ом.
    """
    if value <= 0:
        raise ValueError("Опір має бути строго додатним.")
        
    series_map = {
        "E12": E12_SERIES,
        "E24": E24_SERIES,
        "E96": E96_SERIES,
    }
    table = series_map.get(series.upper())
    if table is None:
        raise ValueError(f"Невідомий ряд номіналів: {series}. Очікується E12, E24 або E96.")

    exponent = math.floor(math.log10(value))
    candidates: List[float] = []
    for exp in (exponent - 1, exponent, exponent + 1):
        for base in table:
            candidates.append(round(base * (10 ** exp), 4))

    if prefer_smaller:
        smaller_or_equal = [c for c in candidates if c <= value]
        if smaller_or_equal:
            return max(smaller_or_equal)
        return min(candidates)

    return min(candidates, key=lambda c: abs(c - value) / value)


@dataclass
class MechanicalParameters:
    """Параметри механічної системи та профілю сповільнення."""
    j_rotor: float          # Момент інерції ротора двигуна, кг*м^2
    j_load: float           # Момент інерції навантаження, зведеного до вала, кг*м^2
    omega_start_rpm: float  # Початкова швидкість перед гальмуванням, об/хв
    omega_end_rpm: float    # Кінцева швидкість після гальмування, об/хв (0 для повної зупинки)
    t_decel: float          # Час сповільнення (тривалість гальмування), с
    efficiency: float = 0.88  # Сумарний ККД механіки та інвертора в генераторному режимі

    @property
    def j_total(self) -> float:
        """Повний момент інерції системи (ротор + навантаження)."""
        return self.j_rotor + self.j_load

    @property
    def omega_start_rad_s(self) -> float:
        """Початкова кутова швидкість, рад/с."""
        return self.omega_start_rpm * (2.0 * math.pi / 60.0)

    @property
    def omega_end_rad_s(self) -> float:
        """Кінцева кутова швидкість, рад/с."""
        return self.omega_end_rpm * (2.0 * math.pi / 60.0)


@dataclass
class ElectricalParameters:
    """Електричні параметри ланки постійного струму та обмеження силових компонентів."""
    v_nominal: float        # Номінальна напруга джерела живлення шини DC, В
    v_on: float             # Бажаний поріг увімкнення баластного ключа, В
    v_off: float            # Бажаний поріг вимкнення баластного ключа, В
    v_max_safe: float       # Гранично безпечна напруга силових транзисторів і конденсаторів, В
    c_bus: float            # Сумарна ємність конденсаторів шини DC, Ф
    t_cycle: float = 2.0    # Період повторення циклу руху для розрахунку тривалої потужності, с
    i_fet_max: float = 30.0 # Граничний імпульсний струм баластного MOSFET, А
    margin_factor: float = 1.35  # Коефіцієнт запасу для тривалої потужності баластного резистора


@dataclass
class ComparatorConfig:
    """Параметри схеми компаратора з гістерезисом (тригера Шмітта)."""
    v_ref: float = 2.5            # Опорна напруга компаратора (наприклад, TL431 або REF), В
    v_dd: float = 3.3             # Напруга живлення логіки компаратора (рівень HIGH), В
    r1_base: float = 100_000.0    # Базовий опір верхнього резистора дільника шини, Ом


@dataclass
class ChopperSizingReport:
    """Підсумковий звіт параметричного підбору компонентів схеми гальмування."""
    # Енергетичний баланс
    e_kin: float                 # Кінетична енергія системи перед гальмуванням, Дж
    e_regen: float               # Рекуперована енергія, що повертається в шину DC, Дж
    e_cap_absorbed: float        # Енергія, що поглинається конденсатором шини при заряді до Von, Дж
    e_ballast: float             # Залишкова енергія, яку необхідно розсіяти в баласті, Дж

    # Потужність
    p_mech_peak: float           # Пікова механічна потужність гальмування, Вт
    p_regen_peak: float          # Пікова рекуперативна електрична потужність на шині DC, Вт
    p_avg_ballast: float         # Середня розсіювана потужність баластного резистора за цикл, Вт
    p_rated_resistor: float      # Рекомендована номінальна потужність баластного резистора, Вт

    # Баластний резистор
    r_brake_max: float           # Теоретично максимальний опір баласту для скидання пікової потужності, Ом
    r_brake_min_fet: float       # Мінімальний опір баласту за обмеженням струму MOSFET, Ом
    r_brake_chosen: float        # Обраний стандартний опір баластного резистора, Ом
    i_brake_peak: float          # Піковий струм через баластний ключ при Von, А

    # Дільник компаратора з гістерезисом
    r1_ideal: float              # Розрахунковий резистор шини R1, Ом
    r1_standard: float           # Обраний стандартний резистор R1 (ряд E96), Ом
    r2_ideal: float              # Розрахунковий резистор на землю R2, Ом
    r2_standard: float           # Обраний стандартний резистор R2 (ряд E96), Ом
    rf_ideal: float              # Розрахунковий резистор зворотного зв'язку Rf, Ом
    rf_standard: float           # Обраний стандартний резистор Rf (ряд E96), Ом

    # Фактичні пороги з урахуванням номіналів E96
    v_on_actual: float           # Фактичний поріг увімкнення чопера, В
    v_off_actual: float          # Фактичний поріг вимкнення чопера, В
    hysteresis_actual: float     # Фактична ширина петлі гістерезису, В


class BrakeChopperCalculator:
    """
    Аналітичний інженерний калькулятор параметрів гальмівного чопера
    та схеми керування на базі гістерезисного компаратора.
    """

    @staticmethod
    def validate_inputs(
        mech: MechanicalParameters,
        elec: ElectricalParameters,
        comp: ComparatorConfig
    ) -> None:
        """Перевіряє фізичну коректність вхідних інженерних параметрів."""
        if mech.j_total <= 0:
            raise ValueError("Сумарний момент інерції має бути строго додатним.")
        if mech.omega_start_rpm <= mech.omega_end_rpm:
            raise ValueError("Початкова швидкість має бути більшою за кінцеву для режиму гальмування.")
        if mech.t_decel <= 0:
            raise ValueError("Час сповільнення має бути строго додатним.")
        if not (0.0 < mech.efficiency <= 1.0):
            raise ValueError("ККД має належати інтервалу (0, 1].")

        if elec.v_nominal <= 0:
            raise ValueError("Номінальна напруга шини має бути додатною.")
        if not (elec.v_nominal < elec.v_off < elec.v_on <= elec.v_max_safe):
            raise ValueError(
                f"Порушено умову ієрархії напруг: V_nominal ({elec.v_nominal}V) < "
                f"V_off ({elec.v_off}V) < V_on ({elec.v_on}V) <= V_max_safe ({elec.v_max_safe}V)."
            )
        if elec.c_bus <= 0:
            raise ValueError("Ємність шини має бути строго додатною.")
        if elec.t_cycle < mech.t_decel:
            raise ValueError("Період циклу руху не може бути меншим за час гальмування.")

        if comp.v_ref <= 0 or comp.v_dd <= 0:
            raise ValueError("Опорна напруга та напруга живлення логіки мають бути додатними.")
        if comp.v_ref >= comp.v_dd:
            raise ValueError(f"Опорна напруга V_ref ({comp.v_ref}V) має бути меншою за V_dd ({comp.v_dd}V).")

    @classmethod
    def calculate(
        cls,
        mech: MechanicalParameters,
        elec: ElectricalParameters,
        comp: Optional[ComparatorConfig] = None
    ) -> ChopperSizingReport:
        """
        Виконує повний інженерний розрахунок компонентів баластного захисту.
        """
        if comp is None:
            comp = ComparatorConfig()

        cls.validate_inputs(mech, elec, comp)

        # 1. Кінетична енергія механічної системи перед гальмуванням: E_kin = 0.5 * J * (w0^2 - w1^2)
        w0 = mech.omega_start_rad_s
        w1 = mech.omega_end_rad_s
        e_kin = 0.5 * mech.j_total * (w0 ** 2 - w1 ** 2)

        # 2. Електрична енергія рекуперації, що повертається через інвертор у шину DC
        e_regen = e_kin * mech.efficiency

        # 3. Енергія, яку конденсатори фільтра шини здатні поглинути під час заряду від V_nominal до V_on:
        # Delta E_c = 0.5 * C_bus * (V_on^2 - V_nominal^2)
        e_cap_absorbed = 0.5 * elec.c_bus * (elec.v_on ** 2 - elec.v_nominal ** 2)

        # 4. Залишкова енергія, яку необхідно примусово розсіяти на баластному резисторі
        e_ballast = max(0.0, e_regen - e_cap_absorbed)

        # 5. Пікова потужність гальмування:
        # При лінійному сповільненні кутова швидкість w(t) = w0 * (1 - t / t_decel).
        # Момент гальмування M = J * (w0 - w1) / t_decel.
        # Механічна потужність максимальна на початку гальмування (t = 0): P_mech = M * w0.
        p_mech_peak = mech.j_total * ((w0 - w1) / mech.t_decel) * w0
        p_regen_peak = p_mech_peak * mech.efficiency

        # 6. Розрахунок баластного резистора:
        # Щоб напруга шини не зростала вище порогу V_on, баластний резистор повинен відводити
        # електричну потужність, не меншу за пікову потужність рекуперації:
        # P_brake = (V_on^2) / R_brake >= P_regen_peak  ==>  R_brake <= (V_on^2) / P_regen_peak
        r_brake_max = (elec.v_on ** 2) / p_regen_peak

        # Перевірка обмеження пікового струму через комутуючий MOSFET
        r_brake_min_fet = elec.v_on / elec.i_fet_max
        if r_brake_max < r_brake_min_fet:
            raise ValueError(
                f"Обраний силовий ключ не витримує піковий струм гальмування: R_max ({r_brake_max:.2f} Ом) < "
                f"R_min ({r_brake_min_fet:.2f} Ом). Необхідно збільшити струм ключа або тривалість гальмування."
            )

        # Підбір стандартного номіналу резистора з ряду E24/E12
        r_brake_chosen = find_nearest_standard_resistor(r_brake_max, series="E24", prefer_smaller=True)
        if r_brake_chosen < r_brake_min_fet:
            r_brake_chosen = find_nearest_standard_resistor(r_brake_max, series="E24", prefer_smaller=False)

        i_brake_peak = elec.v_on / r_brake_chosen

        # Середня та номінальна тривала потужність розсіювання резистора за робочий цикл машини
        p_avg_ballast = e_ballast / elec.t_cycle
        p_rated_resistor = p_avg_ballast * elec.margin_factor

        # 7. Розрахунок резистивного дільника неінвертуючого компаратора з гістерезисом
        # Опорна напруга V_ref під'єднана до інвертуючого входу.
        # До неінвертуючого входу під'єднано резистори R1 (до V_bus), R2 (до GND), Rf (до V_out).
        # Вихідні логічні рівні компаратора: LOW = 0 В, HIGH = V_dd.
        # Рівняння тригера Шмітта:
        #   Delta V = V_on - V_off = V_dd * (R1 / Rf)  ==>  Rf = R1 * V_dd / (V_on - V_off)
        #   V_on = V_ref * (1 + R1/R2 + R1/Rf)  ==>  1/R2 = (V_on - V_ref)/(V_ref * R1) - 1/Rf
        delta_v_target = elec.v_on - elec.v_off
        r1_ideal = comp.r1_base
        rf_ideal = r1_ideal * (comp.v_dd / delta_v_target)

        inv_r2 = ((elec.v_on - comp.v_ref) / (comp.v_ref * r1_ideal)) - (1.0 / rf_ideal)
        if inv_r2 <= 0:
            raise ValueError("Неможливо реалізувати дільник компаратора: некоректні V_on, V_ref або Rf.")
        r2_ideal = 1.0 / inv_r2

        # Підбір стандартних номіналів 1% точності ряду E96
        r1_standard = find_nearest_standard_resistor(r1_ideal, series="E96")
        r2_standard = find_nearest_standard_resistor(r2_ideal, series="E96")
        rf_standard = find_nearest_standard_resistor(rf_ideal, series="E96")

        # Перерахунок фактичних порогів спрацьовування зі стандартними резисторами
        v_on_actual = comp.v_ref * r1_standard * (
            (1.0 / r1_standard) + (1.0 / r2_standard) + (1.0 / rf_standard)
        )
        v_off_actual = v_on_actual - comp.v_dd * (r1_standard / rf_standard)
        hysteresis_actual = v_on_actual - v_off_actual

        return ChopperSizingReport(
            e_kin=e_kin,
            e_regen=e_regen,
            e_cap_absorbed=e_cap_absorbed,
            e_ballast=e_ballast,
            p_mech_peak=p_mech_peak,
            p_regen_peak=p_regen_peak,
            p_avg_ballast=p_avg_ballast,
            p_rated_resistor=p_rated_resistor,
            r_brake_max=r_brake_max,
            r_brake_min_fet=r_brake_min_fet,
            r_brake_chosen=r_brake_chosen,
            i_brake_peak=i_brake_peak,
            r1_ideal=r1_ideal,
            r1_standard=r1_standard,
            r2_ideal=r2_ideal,
            r2_standard=r2_standard,
            rf_ideal=rf_ideal,
            rf_standard=rf_standard,
            v_on_actual=v_on_actual,
            v_off_actual=v_off_actual,
            hysteresis_actual=hysteresis_actual,
        )
