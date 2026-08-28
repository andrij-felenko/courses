#!/usr/bin/env python3
# mission_upload_verify.py — завантажити місію, зчитати назад, звірити, стежити.
# Реальний pymavlink; запускати на землі проти борту (SITL чи справжнього).
from pymavlink import mavutil

# Підключення. Приклади рядка:
#   'udpin:0.0.0.0:14550'      — слухати SITL / mavproxy
#   'com7'  (Windows) / '/dev/ttyUSB0'  — телеметрійний радіомодем
#   baud=57600 для типового радіо; для USB baud ігнорується.
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

# Без цього target_system/target_component невідомі — чекаємо перший HEARTBEAT.
master.wait_heartbeat()
print(f"звʼязок є: system={master.target_system} component={master.target_component}")

TSYS = master.target_system
TCMP = master.target_component
MTYPE = mavutil.mavlink.MAV_MISSION_TYPE_MISSION   # звичайна місія (не гео/ралі)
