"""Сценарії заняття: три відповіді на команду й пастка повторного виконання.

Запуск: python main.py
"""

from __future__ import annotations

import asyncio
from dataclasses import replace

from cmdlink.client import CommandClient
from cmdlink.protocol import (
    CUSTOM_MODE_ENABLED,
    CommandInt,
    CommandLong,
    CopterMode,
    MavCmd,
    MavFrame,
    MavResult,
    TxState,
    deg_to_1e7,
)
from cmdlink.sim import SimAutopilot, SimRadio

failures = 0


def check(condition: bool, what: str) -> None:
    global failures
    print(f"  {'✔' if condition else '✘'} {what}")
    if not condition:
        failures += 1


def title(text: str) -> None:
    print(f"\n=== {text} ===")


def show_progress(percent: int) -> None:
    print(f"  [прогрес] {percent}%")


def arm_command(arm: bool) -> CommandLong:
    return CommandLong(command=MavCmd.COMPONENT_ARM_DISARM,
                       params=[1.0 if arm else 0.0])


def set_mode_command(mode: CopterMode) -> CommandLong:
    return CommandLong(command=MavCmd.DO_SET_MODE,
                       params=[CUSTOM_MODE_ENABLED, float(mode)])


def gripper_toggle_command() -> CommandLong:
    # param1 — номер захоплення, param2 = 2 — перемкнути (неідемпотентна дія).
    return CommandLong(command=MavCmd.DO_GRIPPER, params=[1.0, 2.0])


async def execute(client: CommandClient, frame) -> object:
    outcome = await client.send(replace(frame), progress_cb=show_progress)
    print(f"  => {outcome.state.name} / {outcome.result.name}, "
          f"кадрів у ефір: {outcome.attempts}, {outcome.message}")
    return outcome


async def main() -> int:
    vehicle = SimAutopilot()
    radio = SimRadio(vehicle, up_delay=0.06, down_delay=0.06)
    client = CommandClient(radio, retry_interval=0.3, max_retries=3)
    radio.attach(client)

    title("1. Відхилено: ARM без супутникового фіксу")
    outcome = await execute(client, arm_command(True))
    check(outcome.state == TxState.REJECTED and outcome.result == MavResult.DENIED,
          "борт відповів DENIED, автомат зупинився без повторів")
    check(outcome.attempts == 1, "відмова остаточна: другий кадр в ефір не пішов")
    check(not vehicle.armed, "мотори лишилися вимкненими")

    title("2. Прийнято: ARM із фіксом, двічі поспіль")
    vehicle.gps_fix = True
    await execute(client, arm_command(True))
    outcome = await execute(client, arm_command(True))
    check(outcome.result == MavResult.ACCEPTED and vehicle.armed,
          "ідемпотентна команда: повторне виконання нічого не зламало")

    title("3. Тиша в Uplink: перший кадр загинув, повтор із confirmation=1")
    radio.drop_next_uplink(1)
    outcome = await execute(client, set_mode_command(CopterMode.GUIDED))
    check(outcome.result == MavResult.ACCEPTED and outcome.attempts == 2,
          "друга спроба дійшла, режим перемкнено")
    check(vehicle.mode == CopterMode.GUIDED, f"режим борту: {vehicle.mode.name}")

    title("4. Тимчасова відмова: AUTO поки не звівся EKF")
    vehicle.ekf_ready = False
    outcome = await execute(client, set_mode_command(CopterMode.AUTO))
    check(outcome.result == MavResult.TEMPORARILY_REJECTED,
          "TEMPORARILY_REJECTED: повторити варто, але вже рішенням оператора")
    vehicle.ekf_ready = True

    title("5. Тиша в Downlink: замок і кеш дедуплікації на борту")
    before = vehicle.gripper_actuations
    radio.drop_next_downlink(1)  # дія виконана, квитанція загинула
    outcome = await execute(client, gripper_toggle_command())
    check(outcome.result == MavResult.ACCEPTED and outcome.attempts == 2,
          "станція отримала квитанцію лише з другої спроби")
    check(vehicle.gripper_actuations - before == 1,
          "сервопривід спрацював РІВНО один раз — кеш упізнав confirmation=1")

    title("6. Той самий сценарій без дедуплікації — подвійне спрацювання")
    vehicle.dedup = False
    before = vehicle.gripper_actuations
    radio.drop_next_downlink(1)
    await execute(client, gripper_toggle_command())
    check(vehicle.gripper_actuations - before == 2,
          "без кешу замок клацнув двічі: вантаж скинуто й механізм закрито")
    vehicle.dedup = True

    title("7. Контейнер: навігаційний наказ через LONG і через INT")
    outcome = await execute(client, CommandLong(command=MavCmd.NAV_LOITER_UNLIM))
    check(outcome.result == MavResult.COMMAND_INT_ONLY,
          "COMMAND_INT_ONLY: координати у float32 борт не приймає")

    loiter = CommandInt(
        command=MavCmd.NAV_LOITER_UNLIM,
        frame=MavFrame.GLOBAL_RELATIVE_ALT_INT,
        x=deg_to_1e7(50.4501234),
        y=deg_to_1e7(30.5234567),
        z=80.0,
    )
    outcome = await execute(client, loiter)
    check(outcome.result == MavResult.ACCEPTED,
          "COMMAND_INT прийнято, крок координати — 1.1 см")

    title("8. Довга операція: IN_PROGRESS відсуває таймаут")
    outcome = await execute(client, CommandLong(command=MavCmd.DO_START_MAG_CAL))
    check(outcome.result == MavResult.ACCEPTED and outcome.attempts == 1,
          "калібрування тривало довше за таймаут, але повторів не було")

    title("9. Повна тиша: борт не відповідає")
    vehicle.powered = False
    outcome = await execute(client, set_mode_command(CopterMode.RTL))
    check(outcome.state == TxState.TIMEOUT_FAILURE and outcome.attempts == 4,
          "після 1 + 3 спроб оголошено збій каналу керування")
    check(vehicle.mode == CopterMode.GUIDED,
          "стан апарата станції невідомий — телеметрію тут не замінити нічим")

    await radio.drain()
    print(f"\nневдалих перевірок: {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
