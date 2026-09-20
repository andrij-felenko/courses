"""
Демонстраційна утиліта інженерного розрахунку та моделювання схеми баластного гальмування
(brake chopper) для інтегрального сервоконтролера безколекторного двигуна (BLDC).

Виконує:
1. Задання фізичних параметрів механічного навантаження, двигуна та шини живлення DC.
2. Аналітичний розрахунок баластного резистора та дільника компаратора з гістерезисом.
3. Чисельне моделювання динаміки напруги шини DC у двох сценаріях (без чопера та з чопером).
4. Виведення підсумкового інженерного звіту та ASCII-діаграми перехідного процесу.
"""

import sys
from typing import List

from brake_chopper import (
    BrakeChopperCalculator,
    MechanicalParameters,
    ElectricalParameters,
    ComparatorConfig,
)
from chopper_sim import DcBusSimulator, SimulationResult


def render_ascii_waveform(
    time_series: List[float],
    v_bus_series: List[float],
    v_on: float,
    v_off: float,
    v_nom: float,
    v_safe: float,
    width: int = 64,
    height: int = 14,
) -> str:
    """
    Генерує текстовий ASCII-графік динаміки напруги шини DC з горизонтальними
    маркерами ключових порогів спрацьовування та безпеки.
    """
    if not time_series or not v_bus_series:
        return "Графік недоступний: порожні дані симуляції."

    v_min_plot = min(v_nom - 2.0, min(v_bus_series))
    v_max_plot = max(v_safe + 1.5, max(v_bus_series) + 1.0)
    v_range = v_max_plot - v_min_plot

    grid = [[" " for _ in range(width)] for _ in range(height)]

    def v_to_row(v: float) -> int:
        ratio = (v - v_min_plot) / v_range if v_range > 0 else 0.5
        r = int(round((height - 1) * (1.0 - ratio)))
        return max(0, min(height - 1, r))

    row_safe = v_to_row(v_safe)
    row_on = v_to_row(v_on)
    row_off = v_to_row(v_off)
    row_nom = v_to_row(v_nom)

    # Горизонтальні лінії порогів
    for c in range(width):
        if 0 <= row_safe < height:
            grid[row_safe][c] = "!"
        if 0 <= row_on < height:
            grid[row_on][c] = "-"
        if 0 <= row_off < height:
            grid[row_off][c] = "."
        if 0 <= row_nom < height:
            grid[row_nom][c] = "_"

    # Нанесення кривої напруги V_bus(t)
    n = len(time_series)
    for c in range(width):
        idx = int(c * (n - 1) / (width - 1))
        v_val = v_bus_series[idx]
        r = v_to_row(v_val)
        grid[r][c] = "#"

    lines: List[str] = []
    lines.append("     Напруга [В]")
    for r in range(height):
        v_at_r = v_max_plot - (r / (height - 1)) * v_range
        tag = "      "
        if r == row_safe:
            tag = " [SAFE]"
        elif r == row_on:
            tag = "  [Von]"
        elif r == row_off:
            tag = " [Voff]"
        elif r == row_nom:
            tag = "  [Vnom]"
        line_str = f"{v_at_r:5.1f}V{tag} |" + "".join(grid[r]) + "|"
        lines.append(line_str)

    t_end = time_series[-1]
    lines.append("             +" + "-" * width + "+")
    t_label_padding = max(0, width - 13)
    t_labels = f"             0.00s" + " " * t_label_padding + f"{t_end:.2f}s  Час"
    lines.append(t_labels)
    lines.append(
        "             Позначення: [#] Напруга V_bus  [-] Поріг Von  [.] Поріг Voff  [!] Границя Safe  [_] V_nom"
    )

    return "\n".join(lines)


def main() -> None:
    # Забезпечуємо коректне виведення символів UTF-8 у терміналі
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print(" РОЗРАХУНОК І МОДЕЛЮВАННЯ ГАЛЬМІВНОГО ЧОПЕРА BLDC СЕРВОКОНТРОЛЕРА")
    print("=" * 80)

    # 1. Задання інженерних параметрів системи
    # Типовий інтегральний сервопривід (робототехнічний суглоб з інерційним маніпулятором)
    mech_params = MechanicalParameters(
        j_rotor=0.00004,        # Момент інерції ротора двигуна: 0.4e-4 кг*м^2
        j_load=0.00036,         # Зведений момент інерції ланки: 3.6e-4 кг*м^2 (співвідношення 9:1)
        omega_start_rpm=3000.0, # Робоча кутова швидкість перед сповільненням: 3000 об/хв
        omega_end_rpm=0.0,      # Повна зупинка вала
        t_decel=0.08,           # Інтенсивне гальмування за 80 мс
        efficiency=0.88,        # Сумарний ККД механіки та інвертора в генераторному режимі
    )

    elec_params = ElectricalParameters(
        v_nominal=48.0,         # Номінальна напруга шини живлення: 48 В
        v_on=56.0,              # Бажаний поріг увімкнення баласту: 56 В
        v_off=52.0,             # Бажаний поріг вимкнення баласту: 52 В
        v_max_safe=60.0,        # Максимальна безпечна напруга ключів/конденсаторів: 60 В
        c_bus=1000e-6,          # Ємність електролітичних та керамічних конденсаторів шини: 1000 мкФ
        t_cycle=2.0,            # Період повторення циклу «розгін-рух-гальмування»: 2.0 с
        i_fet_max=30.0,         # Допустимий імпульсний струм баластного MOSFET (наприклад, 40A ключ): 30 А
        margin_factor=1.35,     # Коефіцієнт запасу тривалої потужності резистора: 35%
    )

    comp_cfg = ComparatorConfig(
        v_ref=2.5,              # Джерело опорної напруги: 2.5 В (прецизійний ІОН TL431)
        v_dd=3.3,               # Логічне живлення компаратора: 3.3 В
        r1_base=100_000.0,      # Базовий резистор дільника шини: 100 кОм
    )

    # 2. Аналітичний розрахунок компонентів чопера
    report = BrakeChopperCalculator.calculate(mech_params, elec_params, comp_cfg)

    print("\n--- 1. ВХІДНІ ДАНІ СЕРВОПРИВОДА ---")
    print(f"Повний момент інерції J_total:      {report.e_kin * 2 / (mech_params.omega_start_rad_s**2) * 1e4:.2f} * 10^-4 кг*м^2")
    print(f"Швидкість до сповільнення:          {mech_params.omega_start_rpm:.0f} об/хв ({mech_params.omega_start_rad_s:.2f} рад/с)")
    print(f"Час сповільнення t_decel:           {mech_params.t_decel * 1000:.1f} мс")
    print(f"Номінал шини DC V_nominal:          {elec_params.v_nominal:.1f} В")
    print(f"Ємність фільтра шини C_bus:         {elec_params.c_bus * 1e6:.0f} мкФ")

    print("\n--- 2. ЕНЕРГЕТИЧНИЙ БАЛАНС ТА ПОТУЖНІСТЬ ---")
    print(f"Кінетична енергія E_kin:            {report.e_kin:.2f} Дж")
    print(f"Рекуперована в шину енергія E_regen:{report.e_regen:.2f} Дж")
    print(f"Поглинання конденсатором Delta E_C: {report.e_cap_absorbed:.2f} Дж (лише {report.e_cap_absorbed / report.e_regen * 100:.1f}% від E_regen)")
    print(f"Необхідно розсіяти в баласті E_res: {report.e_ballast:.2f} Дж")
    print(f"Пікова механічна потужність P_mech: {report.p_mech_peak:.1f} Вт")
    print(f"Пікова рекуперативна потужність P_el:{report.p_regen_peak:.1f} Вт")

    print("\n--- 3. ПІДБІР БАЛАСТНОГО РЕЗИСТОРА ТА КЛЮЧА ---")
    print(f"Максимальний опір R_brake_max:      {report.r_brake_max:.2f} Ом")
    print(f"Мінімальний опір за струмом ключа:  {report.r_brake_min_fet:.2f} Ом (при I_max = {elec_params.i_fet_max:.1f} А)")
    print(f"Обраний стандартний номінал (E24):  {report.r_brake_chosen:.1f} Ом")
    print(f"Піковий струм баластного ключа:     {report.i_brake_peak:.2f} А")
    print(f"Середня потужність резистора P_avg: {report.p_avg_ballast:.2f} Вт (період циклу {elec_params.t_cycle:.1f} с)")
    print(f"Рекомендована номінальна потужність:{report.p_rated_resistor:.1f} Вт (з урахуванням запасу 35%)")

    print("\n--- 4. РОЗРАХУНОК ДІЛЬНИКА КОМПАРАТОРА З ГІСТЕРЕЗИСОМ ---")
    print(f"Опорна напруга V_ref / Живлення Vdd:{comp_cfg.v_ref:.2f} В / {comp_cfg.v_dd:.2f} В")
    print(f"Цільові пороги спрацьовування:      Von = {elec_params.v_on:.2f} В, Voff = {elec_params.v_off:.2f} В (dHys = {elec_params.v_on - elec_params.v_off:.2f} В)")
    print(f"Резистор шини R1 (ідеал / E96):     {report.r1_ideal:.1f} Ом  -->  {report.r1_standard / 1000:.2f} кОм")
    print(f"Резистор на GND R2 (ідеал / E96):   {report.r2_ideal:.1f} Ом  -->  {report.r2_standard / 1000:.3f} кОм")
    print(f"Резистор гістерезису Rf (ідеал/E96):{report.rf_ideal:.1f} Ом  -->  {report.rf_standard / 1000:.2f} кОм")
    print(f"ФАКТИЧНІ ПОРОГИ З РЕЗИСТОРАМИ E96:  Von = {report.v_on_actual:.2f} В, Voff = {report.v_off_actual:.2f} В (dHys = {report.hysteresis_actual:.2f} В)")

    # 3. Чисельне моделювання динаміки шини DC
    def regen_profile(t: float) -> float:
        """Лінійний профіль спадання потужності сповільнення від P_peak до 0."""
        if t <= mech_params.t_decel:
            return report.p_regen_peak * (1.0 - t / mech_params.t_decel)
        return 0.0

    simulator = DcBusSimulator(
        c_bus=elec_params.c_bus,
        r_brake=report.r_brake_chosen,
        v_nominal=elec_params.v_nominal,
        v_on=report.v_on_actual,
        v_off=report.v_off_actual,
        v_max_safe=elec_params.v_max_safe,
    )

    sim_no_chopper = simulator.simulate(
        t_decel=mech_params.t_decel,
        p_regen_profile=regen_profile,
        enable_chopper=False,
    )

    sim_with_chopper = simulator.simulate(
        t_decel=mech_params.t_decel,
        p_regen_profile=regen_profile,
        enable_chopper=True,
    )

    # 4. Порівняльна таблиця результатів симуляції
    print("\n" + "=" * 80)
    print(" РЕЗУЛЬТАТИ ВЕРИФІКАЦІЙНОГО МОДЕЛЮВАННЯ ДИНАМІКИ ШИНИ DC")
    print("=" * 80)
    col_w = 34
    print(f"{'Параметр симуляції':<30} | {'Без чопера (аварія)':<{col_w}} | {'З баластним чопером':<{col_w}}")
    print("-" * 105)
    print(f"{'Пікова напруга шини V_max':<30} | {sim_no_chopper.v_max:.2f} В {'[ПРОБІЙ!]':<20} | {sim_with_chopper.v_max:.2f} В {'[БЕЗПЕЧНО]':<20}")
    print(f"{'Стан захисту інвертора':<30} | {'АВАРІЙНЕ ПЕРЕНАПРУЖЕННЯ':<{col_w}} | {'ШТАТНА СТАБІЛІЗАЦІЯ':<{col_w}}")
    print(f"{'Кількість перемикань ключа':<30} | {sim_no_chopper.switch_count:<{col_w}} | {sim_with_chopper.switch_count:<{col_w}}")
    print(f"{'Робочий цикл чопера (Duty)':<30} | {'0.0%':<{col_w}} | {sim_with_chopper.chopper_duty_cycle:.1f}%")
    print(f"{'Розсіяна в баласті енергія':<30} | {'0.00 Дж':<{col_w}} | {sim_with_chopper.e_brake_dissipated:.2f} Дж")
    print(f"{'Кінцева напруга шини':<30} | {sim_no_chopper.v_final:.2f} В{'':<{col_w-8}} | {sim_with_chopper.v_final:.2f} В{'':<{col_w-8}}")
    print("-" * 105)

    # 5. Візуалізація перехідного процесу
    print("\n--- 5. ЧАСОВА ДІАГРАМА НАПРУГИ ШИНИ З БАЛАСТНИМ ЧОПЕРОМ ---")
    waveform_ascii = render_ascii_waveform(
        time_series=sim_with_chopper.time_series,
        v_bus_series=sim_with_chopper.v_bus_series,
        v_on=report.v_on_actual,
        v_off=report.v_off_actual,
        v_nom=elec_params.v_nominal,
        v_safe=elec_params.v_max_safe,
    )
    print(waveform_ascii)

    # 6. Інженерні висновки та рекомендації
    print("\n--- 6. ІНЖЕНЕРНИЙ ВИСНОВОК ТА РЕКОМЕНДАЦІЇ ДЛЯ СХЕМОТЕХНІКИ ---")
    print(f"1. Конденсатори шини ({elec_params.c_bus*1e6:.0f} мкФ) здатні абсорбувати лише {report.e_cap_absorbed:.2f} Дж.")
    print(f"   Без чопера напруга сягає {sim_no_chopper.v_max:.1f} В, що в {sim_no_chopper.v_max / elec_params.v_nominal:.1f} рази перевищує номінал.")
    print(f"2. Баластний резистор {report.r_brake_chosen:.1f} Ом потужністю >= {report.p_rated_resistor:.0f} Вт надійно обмежує")
    print(f"   пікову напругу на рівні {sim_with_chopper.v_max:.2f} В (нижче допустимого ліміту {elec_params.v_max_safe:.1f} В).")
    print(f"3. Гістерезис компаратора dHys = {report.hysteresis_actual:.2f} В забезпечує стійку комутацію без брязкоту")
    print(f"   ({sim_with_chopper.switch_count} перемикань за {mech_params.t_decel*1000:.0f} мс гальмування при середній частоті ~{sim_with_chopper.switch_count / (2 * mech_params.t_decel):.0f} Гц).")
    print("4. Рекомендовано використовувати антипаралельний діод Шотткі (freewheeling diode) паралельно")
    print("   баластному резистору для гасіння індуктивних викидів розсіювання дротяних резисторів.")
    print("=" * 80)


if __name__ == "__main__":
    main()
