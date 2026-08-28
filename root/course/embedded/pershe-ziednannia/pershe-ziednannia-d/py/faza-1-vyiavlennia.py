# Обробка вхідного HEARTBEAT у Python через pymavlink
def process_incoming_heartbeat(msg):
    # Ігноруємо пакети від самої GCS (SysID 255)
    if msg.get_srcSystem() == 255:
        return

    vehicle_sysid = msg.get_srcSystem()
    vehicle_compid = msg.get_srcComponent()
    is_armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
    autopilot_name = "ArduPilot" if msg.autopilot == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA else "PX4"

    print(f"[GCS] Виявлено апарат SysID: {vehicle_sysid}, CompID: {vehicle_compid}, "
          f"Стек: {autopilot_name}, Стан моторів: {'ARMED' if is_armed else 'DISARMED'}")
