import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class FlightRecord:
    time_boot_us: int
    roll_deg: float
    pitch_deg: float
    yaw_deg: float
    vbat_v: float
    ekf_sm_ratio: float
    rc_roll_in: float
    motor1_out: float
    imu_acc_z: float
    is_armed: bool

@dataclass
class GcsTelemetryPacket:
    time_utc_epoch_ms: int
    pitch_deg: float
    base_mode: int
    rc_channel_roll: int
    rssi_pct: int

@dataclass
class VideoFrameMetadata:
    frame_index: int
    pts_seconds: float
    dominant_audio_freq_hz: float

@dataclass
class AnchorEvent:
    name: str
    t_boot_us: int
    t_gcs_ms: int

@dataclass
class TimeAlignmentResult:
    alpha_drift: float
    beta_offset_ms: float
    video_offset_sec: float
    residual_rms_ms: float

@dataclass
class IncidentVerdict:
    root_cause: str
    confidence: float
    description: str


class IncidentReconstructionEngine:
    @staticmethod
    def compute_cross_correlation_offset(sig_a: List[float], sig_b: List[float], dt_sec: float, max_lag: int) -> float:
        n = len(sig_a)
        if n == 0 or len(sig_b) != n:
            return 0.0

        mean_a = sum(sig_a) / n
        mean_b = sum(sig_b) / n

        var_a = sum((x - mean_a) ** 2 for x in sig_a)
        var_b = sum((y - mean_b) ** 2 for y in sig_b)

        if var_a < 1e-6 or var_b < 1e-6:
            return 0.0

        std_prod = math.sqrt(var_a * var_b)
        max_corr = -1.0
        best_lag = 0

        for lag in range(-max_lag, max_lag + 1):
            cov = 0.0
            count = 0
            for i in range(n):
                j = i + lag
                if 0 <= j < n:
                    cov += (sig_a[i] - mean_a) * (sig_b[j] - mean_b)
                    count += 1
            if count > n // 2:
                r = cov / std_prod
                if r > max_corr:
                    max_corr = r
                    best_lag = lag

        return best_lag * dt_sec

    @staticmethod
    def align_clocks_linear_regression(anchors: List[AnchorEvent], video_spool_sec: float) -> TimeAlignmentResult:
        p = len(anchors)
        if p < 2:
            return TimeAlignmentResult(1.0, 0.0, 0.0, 0.0)

        t_boot_ms = [a.t_boot_us / 1000.0 for a in anchors]
        t_gcs_ms = [float(a.t_gcs_ms) for a in anchors]

        mean_tb = sum(t_boot_ms) / p
        mean_tg = sum(t_gcs_ms) / p

        cov = sum((tb - mean_tb) * (tg - mean_tg) for tb, tg in zip(t_boot_ms, t_gcs_ms))
        var_tb = sum((tb - mean_tb) ** 2 for tb in t_boot_ms)

        alpha = (cov / var_tb) if var_tb > 1e-9 else 1.0
        beta = mean_tg - alpha * mean_tb

        sq_err = sum((tg - (alpha * tb + beta)) ** 2 for tb, tg in zip(t_boot_ms, t_gcs_ms))
        rms = math.sqrt(sq_err / p)
        vid_offset = (anchors[0].t_boot_us / 1e6) - video_spool_sec

        return TimeAlignmentResult(alpha, beta, vid_offset, rms)

    @staticmethod
    def diagnose_incident(
        flight_records: List[FlightRecord],
        gcs_records: List[GcsTelemetryPacket],
        video_records: List[VideoFrameMetadata]
    ) -> IncidentVerdict:
        if not flight_records:
            return IncidentVerdict("UNKNOWN_NO_DATA", 0.0, "Бортовий лог порожній або відсутній.")

        last_rec = flight_records[-1]

        # 1. Раптове знеструмлення
        if 0.0 < last_rec.vbat_v < 10.0 and abs(last_rec.imu_acc_z) > 15.0:
            return IncidentVerdict(
                "HARDWARE_POWER_LOSS",
                0.98,
                "Раптове падіння напруги живлення нижче межі утримання MCU зі сплеском перевантаження IMU. Журнал обірвано без збереження буфера."
            )

        # 2. Розбіжність інновацій EKF
        for rec in flight_records:
            if rec.ekf_sm_ratio > 1.0:
                return IncidentVerdict(
                    "SENSOR_EKF_DIVERGENCE",
                    0.94,
                    "Перевищення критичного порогу інноваційного тесту EKF у каналі магнітометра (SM > 1.0). Розвиток розбіжної спіралі утримання позиції."
                )

        # 3. Команда пілота чи зрив ESC
        pilot_command = any(abs(r.rc_roll_in - 1500.0) > 350.0 for r in flight_records)
        motor_sat = any(r.motor1_out > 0.98 and abs(r.roll_deg) > 45.0 for r in flight_records)

        if motor_sat and not pilot_command:
            return IncidentVerdict(
                "ACTUATOR_ESC_DESYNC",
                0.91,
                "Повне насичення виходу регулятора мотора при нейтральному положенні стіків пілота. Відмова комутації ESC або зрив пропелера."
            )

        if pilot_command:
            return IncidentVerdict(
                "PILOT_CFIT_COLLISION",
                0.89,
                "Апарат точно виконував екстремальне кутове завдання пілота аж до точки фізичного контакту з перешкодою."
            )

        return IncidentVerdict("UNDETERMINED_ANOMALY", 0.50, "Ознак критичних збоїв не виявлено, потрібен покадровий ручний аудит.")


if __name__ == "__main__":
    print("[FUSER] Ініціалізація мультимодального розбору інциденту...")

    anchors = [
        AnchorEvent("ARMING", 12450000, 1724753532564),
        AnchorEvent("TAKEOFF_SPOOL", 18200000, 1724753538314),
        AnchorEvent("MODE_AUTO", 65120000, 1724753585235),
        AnchorEvent("IMPACT_SHOCK", 422450000, 1724753942571),
    ]

    sync = IncidentReconstructionEngine.align_clocks_linear_regression(anchors, 15.87)
    print(f"  Коефіцієнт дрейфу (alpha): {sync.alpha_drift:.8f} ({(sync.alpha_drift - 1.0)*1e6:.1f} ppm)")
    print(f"  Зсув епохи (beta): {sync.beta_offset_ms:.3f} ms")
    print(f"  Зсув відео (PTS): {sync.video_offset_sec:.3f} s")
    print(f"  Залишкова похибка (RMS): {sync.residual_rms_ms:.3f} ms")

    records = [
        FlightRecord(422440000, 2.1, 1.2, 180.0, 22.4, 0.12, 1500.0, 0.45, -9.8, True),
        FlightRecord(422445000, 2.2, 1.3, 180.1, 22.3, 0.13, 1500.0, 0.46, -9.9, True),
        FlightRecord(422450000, 2.3, 1.4, 180.2, 5.1, 0.13, 1500.0, 0.46, 18.4, True),
    ]

    verdict = IncidentReconstructionEngine.diagnose_incident(records, [], [])
    print(f"\n[ДІАГНОЗ]: {verdict.root_cause} (Достовірність: {verdict.confidence * 100:.1f}%)")
    print(f"Опис: {verdict.description}")
