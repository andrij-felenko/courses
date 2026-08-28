from pymavlink import mavutil
import io

def send_and_decode_telemetry():
    # Створення віртуального потоку в пам'яті для емуляції послідовного порту
    stream = io.BytesIO()
    
    # Створення екземпляра кодека MAVLink v2 (SYS ID = 1, COMP ID = 1)
    mav = mavutil.mavlink.MAVLink(stream, srcSystem=1, srcComponent=1)
    mav.set_proto_version(2)

    # 1. Формування та відправка повідомлення GLOBAL_POSITION_INT (#33)
    time_boot_ms = 125400
    lat = int(50.4501000 * 1e7)      # 504501000
    lon = int(30.5234000 * 1e7)      # 305234000
    alt = 185200                     # 185.2 м над рівнем моря в мм
    relative_alt = 45500            # 45.5 м над точкою зльоту в мм
    vx = 450                         # 4.5 м/с
    vy = -120                        # -1.2 м/с
    vz = -50                         # підйом 0.5 м/с
    hdg = 18050                      # 180.50 градусів (cdeg)

    mav.global_position_int_send(
        time_boot_ms, lat, lon, alt, relative_alt, vx, vy, vz, hdg
    )

    wire_data = stream.getvalue()
    print(f"[Python] Згенеровано кадр довжиною {len(wire_data)} байтів.")

    # 2. Розбір отриманого бінарного потоку на стороні приймача
    rx_stream = io.BytesIO(wire_data)
    rx_mav = mavutil.mavlink.MAVLink(rx_stream)

    while True:
        byte = rx_stream.read(1)
        if not byte:
            break
        msg = rx_mav.parse_char(byte)
        if msg is not None:
            if msg.get_type() == 'GLOBAL_POSITION_INT':
                lat_deg = msg.lat / 1e7
                lon_deg = msg.lon / 1e7
                alt_m = msg.relative_alt / 1000.0
                print(f"[Python] Отримано: широта={lat_deg:.7f}°, довгота={lon_deg:.7f}°, висота={alt_m:.1f} м.")

if __name__ == "__main__":
    send_and_decode_telemetry()
