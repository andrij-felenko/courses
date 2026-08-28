#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iomanip>
#include <chrono>
#include <optional>
#include <span>

struct FlightRecord {
    uint64_t time_boot_us;
    float roll_deg;
    float pitch_deg;
    float yaw_deg;
    float vbat_v;
    float ekf_sm_ratio;
    float rc_roll_in;
    float motor1_out;
    float imu_acc_z;
    bool is_armed;
};

struct GcsTelemetryPacket {
    uint64_t time_utc_epoch_ms;
    float pitch_deg;
    uint8_t base_mode;
    int16_t rc_channel_roll;
    uint8_t rssi_pct;
};

struct VideoFrameMetadata {
    uint32_t frame_index;
    double pts_seconds;
    float dominant_audio_freq_hz;
};

struct AnchorEvent {
    std::string name;
    uint64_t t_boot_us;
    uint64_t t_gcs_ms;
};

struct TimeAlignmentResult {
    double alpha_drift;
    double beta_offset_ms;
    double video_offset_sec;
    double residual_rms_ms;
};

struct IncidentVerdict {
    std::string root_cause;
    double confidence;
    std::string description;
};

class IncidentReconstructionEngine {
public:
    static double compute_cross_correlation_offset(
        std::span<const float> sig_a,
        std::span<const float> sig_b,
        double dt_sec,
        int max_lag_samples
    ) {
        if (sig_a.empty() || sig_b.empty() || sig_a.size() != sig_b.size()) {
            return 0.0;
        }

        const size_t n = sig_a.size();
        const double mean_a = std::accumulate(sig_a.begin(), sig_a.end(), 0.0) / n;
        const double mean_b = std::accumulate(sig_b.begin(), sig_b.end(), 0.0) / n;

        double var_a = 0.0, var_b = 0.0;
        for (size_t i = 0; i < n; ++i) {
            var_a += (sig_a[i] - mean_a) * (sig_a[i] - mean_a);
            var_b += (sig_b[i] - mean_b) * (sig_b[i] - mean_b);
        }

        if (var_a < 1e-6 || var_b < 1e-6) return 0.0;
        const double std_product = std::sqrt(var_a * var_b);

        double max_corr = -1.0;
        int best_lag = 0;

        for (int lag = -max_lag_samples; lag <= max_lag_samples; ++lag) {
            double current_cov = 0.0;
            size_t count = 0;

            for (size_t i = 0; i < n; ++i) {
                int j = static_cast<int>(i) + lag;
                if (j >= 0 && j < static_cast<int>(n)) {
                    current_cov += (sig_a[i] - mean_a) * (sig_b[j] - mean_b);
                    count++;
                }
            }

            if (count > n / 2) {
                double r = current_cov / std_product;
                if (r > max_corr) {
                    max_corr = r;
                    best_lag = lag;
                }
            }
        }

        return best_lag * dt_sec;
    }

    static TimeAlignmentResult align_clocks_linear_regression(
        std::span<const AnchorEvent> anchors,
        double video_spool_sec
    ) {
        const size_t p = anchors.size();
        if (p < 2) {
            return {1.0, 0.0, 0.0, 0.0};
        }

        double sum_t_boot = 0.0, sum_t_gcs = 0.0;
        for (const auto& a : anchors) {
            double tb_ms = static_cast<double>(a.t_boot_us) / 1000.0;
            sum_t_boot += tb_ms;
            sum_t_gcs += static_cast<double>(a.t_gcs_ms);
        }

        const double mean_tb = sum_t_boot / p;
        const double mean_tg = sum_t_gcs / p;

        double cov = 0.0, var_tb = 0.0;
        for (const auto& a : anchors) {
            double tb_ms = (static_cast<double>(a.t_boot_us) / 1000.0) - mean_tb;
            double tg_ms = static_cast<double>(a.t_gcs_ms) - mean_tg;
            cov += tb_ms * tg_ms;
            var_tb += tb_ms * tb_ms;
        }

        const double alpha = (var_tb > 1e-9) ? (cov / var_tb) : 1.0;
        const double beta = mean_tg - alpha * mean_tb;

        double sum_sq_err = 0.0;
        for (const auto& a : anchors) {
            double tb_ms = static_cast<double>(a.t_boot_us) / 1000.0;
            double pred_tg = alpha * tb_ms + beta;
            double diff = static_cast<double>(a.t_gcs_ms) - pred_tg;
            sum_sq_err += diff * diff;
        }

        const double rms = std::sqrt(sum_sq_err / p);
        const double vid_offset = (static_cast<double>(anchors[0].t_boot_us) / 1e6) - video_spool_sec;

        return {alpha, beta, vid_offset, rms};
    }

    static IncidentVerdict diagnose_incident(
        std::span<const FlightRecord> flight_records,
        std::span<const GcsTelemetryPacket> gcs_records,
        std::span<const VideoFrameMetadata> video_records
    ) {
        if (flight_records.empty()) {
            return {"UNKNOWN_NO_DATA", 0.0, "Бортовий лог порожній або відсутній."};
        }

        const auto& last_rec = flight_records.back();

        // Правило 1: Раптове знеструмлення (Power Rail Brownout)
        if (last_rec.vbat_v > 0.0f && last_rec.vbat_v < 10.0f && std::abs(last_rec.imu_acc_z) > 15.0f) {
            return {
                "HARDWARE_POWER_LOSS",
                0.98,
                "Раптове падіння напруги живлення нижче межі утримання MCU зі сплеском перевантаження IMU. Журнал обірвано без збереження буфера."
            };
        }

        // Правило 2: Зрив сенсора та розбіжність EKF інновацій
        for (const auto& rec : flight_records) {
            if (rec.ekf_sm_ratio > 1.0f) {
                return {
                    "SENSOR_EKF_DIVERGENCE",
                    0.94,
                    "Перевищення критичного порогу інноваційного тесту EKF у каналі магнітометра (SM > 1.0). Розвиток розбіжної спіралі утримання позиції."
                };
            }
        }

        // Правило 3: Зіткнення з вини пілота чи відмова приводу
        bool pilot_commanded_turn = false;
        bool motor_saturated = false;

        for (const auto& rec : flight_records) {
            if (std::abs(rec.rc_roll_in - 1500.0f) > 350.0f) {
                pilot_commanded_turn = true;
            }
            if (rec.motor1_out > 0.98f && std::abs(rec.roll_deg) > 45.0f) {
                motor_saturated = true;
            }
        }

        if (motor_saturated && !pilot_commanded_turn) {
            return {
                "ACTUATOR_ESC_DESYNC",
                0.91,
                "Повне насичення виходу регулятора мотора при нейтральному положенні стіків пілота. Відмова комутації ESC або зрив пропелера."
            };
        }

        if (pilot_commanded_turn) {
            return {
                "PILOT_CFIT_COLLISION",
                0.89,
                "Апарат точно виконував екстремальне кутове завдання пілота аж до точки фізичного контакту з перешкодою."
            };
        }

        return {"UNDETERMINED_ANOMALY", 0.50, "Ознак критичних збоїв не виявлено, потрібен покадровий ручний аудит."};
    }
};

int main() {
    std::cout << "[FUSER] Ініціалізація мультимодального розбору інциденту..." << std::endl;

    std::vector<AnchorEvent> anchors = {
        {"ARMING", 12450000ULL, 1724753532564ULL},
        {"TAKEOFF_SPOOL", 18200000ULL, 1724753538314ULL},
        {"MODE_AUTO", 65120000ULL, 1724753585235ULL},
        {"IMPACT_SHOCK", 422450000ULL, 1724753942571ULL}
    };

    auto sync = IncidentReconstructionEngine::align_clocks_linear_regression(anchors, 15.87);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "  Коефіцієнт дрейфу (alpha): " << sync.alpha_drift
              << " (" << (sync.alpha_drift - 1.0) * 1e6 << " ppm)" << std::endl;
    std::cout << "  Зсув епохи (beta): " << sync.beta_offset_ms << " ms" << std::endl;
    std::cout << "  Зсув відео (PTS): " << sync.video_offset_sec << " s" << std::endl;
    std::cout << "  Залишкова похибка (RMS): " << sync.residual_rms_ms << " ms" << std::endl;

    std::vector<FlightRecord> records = {
        {422440000ULL, 2.1f, 1.2f, 180.0f, 22.4f, 0.12f, 1500.0f, 0.45f, -9.8f, true},
        {422445000ULL, 2.2f, 1.3f, 180.1f, 22.3f, 0.13f, 1500.0f, 0.46f, -9.9f, true},
        {422450000ULL, 2.3f, 1.4f, 180.2f, 5.1f,  0.13f, 1500.0f, 0.46f, 18.4f, true}
    };

    std::vector<GcsTelemetryPacket> gcs_dummy;
    std::vector<VideoFrameMetadata> vid_dummy;

    auto verdict = IncidentReconstructionEngine::diagnose_incident(records, gcs_dummy, vid_dummy);

    std::cout << "\n[ДІАГНОЗ]: " << verdict.root_cause << " (Достовірність: "
              << verdict.confidence * 100.0 << "%)" << std::endl;
    std::cout << "Опис: " << verdict.description << std::endl;

    return 0;
}
