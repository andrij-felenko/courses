#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DVT Automated Power Supply Sweep Runner

Керує блоком живлення Rigol DP832A та мультиметром Keysight 34465A.
Знімає характеристику Line Regulation та формує звіт відповідності ТЗ.
"""

import time
import csv
import sys
try:
    import pyvisa
except ImportError:
    print("Помилка: встановіть pyvisa (pip install pyvisa pyvisa-py)")
    sys.exit(1)


def run_power_sweep(psu_resource: str, dmm_resource: str, output_file: str):
    rm = pyvisa.ResourceManager()
    
    print(f"Підключення до БЖ: {psu_resource}")
    psu = rm.open_resource(psu_resource)
    print(f"Підключення до DMM: {dmm_resource}")
    dmm = rm.open_resource(dmm_resource)

    # Ініціалізація приладів
    psu.write("*RST")
    dmm.write("*RST")
    time.sleep(1.0)

    # Налаштування мультиметра на вимірювання напруги DC, автодіапазон, 10 NPLC (висока точність)
    dmm.write(":SENS:VOLT:DC:NPLC 10")
    dmm.write(":SENS:VOLT:DC:RANG:AUTO ON")

    # Налаштування БЖ: Канал 1, обмеження струму 350 мА
    psu.write(":INST CH1")
    psu.write(":CURR 0.350")
    psu.write(":VOLT 3.600")
    psu.write(":OUTP CH1,ON")
    time.sleep(0.5)

    voltages_to_test = [round(2.0 + i * 0.1, 2) for i in range(23)] # 2.0V .. 4.2V
    results = []

    print("\n--- Початок сканування вхідної напруги (Line Regulation) ---")
    print("V_set (V) | V_in_meas (V) | V_out_3V3 (V) | I_in (mA) | Статус")
    print("-" * 60)

    for v_set in voltages_to_test:
        psu.write(f":VOLT {v_set:.3f}")
        time.sleep(0.4) # Час на стабілізацію перехідного процесу

        # Зчитування фактичної вхідної напруги та струму з БЖ
        v_in_act = float(psu.query(":MEAS:VOLT? CH1"))
        i_in_act = float(psu.query(":MEAS:CURR? CH1")) * 1000.0 # в мА

        # Прецизійне зчитування вихідної напруги 3.3V плати з мультиметра
        v_out_3v3 = float(dmm.query(":READ?"))

        # Перевірка критерію: вихідна напруга має бути в межах 3.30V +/- 2% (3.234V .. 3.366V)
        # за умови, що вхідна напруга вища за напругу падіння (Vin >= 3.45V)
        if v_in_act >= 3.45:
            is_pass = (3.234 <= v_out_3v3 <= 3.366)
            status = "PASS" if is_pass else "FAIL"
        else:
            status = "DROPOUT" # Очікуваний вихід із режиму стабілізації

        print(f"{v_set:9.2f} | {v_in_act:11.3f} | {v_out_3v3:13.4f} | {i_in_act:9.2f} | {status}")
        results.append({
            "v_set_v": v_set,
            "v_in_v": v_in_act,
            "v_out_3v3_v": v_out_3v3,
            "i_in_ma": i_in_act,
            "status": status
        })

    # Безпечне вимкнення виходу БЖ
    psu.write(":OUTP CH1,OFF")
    psu.close()
    dmm.close()

    # Запис звіту у CSV файл
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["v_set_v", "v_in_v", "v_out_3v3_v", "i_in_ma", "status"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nЗвіт успішно збережено у файл: {output_file}")


if __name__ == "__main__":
    # Замініть VISA-дескриптори на реальні адреси вашого обладнання в лабораторії
    PSU_VISA_ADDR = "USB0::0x1AB1::0x0E11::DP8C214000000::INSTR"
    DMM_VISA_ADDR = "USB0::0x2A8D::0x1301::MY59000000::INSTR"
    REPORT_PATH = "dvt_power_line_regulation_report.csv"
    
    # run_power_sweep(PSU_VISA_ADDR, DMM_VISA_ADDR, REPORT_PATH)
