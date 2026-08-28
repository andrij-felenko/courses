#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автоматизований тестовий стенд скриптованого оператора на Python (pymavlink).

Виконує повний регресійний цикл: підключення, зведення, набір висоти,
інжекцію обриву зв'язку на 1.5 с, перевірку Failsafe та розрахунок DTW-RMSE.
"""

import time
import math
import sys
from pymavlink import mavutil

class ScriptedOperatorHarness:
    def __init__(self, endpoint="udpin:0.0.0.0:14550", sysid=254):
        self.endpoint = endpoint
        self.sysid = sysid
        self.master = None
        self.telemetry_log = []

    def connect(self, timeout=10.0):
        """Відкриття з'єднання та очікування першого HEARTBEAT."""
        self.master = mavutil.mavlink_connection(
            self.endpoint,
            source_system=self.sysid,
            source_component=mavutil.mavlink.MAV_COMP_ID_MISSIONPLANNER
        )
        print(f"[*] Очікування серцебиття від апарата на {self.endpoint}...")
        msg = self.master.wait_heartbeat(timeout=timeout)
        if not msg:
            raise TimeoutError("Немає відповіді від автопілота!")
        print(f"[+] Зв'язок встановлено. Ціль: System {self.master.target_system}, Component {self.master.target_component}")

    def set_mode(self, mode_name, timeout=3.0):
        """Зміна режиму польоту з перевіркою підтвердження."""
        mode_id = self.master.mode_mapping().get(mode_name)
        if mode_id is None:
            raise ValueError(f"Невідомий режим: {mode_name}")

        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )

        t_start = time.monotonic()
        while time.monotonic() - t_start < timeout:
            msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5)
            if msg and msg.custom_mode == mode_id:
                print(f"[+] Режим перемкнено на {mode_name}")
                return True
        raise TimeoutError(f"Не вдалося встановити режим {mode_name} за {timeout} с")

    def arm_vehicle(self, timeout=5.0):
        """Команда на зведення двигунів (ARM)."""
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # confirmation
            1,  # 1 = ARM
            0, 0, 0, 0, 0, 0
        )
        t_start = time.monotonic()
        while time.monotonic() - t_start < timeout:
            msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5)
            if msg and (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
                print("[+] Двигуни зведено (ARMED)")
                return True
        raise RuntimeError("Відхилено команду ARM автопілотом")

    def send_rc_override(self, roll=1500, pitch=1500, throttle=1500, yaw=1500):
        """Надсилання сирих значень каналів PWM (1000..2000 мкс)."""
        self.master.mav.rc_channels_override_send(
            self.master.target_system,
            self.master.target_component,
            roll, pitch, throttle, yaw,
            0, 0, 0, 0
        )

    def log_telemetry_step(self):
        """Неблокуюче опитування стану для логування."""
        msg = self.master.recv_match(type=['ATTITUDE', 'GLOBAL_POSITION_INT', 'HEARTBEAT'], blocking=False)
        while msg:
            mtype = msg.get_type()
            if mtype == 'ATTITUDE':
                t_now = time.monotonic()
                self.telemetry_log.append({
                    't': t_now,
                    'roll': math.degrees(msg.roll),
                    'pitch': math.degrees(msg.pitch),
                    'yaw': math.degrees(msg.yaw)
                })
            msg = self.master.recv_match(type=['ATTITUDE', 'GLOBAL_POSITION_INT', 'HEARTBEAT'], blocking=False)

    def run_regression_scenario(self):
        """Виконання сценарію: набір висоти -> інжекція відмови лінка -> перевірка Failsafe."""
        print("[*] Старт регресійного тесту...")
        self.set_mode('GUIDED')
        self.arm_vehicle()

        # Фаза 1: Генерація команд керування (набір висоти та легкий крен)
        print("[*] Фаза 1: Подача команд RC Override (50 Гц)...")
        t_phase1 = time.monotonic()
        while time.monotonic() - t_phase1 < 3.0:
            # Throttle = 1650 мкс (підйом), Roll = 1550 мкс (невеликий крен вправо)
            self.send_rc_override(roll=1550, pitch=1500, throttle=1650, yaw=1500)
            self.log_telemetry_step()
            time.sleep(0.02)

        # Фаза 2: Інжекція відмови (обрив генерації пакетів)
        print("[*] Фаза 2: Штучний обрив зв'язку! Очікування Failsafe RTL...")
        t_drop = time.monotonic()
        failsafe_triggered = False
        t_trigger = 0.0

        # Спостерігаємо до 3 секунд за реакцією
        while time.monotonic() - t_drop < 3.0:
            self.log_telemetry_step()
            msg = self.master.recv_match(type='HEARTBEAT', blocking=False)
            if msg:
                # Режим RTL в ArduPilot типово має числовий код 6
                current_mode_str = self.master.flightmode
                if current_mode_str in ['RTL', 'LAND', 'AUTO']:
                    if not failsafe_triggered:
                        failsafe_triggered = True
                        t_trigger = time.monotonic()
                        print(f"[+] Failsafe активовано! Режим: {current_mode_str} через {t_trigger - t_drop:.3f} с")
            time.sleep(0.02)

        # Перевірка інваріанту таймінгу Failsafe (має спрацювати між 1.40 та 1.65 с)
        assert failsafe_triggered, "FAIL: Автопілот не активував аварійний режим після обриву зв'язку!"
        dt = t_trigger - t_drop
        assert 1.40 <= dt <= 1.65, f"FAIL: Час спрацювання Failsafe {dt:.3f} с виходить за межі [1.40, 1.65] с"
        print(f"[PASS] Таймінг Failsafe ідеальний: {dt:.3f} с")

    def compute_dtw_rmse(self, reference_log, max_warping_band=20):
        """Розрахунок DTW-відхилення зі смугою Сакое-Чіба між фактичним та еталонним логами."""
        if not self.telemetry_log or not reference_log:
            return 0.0

        A = [p['roll'] for p in self.telemetry_log]
        R = [p['roll'] for p in reference_log]
        N, M = len(A), len(R)

        # Матриця динамічного програмування
        D = [[float('inf')] * (M + 1) for _ in range(N + 1)]
        D[0][0] = 0.0

        for i in range(1, N + 1):
            j_min = max(1, i - max_warping_band)
            j_max = min(M, i + max_warping_band)
            for j in range(j_min, j_max + 1):
                cost = (A[i - 1] - R[j - 1]) ** 2
                D[i][j] = cost + min(D[i - 1][j],      # вставка
                                     D[i][j - 1],      # видалення
                                     D[i - 1][j - 1])  # збіг

        dtw_distance = math.sqrt(D[N][M] / max(N, M))
        return dtw_distance

if __name__ == "__main__":
    harness = ScriptedOperatorHarness(endpoint="udpin:0.0.0.0:14550")
    try:
        harness.connect(timeout=5.0)
        harness.run_regression_scenario()
        print("[SUCCESS] Тестовий сценарій виконано успішно.")
    except Exception as e:
        print(f"[ERROR] Помилка виконання тесту: {e}")
        sys.exit(1)
