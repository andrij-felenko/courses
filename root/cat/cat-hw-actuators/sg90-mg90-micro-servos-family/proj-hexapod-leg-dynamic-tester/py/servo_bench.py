"""
Модуль взаємодії з випробувальним стендом мікросервоприводів через послідовний порт.

Забезпечує:
- Двосторонній обмін даними між керуючим комп'ютером і стендом (UART/Serial).
- Передачу тестових профілів руху (ступінчастий стрибок, плавний реверс, блокування вала).
- Потоковий розбір і валідацію телеметричних пакетів із контрольною сумою CRC-8.
- Вбудовану фізико-математичну модель випробувального стенда (HIL симулятор)
  для автономного тестування та верифікації алгоритмів без фізичного обладнання.
"""

from dataclasses import dataclass
import math
import random
import time
from typing import List, Dict, Tuple, Optional, Any

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


def calculate_crc8(data: bytes) -> int:
    """
    Обчислює контрольну суму CRC-8 за стандартним поліномом 0x07 (x^8 + x^2 + x + 1).
    
    :param data: Послідовність байтів телеметричного кадру.
    :return: 8-бітне значення контрольної суми [0..255].
    """
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


@dataclass
class TelemetryRecord:
    """
    Синхронізований часовий зріз вимірювань випробувального стенда.

    Атрибути:
        timestamp_s: Часова мітка від початку тестового сценарію, с.
        target_angle_deg: Заданий кут положення вала (команда керування), градуси.
        actual_angle_deg: Фактичний кут вала за показами вимірювального енкодера, градуси.
        current_ma: Струм споживання сервопривода (виміряний шунтом), мА.
        load_torque_mNm: Механічний момент навантаження на валу, мН·м.
        voltage_v: Напруга на лінії живлення привода, В.
        is_stalled: Прапорець апаратного виявлення блокування ротора.
    """
    timestamp_s: float
    target_angle_deg: float
    actual_angle_deg: float
    current_ma: float
    load_torque_mNm: float = 0.0
    voltage_v: float = 5.0
    is_stalled: bool = False

    def to_frame(self) -> str:
        """
        Серіалізує запис у текстовий кадр протоколу стенда з контрольною сумою CRC-8:
        $TLM,<time_ms>,<target_deg>,<actual_deg>,<current_ma>,<load_mNm>,<flags>*<crc_hex>
        """
        flags = 1 if self.is_stalled else 0
        payload = (
            f"$TLM,{self.timestamp_s * 1000.0:.1f},"
            f"{self.target_angle_deg:.2f},{self.actual_angle_deg:.2f},"
            f"{self.current_ma:.1f},{self.load_torque_mNm:.2f},{flags}"
        )
        crc = calculate_crc8(payload.encode("ascii"))
        return f"{payload}*{crc:02X}\r\n"

    @classmethod
    def from_frame(cls, frame_str: str) -> "TelemetryRecord":
        """
        Розбирає сирий текстовий рядок кадру телеметрії, валідує CRC-8 та повертає об'єкт.

        :raises ValueError: Якщо формат кадру пошкоджено або не збігається контрольна сума.
        """
        clean = frame_str.strip()
        if not clean.startswith("$TLM,") or "*" not in clean:
            raise ValueError(f"Некоректний префікс або розділювач кадру: '{frame_str}'")

        payload, crc_hex = clean.split("*", 1)
        expected_crc = calculate_crc8(payload.encode("ascii"))
        try:
            received_crc = int(crc_hex, 16)
        except ValueError as err:
            raise ValueError(f"Помилка шістнадцяткового формату CRC: '{crc_hex}'") from err

        if expected_crc != received_crc:
            raise ValueError(
                f"Помилка валідації CRC-8: отримано 0x{received_crc:02X}, "
                f"очікувалося 0x{expected_crc:02X} для кадру '{payload}'"
            )

        fields = payload.split(",")
        if len(fields) < 7:
            raise ValueError(f"Недостатньо полів у кадрі телеметрії: {payload}")

        return cls(
            timestamp_s=float(fields[1]) / 1000.0,
            target_angle_deg=float(fields[2]),
            actual_angle_deg=float(fields[3]),
            current_ma=float(fields[4]),
            load_torque_mNm=float(fields[5]),
            is_stalled=(int(fields[6]) & 0x01) != 0,
        )


@dataclass(frozen=True)
class ServoConfig:
    """
    Інженерні параметри та паспортні характеристики сервопривода.

    Параметри:
        name: Назва моделі (SG90, SG92R, MG90S, MG90D).
        gear_material: Матеріал шестерень редуктора (Нейлон, Карбон, Метал).
        controller_type: Архітектура контуру керування (Аналоговий 50 Гц чи Цифровий 300 Гц).
        mass_g: Конструкційна маса привода, г.
        stall_torque_mNm: Паспортний момент блокування вала, мН·м.
        stall_current_ma: Струм короткого замикання (блокування ротора), мА.
        idle_current_ma: Струм спокою внутрішньої електроніки, мА.
        max_speed_deg_s: Максимальна швидкість повороту вала на холостому ходу, °/с.
        accel_time_s: Постійна часу розгону (інерційність ротора та редуктора), с.
        proportional_band_deg: Ширина пропорційної зони регулятора, градуси.
        deadband_deg: Ширина зони нечутливості (deadband), градуси.
        dynamic_brake_gain: Коефіцієнт активного динамічного гальмування H-мостом.
        backlash_deg: Кутовий люфт зубчастого зачеплення редуктора, градуси.
        protection_trip_time_s: Таймаут струмового захисту випробувального стенда, с.
    """
    name: str
    gear_material: str
    controller_type: str
    mass_g: float
    stall_torque_mNm: float
    stall_current_ma: float
    idle_current_ma: float
    max_speed_deg_s: float
    accel_time_s: float
    proportional_band_deg: float
    deadband_deg: float
    dynamic_brake_gain: float
    backlash_deg: float
    protection_trip_time_s: float = 0.175


SERVO_CONFIGS: Dict[str, ServoConfig] = {
    "SG90": ServoConfig(
        name="SG90",
        gear_material="Нейлон (POM)",
        controller_type="Аналоговий (50 Гц)",
        mass_g=9.0,
        stall_torque_mNm=176.5,     # 1.8 кг·см
        stall_current_ma=650.0,
        idle_current_ma=12.0,
        max_speed_deg_s=500.0,      # 0.12 с / 60°
        accel_time_s=0.038,         # Легкий ротор, пружні пластикові зуби
        proportional_band_deg=9.0,
        deadband_deg=0.45,          # ~4 мкс
        dynamic_brake_gain=0.0,     # Без активного гальмування
        backlash_deg=0.40,
        protection_trip_time_s=0.175,
    ),
    "SG92R": ServoConfig(
        name="SG92R",
        gear_material="Вуглепластик (CF-POM)",
        controller_type="Аналоговий (50 Гц)",
        mass_g=9.0,
        stall_torque_mNm=245.0,     # 2.5 кг·см
        stall_current_ma=750.0,
        idle_current_ma=14.0,
        max_speed_deg_s=600.0,      # 0.10 с / 60°
        accel_time_s=0.025,         # Висока жорсткість композиту зуба
        proportional_band_deg=10.5,
        deadband_deg=0.35,          # ~3 мкс
        dynamic_brake_gain=0.20,    # Підвищене внутрішнє демпфування композиту
        backlash_deg=0.30,
        protection_trip_time_s=0.175,
    ),
    "MG90S": ServoConfig(
        name="MG90S",
        gear_material="Метал (Латунь/Алюміній)",
        controller_type="Аналоговий (50 Гц)",
        mass_g=13.4,
        stall_torque_mNm=215.0,     # 2.2 кг·см
        stall_current_ma=850.0,
        idle_current_ma=15.0,
        max_speed_deg_s=520.0,      # 0.11 с / 60°
        accel_time_s=0.075,         # Важкий металевий зубчастий ряд, висока інерція
        proportional_band_deg=7.0,
        deadband_deg=0.45,
        dynamic_brake_gain=0.0,     # Аналоговий чип без випереджального гальмування
        backlash_deg=0.65,          # Механічний зазор металевих зубів
        protection_trip_time_s=0.175,
    ),
    "MG90D": ServoConfig(
        name="MG90D",
        gear_material="Метал + Підшипник",
        controller_type="Цифровий (300 Гц)",
        mass_g=13.4,
        stall_torque_mNm=250.0,     # 2.55 кг·см
        stall_current_ma=1050.0,
        idle_current_ma=20.0,       # Потужніший мікроконтролер контуру
        max_speed_deg_s=680.0,      # 0.085 с / 60°
        accel_time_s=0.022,         # Висока частота внутрішнього ШІМ
        proportional_band_deg=6.0,
        deadband_deg=0.15,          # Вузька цифрова зона нечутливості ~1.2 мкс
        dynamic_brake_gain=0.75,    # Активне реверсивне електродинамічне гальмування
        backlash_deg=0.35,
        protection_trip_time_s=0.175,
    ),
}


class ServoBenchSimulator:
    """
    Фізико-математичний симулятор випробувального стенда мікросервоприводів.

    Відтворює нелінійну електромеханічну динаміку:
    - Інерційні характеристики ротора та зубчастого ряду (accel_time_s).
    - Вплив матеріалу шестерень на демпфування та перерегулювання.
    - Дискретизацію контуру керування (50 Гц аналоговий vs 300 Гц цифровий із гальмуванням).
    - Стрибок струму під час механічного упору (stall) та спрацьовування захисту стенда.
    """

    def __init__(self, config: ServoConfig):
        self.config = config
        self.reset()

    def reset(self, initial_angle: float = 0.0) -> None:
        """Скидає стан моделі до початкових умов."""
        self.theta = initial_angle
        self.vel = 0.0
        self.t = 0.0
        self.is_stalled = False
        self.stall_timer = 0.0
        self.tripped = False

    def simulate_step(
        self,
        dt: float,
        target_angle: float,
        obstacle_angle: Optional[float] = None,
        load_torque_mNm: float = 0.0,
    ) -> TelemetryRecord:
        """
        Інтегрує крок динаміки за час dt та повертає кадр телеметрії.

        :param dt: Крок дискретизації часу, секунди.
        :param target_angle: Командний кут вала, градуси.
        :param obstacle_angle: Кут механічного стопора для тестування блокування.
        :param load_torque_mNm: Протидіючий зовнішній момент, мН·м.
        """
        self.t += dt

        # 1. Режим аварійного механічного блокування вала
        if obstacle_angle is not None and self.theta >= obstacle_angle and target_angle > obstacle_angle:
            self.theta = obstacle_angle
            self.vel = 0.0
            self.is_stalled = True
            self.stall_timer += dt

            # Перевірка спрацьовування апаратного захисту стенда за таймаутом
            if self.stall_timer >= self.config.protection_trip_time_s:
                self.tripped = True

            if self.tripped:
                # Після відсікання живлення струм падає до струму холостого спокою схеми
                current = self.config.idle_current_ma + random.gauss(0.0, 0.4)
            else:
                # Експоненційне наростання струму до струму блокування stall_current
                alpha = min(1.0, self.stall_timer / 0.012)
                current = (
                    self.config.idle_current_ma
                    + (self.config.stall_current_ma - self.config.idle_current_ma) * alpha
                    + random.gauss(0.0, 2.0)
                )

            # Просідання напруги живлення на опорі підвідних дротів (R_wire ~ 0.18 Ом)
            v_drop = (current / 1000.0) * 0.18
            return TelemetryRecord(
                timestamp_s=round(self.t, 4),
                target_angle_deg=target_angle,
                actual_angle_deg=round(self.theta, 2),
                current_ma=max(0.0, round(current, 1)),
                load_torque_mNm=load_torque_mNm if not self.tripped else 0.0,
                voltage_v=round(5.0 - v_drop, 2),
                is_stalled=self.is_stalled and not self.tripped,
            )

        # 2. Штатний рух вала
        err = target_angle - self.theta
        if abs(err) < self.config.deadband_deg:
            duty = 0.0
        else:
            duty = max(-1.0, min(1.0, err / self.config.proportional_band_deg))
            # Активне динамічне гальмування (H-bridge brake mode) для цифрових серв
            if self.config.dynamic_brake_gain > 0 and abs(err) < 12.0 and (self.vel * err > 0):
                duty -= (self.vel / self.config.max_speed_deg_s) * self.config.dynamic_brake_gain

        target_v = duty * self.config.max_speed_deg_s
        dv = (target_v - self.vel) / self.config.accel_time_s * dt
        self.vel += dv
        self.theta += self.vel * dt

        # Додавання апаратного шуму оптичного енкодера стенда
        measured_theta = self.theta + random.gauss(0.0, 0.03)

        # Розрахунок струму: спокій + динамічна складова швидкості + момент навантаження
        speed_ratio = abs(self.vel) / self.config.max_speed_deg_s
        accel_ratio = min(1.0, abs(dv / dt) / 25000.0)
        run_current = 160.0 * speed_ratio + 80.0 * accel_ratio
        current = (
            self.config.idle_current_ma
            + run_current
            + (load_torque_mNm / self.config.stall_torque_mNm) * self.config.stall_current_ma * 0.5
            + random.gauss(0.0, 1.5)
        )

        v_drop = (current / 1000.0) * 0.18
        return TelemetryRecord(
            timestamp_s=round(self.t, 4),
            target_angle_deg=target_angle,
            actual_angle_deg=round(measured_theta, 2),
            current_ma=max(0.0, round(current, 1)),
            load_torque_mNm=load_torque_mNm,
            voltage_v=round(5.0 - v_drop, 2),
            is_stalled=False,
        )


class ServoTestbenchClient:
    """
    Клієнт взаємодії з випробувальним стендом через послідовний інтерфейс (UART/Serial).

    Керує фізичним підключенням до мікроконтролера стенда або прозоро перемикається
    на вбудований фізичний симулятор ServoBenchSimulator у разі відсутності COM-порту.
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 115200,
        timeout: float = 0.5,
        model_name: str = "SG90",
        use_simulator: bool = True,
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.model_name = model_name
        self.use_simulator = use_simulator

        self.config = SERVO_CONFIGS.get(model_name, SERVO_CONFIGS["SG90"])
        self.simulator = ServoBenchSimulator(self.config)
        self.serial_conn: Optional[Any] = None

        # Лічильники статистики зв'язку
        self.frames_received = 0
        self.frames_valid = 0
        self.crc_errors = 0

    def connect(self) -> bool:
        """
        Встановлює зв'язок із реальним обладнанням стенда або ініціалізує симулятор.
        """
        if self.use_simulator or self.port is None:
            self.simulator.reset()
            return True

        if not SERIAL_AVAILABLE:
            self.use_simulator = True
            self.simulator.reset()
            return True

        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            return True
        except Exception:
            # Якщо COM-порт недоступний, використовуємо симулятор без аварійного падіння
            self.use_simulator = True
            self.simulator.reset()
            return True

    def disconnect(self) -> None:
        """Акуратно розриває з'єднання та переводить стенд у безпечний стан."""
        if self.serial_conn and hasattr(self.serial_conn, "is_open") and self.serial_conn.is_open:
            try:
                self.send_command("CMD:STOP")
                self.serial_conn.close()
            except Exception:
                pass
        self.serial_conn = None

    def send_command(self, cmd: str) -> None:
        """Надсилає текстову команду керування стенду."""
        if self.serial_conn and hasattr(self.serial_conn, "is_open") and self.serial_conn.is_open:
            data = (cmd.strip() + "\r\n").encode("ascii")
            self.serial_conn.write(data)

    def run_step_test(
        self,
        from_angle: float,
        to_angle: float,
        duration_s: float = 0.5,
        sample_rate_hz: int = 200,
    ) -> List[TelemetryRecord]:
        """
        Виконує стендовий тест сходинкового збурення (Step Response Test).
        
        :param from_angle: Початкове положення вала, градуси.
        :param to_angle: Цільовий кут переміщення, градуси.
        :param duration_s: Загальна тривалість запису телеметрії, секунди.
        :param sample_rate_hz: Частота вибірки телеметрії, Гц.
        :return: Список структурованих записів TelemetryRecord.
        """
        dt = 1.0 / sample_rate_hz
        steps = int(duration_s * sample_rate_hz)
        records: List[TelemetryRecord] = []

        if self.use_simulator:
            self.simulator.reset(initial_angle=from_angle)
            for _ in range(steps):
                rec = self.simulator.simulate_step(dt=dt, target_angle=to_angle)
                records.append(rec)
        else:
            self.send_command(f"CMD:STEP,{from_angle:.1f},{to_angle:.1f},{duration_s:.2f}")
            records = self._read_hardware_stream(duration_s, steps)

        return records

    def run_reversal_sweep(
        self,
        angle_a: float,
        angle_b: float,
        speed_deg_s: float = 500.0,
        cycles: int = 2,
        sample_rate_hz: int = 200,
    ) -> List[TelemetryRecord]:
        """
        Виконує циклічний тест швидкісного реверсу вала (Reversal Test)
        для оцінки кутового люфту зубчастого ряду та сплесків струму зміни напрямку.
        """
        dt = 1.0 / sample_rate_hz
        records: List[TelemetryRecord] = []
        travel = abs(angle_b - angle_a)
        leg_duration = (travel / speed_deg_s) + 0.15  # час ходу + час заспокоєння
        total_duration = leg_duration * 2 * cycles
        steps_per_leg = int(leg_duration * sample_rate_hz)

        if self.use_simulator:
            self.simulator.reset(initial_angle=angle_a)
            for cycle in range(cycles):
                # Рух у бік B
                for _ in range(steps_per_leg):
                    rec = self.simulator.simulate_step(dt=dt, target_angle=angle_b)
                    records.append(rec)
                # Реверс у бік A
                for _ in range(steps_per_leg):
                    rec = self.simulator.simulate_step(dt=dt, target_angle=angle_a)
                    records.append(rec)
        else:
            self.send_command(f"CMD:REVERSE,{angle_a:.1f},{angle_b:.1f},{speed_deg_s:.1f},{cycles}")
            records = self._read_hardware_stream(total_duration, steps_per_leg * 2 * cycles)

        return records

    def run_stall_test(
        self,
        target_angle: float = 90.0,
        obstacle_angle: float = 45.0,
        duration_s: float = 0.45,
        sample_rate_hz: int = 200,
    ) -> List[TelemetryRecord]:
        """
        Виконує стендовий тест аварійного блокування вала (Stall Protection Test).
        Фіксує стрибок струму короткого замикання та точний час спрацьовування захисту.
        """
        dt = 1.0 / sample_rate_hz
        steps = int(duration_s * sample_rate_hz)
        records: List[TelemetryRecord] = []

        if self.use_simulator:
            self.simulator.reset(initial_angle=0.0)
            for _ in range(steps):
                rec = self.simulator.simulate_step(
                    dt=dt,
                    target_angle=target_angle,
                    obstacle_angle=obstacle_angle,
                )
                records.append(rec)
        else:
            self.send_command(f"CMD:STALL,{target_angle:.1f},{obstacle_angle:.1f},{duration_s:.2f}")
            records = self._read_hardware_stream(duration_s, steps)

        return records

    def _read_hardware_stream(self, duration_s: float, expected_steps: int) -> List[TelemetryRecord]:
        """Зчитує та розбирає кадри телеметрії з фізичного послідовного порту."""
        records: List[TelemetryRecord] = []
        if not self.serial_conn:
            return records

        t_end = time.time() + duration_s + 0.5
        line_buffer = b""

        while time.time() < t_end and len(records) < expected_steps:
            if self.serial_conn.in_waiting > 0:
                chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                line_buffer += chunk
                while b"\n" in line_buffer:
                    line_bytes, line_buffer = line_buffer.split(b"\n", 1)
                    raw_str = line_bytes.decode("ascii", errors="replace").strip()
                    if not raw_str:
                        continue
                    self.frames_received += 1
                    try:
                        record = TelemetryRecord.from_frame(raw_str)
                        records.append(record)
                        self.frames_valid += 1
                    except ValueError:
                        self.crc_errors += 1
            else:
                time.sleep(0.002)

        return records
