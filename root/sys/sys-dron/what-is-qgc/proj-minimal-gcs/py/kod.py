#!/usr/bin/env python3
"""Мінімальна наземна станція: слухає MAVLink, показує стан, шле одну команду."""
import time
from pymavlink import mavutil

mav = mavutil.mavlink                      # згенерований словник повідомлень і сталих
AUTOPILOT = mav.MAV_COMP_ID_AUTOPILOT1

# 'udpin:' — ми чекаємо, поки борт (чи симулятор) сам почне слати сюди.
# Для дротового з'єднання рядок інший: '/dev/ttyACM0' плюс baud=57600.
link = mavutil.mavlink_connection('udpin:0.0.0.0:14550', source_system=255)
