#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автономний рушій первинного рукостискання наземної станції на pymavlink."""

import time
import sys
from pymavlink import mavutil


class GcsHandshakeClient:
    def __init__(self, connection_string: str, baud: int = 57600):
        print(f"[GCS] Відкриття з'єднання: {connection_string} ({baud} бод)...")
        self.master = mavutil.mavlink_connection(
            connection_string,
            baud=baud,
            source_system=255,
            source_component=190
        )
        self.target_sys = None
        self.target_comp = None
        self.params = {}
        self.mission_items = []

    def run(self) -> bool:
        """Виконує повний конвеєр рукостискання."""
        if not self.step1_wait_heartbeat():
            return False
        if not self.step2_fetch_parameters():
            return False
        if not self.step3_configure_telemetry():
            return False
        if not self.step4_download_mission():
            return False

        print("\n" + "=" * 55)
        print(">>> [GCS READY] Усі підсистеми ініціалізовано! <<<")
        print("=" * 55)
        return True

    def step1_wait_heartbeat(self) -> bool:
        print("[1/4] Очікування першого пакета HEARTBEAT...")
        msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=10.0)
        if not msg:
            print("[ERR] Немає серцебиття від апарата (таймаут 10 с)!")
            return False

        self.target_sys = msg.get_srcSystem()
        self.target_comp = msg.get_srcComponent()
        is_armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

        print(f"[OK] Апарат знайдено: SysID={self.target_sys}, CompID={self.target_comp}, "
              f"Type={msg.type}, Autopilot={msg.autopilot}, Armed={is_armed}")
        return True

    def step2_fetch_parameters(self) -> bool:
        print("\n[2/4] Завантаження параметрів (PARAM_REQUEST_LIST)...")
        self.master.mav.param_request_list_send(self.target_sys, self.target_comp)

        expected_count = None
        received_mask = []
        last_rx_time = time.time()

        while True:
            msg = self.master.recv_match(type='PARAM_VALUE', blocking=False)
            if msg:
                last_rx_time = time.time()
                if expected_count is None:
                    expected_count = msg.param_count
                    received_mask = [False] * expected_count
                    print(f"  Очікується параметрів: {expected_count}")

                idx = msg.param_index
                if idx < len(received_mask) and not received_mask[idx]:
                    received_mask[idx] = True
                    p_name = msg.param_id
                    if isinstance(p_name, bytes):
                        p_name = p_name.decode('ascii', errors='ignore').strip('\x00')
                    self.params[p_name] = msg.param_value

                # Перевірка завершення вичитки
                if expected_count and sum(received_mask) == expected_count:
                    print(f"[OK] Усі {expected_count} параметрів успішно завантажено!")
                    return True
            else:
                time.sleep(0.01)

            # Перевірка дірок і затримки прийому
            if expected_count and (time.time() - last_rx_time > 0.8):
                missing_indices = [i for i, ok in enumerate(received_mask) if not ok]
                if not missing_indices:
                    break
                print(f"  Дозапит {len(missing_indices)} пропущених параметрів...")
                for missing_idx in missing_indices[:5]:  # дозапитуємо пачками
                    self.master.mav.param_request_read_send(
                        self.target_sys, self.target_comp, b"", missing_idx
                    )
                last_rx_time = time.time()

            if time.time() - last_rx_time > 15.0:
                print(f"[ERR] Таймаут завантаження параметрів (отримано {sum(received_mask)}/{expected_count})")
                return False

        return True

    def step3_configure_telemetry(self) -> bool:
        print("\n[3/4] Налаштування інтервалів повідомлень (MAV_CMD_SET_MESSAGE_INTERVAL)...")
        streams = [
            (mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 50000),             # 20 Гц
            (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 200000), # 5 Гц
            (mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 1000000),         # 1 Гц
            (mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS, 1000000)      # 1 Гц
        ]

        for msg_id, interval_us in streams:
            self.master.mav.command_long_send(
                self.target_sys, self.target_comp,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                0, float(msg_id), float(interval_us), 0, 0, 0, 0, 0
            )
            # Чекаємо підтвердження COMMAND_ACK
            ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1.0)
            if ack and ack.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL:
                print(f"  Потік MsgID={msg_id} (інтервал {interval_us} мкс) -> ACK={ack.result}")
            else:
                print(f"  Потік MsgID={msg_id} -> немає явного ACK (приймаємо за замовчуванням)")

        print("[OK] Потоки телеметрії сконфігуровано.")
        return True

    def step4_download_mission(self) -> bool:
        print("\n[4/4] Завантаження польотної місії (Mission Protocol)...")
        self.master.mav.mission_request_list_send(
            self.target_sys, self.target_comp,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )

        msg_count = self.master.recv_match(type='MISSION_COUNT', blocking=True, timeout=3.0)
        if not msg_count:
            print("  Місія відсутня або немає відповіді на запит кількості.")
            return True

        total_items = msg_count.count
        print(f"  Кількість елементів місії на борту: {total_items}")

        for seq in range(total_items):
            retries = 0
            while retries < 4:
                self.master.mav.mission_request_int_send(
                    self.target_sys, self.target_comp, seq,
                    mavutil.mavlink.MAV_MISSION_TYPE_MISSION
                )
                item = self.master.recv_match(type='MISSION_ITEM_INT', blocking=True, timeout=1.5)
                if item and item.seq == seq:
                    self.mission_items.append(item)
                    print(f"    Точка #{seq}: Cmd={item.command}, Lat={item.x/1e7:.6f}, Lon={item.y/1e7:.6f}, Alt={item.z}m")
                    break
                retries += 1
                print(f"    [WARN] Повтор запиту точки #{seq} (спроба {retries})...")

            if retries >= 4:
                print(f"[ERR] Не вдалося завантажити точку місії #{seq}!")
                return False

        # Фінальне квитування всієї місії
        self.master.mav.mission_ack_send(
            self.target_sys, self.target_comp,
            mavutil.mavlink.MAV_MISSION_ACCEPTED,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        print("[OK] Місію завантажено та підтверджено.")
        return True


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else 'udpin:127.0.0.1:14550'
    client = GcsHandshakeClient(port)
    client.run()
