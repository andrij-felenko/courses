#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автоматичний верифікатор простору станів таблиці правил."""

import itertools


def evaluate_safety_matrix(level_low: bool, level_high: bool, pressure_ok: bool, 
                           flow_ok: bool, e_stop: bool) -> tuple[bool, bool, str]:
    """
    Імітація логіки безпеки: повертає (heater_cmd, pump_cmd, status_msg).
    """
    # Фізичний парадокс датчиків рівня
    if level_high and not level_low:
        return False, False, "PARADOX_LEVEL_FAULT"

    # Аварійний стоп
    if e_stop:
        return False, False, "EMERGENCY_STOP"

    # Немає рідини в баку
    if not level_low:
        return False, False, "EMPTY_TANK_SAFE_OFF"

    # Немає тиску або протоку
    if not pressure_ok or not flow_ok:
        return False, False, "HYDRAULIC_FAULT_HOLD"

    # Нормальний робочий стан
    return True, True, "NORMAL_HEATING"


def run_exhaustive_test():
    inputs = ["level_low", "level_high", "pressure_ok", "flow_ok", "e_stop"]
    total_states = 2 ** len(inputs)
    print(f"Перевірка всіх {total_states} комбінацій станів...\n")

    violations = 0
    paradoxes = 0

    for combo in itertools.product([False, True], repeat=len(inputs)):
        state = dict(zip(inputs, combo))
        heater, pump, status = evaluate_safety_matrix(**state)

        # Інваріант безпеки: ТЕН ніколи не може бути увімкнений без помпи або без води
        if heater and (not pump or not state["level_low"] or not state["flow_ok"]):
            print(f"[КРИТИЧНЕ ПОРУШЕННЯ] Вхід: {state} -> ТЕН:{heater}, Помпа:{pump} [{status}]")
            violations += 1

        if status == "PARADOX_LEVEL_FAULT":
            paradoxes += 1

    print(f"Результат тестування:")
    print(f"  Всього станів: {total_states}")
    print(f"  Аномальних фізичних станів перехоплено: {paradoxes}")
    print(f"  Порушень інваріантів безпеки: {violations}")

    assert violations == 0, "Тест провалено: знайдено небезпечні комбінації правил!"
    print("-> 100% покриття станів: жодного небезпечного спрацьовування не виявлено.")


if __name__ == "__main__":
    run_exhaustive_test()
