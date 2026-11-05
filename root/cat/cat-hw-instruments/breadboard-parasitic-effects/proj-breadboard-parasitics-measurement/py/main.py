"""
main.py
Головна точка входу консольної програми аналізу паразитних параметрів макетних плат.

Моделює реалістичні тестові осцилограми перехідного процесу заряджання міжрейкової
ємності та імпульсного падіння напруги під навантаженням для якісного нового та
зношеного/окисленого контактів із накладанням вимірювального шуму, координує
конвеєр обробки та формує структурований метрологічний звіт в терміналі.
"""
import math
import random
import sys
from typing import Optional

from oscilloscope_trace import OscilloscopeTrace
from breadboard_parasitics import (
    BreadboardParasiticsAnalyzer,
    ParasiticReport,
    TestBenchConfig,
)


def generate_rc_step_trace(
    v_start: float,
    v_final: float,
    r_ohm: float,
    c_total_f: float,
    step_time_s: float,
    duration_s: float,
    sample_interval_s: float,
    noise_std_v: float = 0.003,
    seed: int = 42,
) -> OscilloscopeTrace:
    """
    Генерація змодельованої осцилограми RC-перехідного процесу заряду ємності.

    Модель сигналу: v(t) = v_start + (v_final - v_start) * (1 - exp(-(t - t_step) / tau)) + шум
    """
    rng = random.Random(seed)
    trace = OscilloscopeTrace()
    tau = r_ohm * c_total_f
    steps = int(round(duration_s / sample_interval_s))

    for i in range(steps + 1):
        t = i * sample_interval_s
        v = v_start
        if t >= step_time_s:
            dt = t - step_time_s
            v = v_start + (v_final - v_start) * (1.0 - math.exp(-dt / tau))
        # Накладання гаусового шуму квантування АЦП
        v += rng.gauss(0.0, noise_std_v)
        trace.add_sample(t, v)

    return trace


def generate_load_pulse_trace(
    v_supply: float,
    r_contact_ohm: float,
    i_load_a: float,
    pulse_start_s: float,
    pulse_duration_s: float,
    duration_s: float,
    sample_interval_s: float,
    noise_std_v: float = 0.002,
    seed: int = 42,
) -> OscilloscopeTrace:
    """
    Генерація змодельованої осцилограми спаду напруги під час імпульсу навантаження.

    Модель: у холостому стані напруга V_supply, під час протікання струму I_load
    напруга просідає на величину Delta_V = I_load * R_contact.
    """
    rng = random.Random(seed)
    trace = OscilloscopeTrace()
    pulse_end_s = pulse_start_s + pulse_duration_s
    v_drop = i_load_a * r_contact_ohm
    steps = int(round(duration_s / sample_interval_s))

    for i in range(steps + 1):
        t = i * sample_interval_s
        v = v_supply
        if pulse_start_s <= t <= pulse_end_s:
            v = v_supply - v_drop
        v += rng.gauss(0.0, noise_std_v)
        trace.add_sample(t, v)

    return trace


def print_report(title: str, rep: ParasiticReport) -> None:
    """
    Форматоване виведення результатів метрологічного аналізу в термінал.
    """
    separator = "=" * 72
    sub_sep = "-" * 72

    print(separator)
    print(f"  {title}")
    print(separator)
    print(f"  Час наростання фронту (t_r 10%-90%):    {rep.rise_time_ns:>8.2f} нс")
    print(f"  Еквівалентна постійна часу (tau):        {rep.tau_ns:>8.2f} нс")
    print(f"  Повна виміряна ємність (C_total):        {rep.total_capacitance_pf:>8.2f} пФ")
    print(f"  Паразитна міжрейкова ємність (C_par):    {rep.parasitic_capacitance_pf:>8.2f} пФ")
    print(f"  Гранична частота зрізу RC (f_-3dB):      {rep.cutoff_frequency_mhz:>8.2f} МГц")
    print(f"  Падіння напруги під навантаженням:       {rep.voltage_drop_mv:>8.2f} мВ")
    print(f"  Контактний перехідний опір (R_cont):     {rep.contact_resistance_mohm:>8.2f} мОм")
    print(f"  Технічний стан затискача:                {rep.health.describe()}")
    print(sub_sep)
    print(f"  Інженерний висновок:\n  {rep.notes}")
    print(separator)
    print()


def main() -> None:
    # Забезпечення коректного кодування виведення UTF-8 у консолі
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    print()
    print("=" * 72)
    print("   ДІАГНОСТИКА ПАРАЗИТНИХ ЕФЕКТІВ БЕЗПАЯЛЬНИХ МАКЕТНИХ ПЛАТ (Python)")
    print("   Визначення міжрейкової ємності та контактного опору за осцилограмами")
    print("=" * 72)
    print()

    # Параметри вимірювального стенда:
    # - Тестовий резистор R_test = 10 кОм (10000 Ом) для створення помірного RC-перехідного процесу
    # - Власна вхідна ємність щупа осцилографа C_probe = 12.0 пФ (стандартний пасивний щуп 10X)
    # - Тестовий струм навантаження для імпульсного заміру опору I_test = 0.5 А
    bench_cfg = TestBenchConfig(
        test_resistance_ohm=10_000.0,
        probe_capacitance_f=12.0e-12,
        test_load_current_a=0.5,
    )

    print("Параметри вимірювального стенда:")
    print(f" - Опір тестового резистора (R_test):    {bench_cfg.test_resistance_ohm:.0f} Ом")
    print(f" - Власна ємність щупа (C_probe 10X):     {bench_cfg.probe_capacitance_f * 1e12:.1f} пФ")
    print(f" - Струм імпульсного навантаження:       {bench_cfg.test_load_current_a:.1f} А\n")

    analyzer = BreadboardParasiticsAnalyzer(bench_cfg)

    # -------------------------------------------------------------------------
    # Сценарій 1: Нова якісна макетна плата (фосфориста бронза, крок 2.54 мм)
    # Очікувані фізичні параметри:
    # - Міжрейкова паразитна ємність C_par ≈ 2.2 пФ -> Разом зі щупом C_total ≈ 14.2 пФ
    # - Контактний опір R_cont ≈ 32 мОм -> Падіння при 0.5 А складе ~16 мВ
    # -------------------------------------------------------------------------
    expected_c_par_1 = 2.2e-12
    expected_c_total_1 = expected_c_par_1 + bench_cfg.probe_capacitance_f
    expected_r_cont_1 = 0.032  # 32 мОм

    step_trace_1 = generate_rc_step_trace(
        v_start=0.0,
        v_final=3.3,
        r_ohm=bench_cfg.test_resistance_ohm,
        c_total_f=expected_c_total_1,
        step_time_s=100.0e-9,
        duration_s=1200.0e-9,
        sample_interval_s=1.0e-9,
        seed=42,
    )
    step_trace_1.filter_outliers()

    load_trace_1 = generate_load_pulse_trace(
        v_supply=5.0,
        r_contact_ohm=expected_r_cont_1,
        i_load_a=bench_cfg.test_load_current_a,
        pulse_start_s=10.0e-6,
        pulse_duration_s=20.0e-6,
        duration_s=50.0e-6,
        sample_interval_s=0.5e-6,
        seed=42,
    )
    load_trace_1.filter_outliers()

    report_1 = analyzer.analyze(step_trace_1, load_trace_1)
    print_report("ЗРАЗОК 1: Нова якісна безпаяльна макетна плата", report_1)

    # -------------------------------------------------------------------------
    # Сценарій 2: Зношена / окислена дешева макетна плата
    # Очікувані фізичні параметри:
    # - Збільшена міжрейкова ємність C_par ≈ 4.8 пФ (забруднення, залишкова паста, деформація)
    # - Деградований контактний опір R_cont ≈ 380 мОм (втома пружинних затискачів, окиснення)
    # -------------------------------------------------------------------------
    expected_c_par_2 = 4.8e-12
    expected_c_total_2 = expected_c_par_2 + bench_cfg.probe_capacitance_f
    expected_r_cont_2 = 0.380  # 380 мОм

    step_trace_2 = generate_rc_step_trace(
        v_start=0.0,
        v_final=3.3,
        r_ohm=bench_cfg.test_resistance_ohm,
        c_total_f=expected_c_total_2,
        step_time_s=100.0e-9,
        duration_s=1500.0e-9,
        sample_interval_s=1.0e-9,
        seed=42,
    )
    step_trace_2.filter_outliers()

    load_trace_2 = generate_load_pulse_trace(
        v_supply=5.0,
        r_contact_ohm=expected_r_cont_2,
        i_load_a=bench_cfg.test_load_current_a,
        pulse_start_s=10.0e-6,
        pulse_duration_s=20.0e-6,
        duration_s=50.0e-6,
        sample_interval_s=0.5e-6,
        seed=42,
    )
    load_trace_2.filter_outliers()

    report_2 = analyzer.analyze(step_trace_2, load_trace_2)
    print_report("ЗРАЗОК 2: Зношена / окислена макетна плата (дефектні затискачі)", report_2)

    # -------------------------------------------------------------------------
    # Практичні інженерні висновки для макетування начорно
    # -------------------------------------------------------------------------
    print("ПРАКТИЧНІ РЕКОМЕНДАЦІЇ ДЛЯ ІНЖЕНЕРА-РОЗРОБНИКА:")
    print("1. Компенсація власної ємності щупа осцилографа є критичною: стандартний")
    print("   щуп 10X (~12 пФ) у 4-6 разів перевищує міжконтактну ємність макетки (1-3 пФ).")
    print("2. Контактний опір > 200 мОм спричиняє неприпустиме просідання шин живлення")
    print("   (Delta_V = I * R) під час імпульсного споживання MCU та Wi-Fi/BLE передавачів.")
    print("3. Обов'язково встановлюйте керамічні блокувальні конденсатори 100 нФ")
    print("   безпосередньо біля виводів живлення кожної мікросхеми на макеті.")
    print()


if __name__ == "__main__":
    main()
