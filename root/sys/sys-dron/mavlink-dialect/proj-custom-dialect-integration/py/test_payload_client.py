#!/usr/bin/env python3
"""
test_payload_client.py — Клієнт перевірки кастомного діалекту MAVLink.
Підключається до UART-порту сенсора, слухає телеметрію та надсилає команди.
"""
import time
import sys
from pymavlink import mavutil

# Імпортуємо згенерований модуль діалекту
import smart_multispectral as custom_mavlink

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = 115200

    print(f"Підключення до сенсора на {port} зі швидкістю {baud} бод...")
    # Створюємо MAVLink з'єднання із зазначенням нашого діалекту
    master = mavutil.mavlink_connection(port, baud=baud, dialect="smart_multispectral")
    master.wait_heartbeat(timeout=5)

    print("З'єднання встановлено. Очікування кастомної телеметрії #42001...")

    # Чекаємо 3 телеметричні повідомлення
    for _ in range(3):
        msg = master.recv_match(type='MULTISPECTRAL_SURVEY_STATUS', blocking=True, timeout=3)
        if msg:
            print(f"[ТЕЛЕМЕТРІЯ] Час: {msg.time_boot_ms} мс | "
                  f"Темп: {msg.sensor_temperature:.2f} °C | "
                  f"Канали: {msg.raw_channels} | "
                  f"Фото: {getattr(msg, 'frame_counter', 0)} | "
                  f"SD: {getattr(msg, 'sd_storage_pct', 0)}%")
        else:
            print("Попередження: таймаут очікування телеметрії!")

    print("\nНадсилання команди запуску зйомки MAV_CMD_DO_TRIGGER_SPECTRAL_CAPTURE (#42050)...")
    master.mav.command_long_send(
        1,                  # target_system (БПЛА)
        100,                # target_component (Мультиспектральний модуль)
        42050,              # command
        0,                  # confirmation
        75.0,               # param1: експозиція 75 мс
        1.0,                # param2: 4-канальний режим
        1.0,                # param3: 1 кадр
        0, 0, 0, 0          # param4..7: зарезервовано
    )

    # Очікування відповіді COMMAND_ACK
    ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    if ack and ack.command == 42050:
        print(f"Отримано підтвердження COMMAND_ACK: результат = {ack.result} (0 = ACCEPTED)")
    else:
        print("Помилка: не отримано підтвердження команди!")

if __name__ == '__main__':
    main()
