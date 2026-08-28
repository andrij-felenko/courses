# Приклад обробки конвеєра рукостискання на Python
from pymavlink import mavutil
import time

class ConnectionFSM:
    def __init__(self, port):
        self.master = mavutil.mavlink_connection(port, baud=57600, source_system=255)
        self.state = "WAIT_HEARTBEAT"
        self.target_sys = None
        self.target_comp = None

    def spin_once(self):
        msg = self.master.recv_match(blocking=False)
        if not msg:
            return

        if self.state == "WAIT_HEARTBEAT":
            if msg.get_type() == 'HEARTBEAT' and msg.get_srcSystem() != 255:
                self.target_sys = msg.get_srcSystem()
                self.target_comp = msg.get_srcComponent()
                print(f"[1/4] HEARTBEAT отримано від SysID={self.target_sys}")
                self.state = "PARAM_DOWNLOAD"
                self.master.mav.param_request_list_send(self.target_sys, self.target_comp)

        elif self.state == "PARAM_DOWNLOAD":
            if msg.get_type() == 'PARAM_VALUE':
                # Обробка та перевірка закінчення параметрів...
                pass

        elif self.state == "CONFIG_STREAMS":
            if msg.get_type() == 'COMMAND_ACK':
                print("[3/4] Телеметрію налаштовано")
                self.state = "MISSION_DOWNLOAD"

        elif self.state == "MISSION_DOWNLOAD":
            # Обробка точок місії...
            pass
