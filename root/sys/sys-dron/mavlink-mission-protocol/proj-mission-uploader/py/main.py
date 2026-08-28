import time
from pymavlink import mavutil

class PyMissionUploader:
    """Клієнт завантаження місії на автопілот через pymavlink."""

    def __init__(self, master: mavutil.mavfile, target_system: int = 1, 
                 target_component: int = 1, timeout: float = 0.5, max_retries: int = 5):
        self.master = master
        self.target_system = target_system
        self.target_component = target_component
        self.timeout = timeout
        self.max_retries = max_retries

    def upload_mission(self, mission_items: list) -> bool:
        """Транзакційне завантаження списку елементів місії."""
        count = len(mission_items)
        if count == 0:
            print("[PY-FSM] Помилка: список місії порожній.")
            return False

        print(f"[PY-FSM] Старт завантаження: {count} пунктів.")
        
        # Крок 1: Відправка MISSION_COUNT
        retries = 0
        seq = 0

        self._send_count(count)
        start_time = time.time()

        while True:
            # Очікуємо відповіді від автопілота
            msg = self.master.recv_match(
                type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
                blocking=False
            )

            current_time = time.time()

            if msg is not None:
                msg_type = msg.get_type()

                if msg_type in ["MISSION_REQUEST_INT", "MISSION_REQUEST"]:
                    req_seq = msg.seq
                    print(f"[PY-FSM] Отримано запит: seq={req_seq}")

                    if req_seq < count:
                        seq = req_seq
                        retries = 0
                        self._send_item(mission_items[seq])
                        start_time = time.time()
                    else:
                        print(f"[PY-FSM] Помилка: автопілот запросив неіснуючий seq={req_seq}")
                        return False

                elif msg_type == "MISSION_ACK":
                    ack_result = msg.type
                    if ack_result == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                        print("[PY-FSM] УСПІХ: Місію прийнято та зафіксовано (MAV_MISSION_ACCEPTED).")
                        return True
                    else:
                        print(f"[PY-FSM] ВІДХИЛЕНО: Автопілот повернув код помилки {ack_result}.")
                        return False

            # Перевірка таймауту
            if current_time - start_time > self.timeout:
                if retries >= self.max_retries:
                    print(f"[PY-FSM] ТАЙМАУТ: Вичерпано ліміт спроб ({self.max_retries}). Відміна.")
                    return False

                retries += 1
                print(f"[PY-FSM] Таймаут. Повторна спроба {retries}/{self.max_retries}...")

                if seq == 0 and msg is None:
                    self._send_count(count)
                else:
                    self._send_item(mission_items[seq])

                start_time = time.time()

            time.sleep(0.01) # Запобігання 100% завантаженню CPU

    def _send_count(self, count: int):
        self.master.mav.mission_count_send(
            self.target_system,
            self.target_component,
            count,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        print(f"  -> TX: MISSION_COUNT(count={count})")

    def _send_item(self, item: dict):
        self.master.mav.mission_item_int_send(
            self.target_system,
            self.target_component,
            item["seq"],
            item.get("frame", mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT),
            item.get("command", mavutil.mavlink.MAV_CMD_NAV_WAYPOINT),
            item.get("current", 0),
            item.get("autocontinue", 1),
            item.get("param1", 0.0),
            item.get("param2", 2.0),
            item.get("param3", 0.0),
            item.get("param4", 0.0),
            int(item["lat"] * 1e7),
            int(item["lon"] * 1e7),
            float(item["alt"]),
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        print(f"  -> TX: MISSION_ITEM_INT(seq={item['seq']}, alt={item['alt']}m)")
