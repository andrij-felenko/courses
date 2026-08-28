# ground_mavlink.py — читати телеметрію дрона з наземного модуля через pymavlink.
# Встановити:  pip install pymavlink pyserial
from pymavlink import mavutil

PORT = "COM7"          # Windows; на Linux — "/dev/ttyUSB0"
BAUD = 57600          # локальна швидкість USB-UART

def main():
    # mavlink_connection розуміє і серійний порт, і UDP/TCP — тут серійний.
    # Рядок 'COM7' (чи '/dev/ttyUSB0') pymavlink відкриває сам через pyserial.
    m = mavutil.mavlink_connection(PORT, baud=BAUD)
    print("чекаю heartbeat від апарата…")

    m.wait_heartbeat()   # блокує, доки не прийде перший HEARTBEAT
    # heartbeat не лише каже «апарат живий» — він ще й ЗНАЙОМИТЬ:
    # запам'ятовує, хто на тому кінці (target_system / target_component)
    print("апарат на лінії: system %d, component %d"
          % (m.target_system, m.target_component))

    while True:
        # читаємо наступне повідомлення; blocking=True — чекати, доки прийде
        msg = m.recv_match(blocking=True)
        if msg is None:
            continue
        t = msg.get_type()

        if t == "HEARTBEAT":
            # тип апарата, автопілот, режим, чи армовано — усе в heartbeat
            print("HEARTBEAT: тип=%d, автопілот=%d" % (msg.type, msg.autopilot))

        elif t == "GLOBAL_POSITION_INT":
            # координати в цілих: lat/lon у градусах × 10^7, alt у МІЛІМЕТРАХ
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.alt / 1000.0        # мм → метри
            print("позиція: %.7f, %.7f  висота %.1f м" % (lat, lon, alt))

        elif t == "SYS_STATUS":
            # напруга батареї в МІЛІВОЛЬТАХ, струм — у сантиамперах (0.01 A)
            volts = msg.voltage_battery / 1000.0     # мВ → В
            amps  = msg.current_battery / 100.0      # сА → А (−1, якщо не міряють)
            print("батарея: %.2f В, %.1f А" % (volts, amps))

if __name__ == "__main__":
    raise SystemExit(main())
