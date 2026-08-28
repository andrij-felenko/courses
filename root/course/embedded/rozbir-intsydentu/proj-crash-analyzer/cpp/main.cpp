#include <cmath>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

namespace postmortem {

enum class FaultType {
    None,
    MotorEscLoss,
    MagneticInterference,
    BrownoutVoltageSag,
    SensorBusLockup
};

struct TelemetryFrame {
    uint64_t timestamp_us{0};
    float roll_des_deg{0.0f};
    float roll_act_deg{0.0f};
    float yaw_des_deg{0.0f};
    float yaw_act_deg{0.0f};
    std::vector<float> motor_out; // нормовані виходи моторів
    float bat_voltage_v{0.0f};
    float bat_current_a{0.0f};
    float ekf_mag_innov{0.0f};
    float gyro_x_rads{0.0f};
    uint32_t sensor_status_mask{0};
};

struct IncidentReport {
    FaultType fault{FaultType::None};
    uint64_t timestamp_us{0};
    float confidence{0.0f};
    std::string_view description;
};

class CrashAnalyzer {
public:
    static IncidentReport analyze(std::span<const TelemetryFrame> frames) {
        if (frames.size() < 30) {
            return {FaultType::None, 0, 0.0f, "Замало даних для формування вікна аналізу"};
        }

        size_t motor_sat_count = 0;
        size_t mag_fault_count = 0;
        size_t sensor_freeze_count = 0;
        float prev_gyro = frames.front().gyro_x_rads;

        for (const auto &f : frames) {
            // 1. Brownout: глибоке падіння напруги під навантаженням
            if (f.bat_voltage_v < 13.2f && f.bat_current_a > 25.0f) {
                return {
                    FaultType::BrownoutVoltageSag,
                    f.timestamp_us,
                    0.95f,
                    "Критичне просідання напруги батареї (Brownout) під струмовим навантаженням"
                };
            }

            // 2. Апаратна відмова шини давачів
            if ((f.sensor_status_mask & 0x01) == 0) {
                return {
                    FaultType::SensorBusLockup,
                    f.timestamp_us,
                    1.0f,
                    "Апаратна відмова шини IMU (I2C/SPI timeout або втрата зв'язку)"
                };
            }

            if (std::abs(f.gyro_x_rads - prev_gyro) < 1e-6f) {
                if (++sensor_freeze_count > 25) {
                    return {
                        FaultType::SensorBusLockup,
                        f.timestamp_us,
                        0.90f,
                        "Застигання показів гіроскопа (Sensor freeze) на постійному значенні"
                    };
                }
            } else {
                sensor_freeze_count = 0;
            }
            prev_gyro = f.gyro_x_rads;

            // 3. Асиметрія виходів моторів (Motor / ESC failure)
            if (f.motor_out.size() >= 2) {
                const bool saturated = (f.motor_out[0] > 0.98f && f.motor_out[1] < 0.05f) ||
                                       (f.motor_out[1] > 0.98f && f.motor_out[0] < 0.05f);

                if (saturated && is_angle_diverging(f.roll_des_deg, f.roll_act_deg, 20.0f)) {
                    if (++motor_sat_count > 15) {
                        return {
                            FaultType::MotorEscLoss,
                            f.timestamp_us,
                            0.98f,
                            "Відмова мотора або ESC: насичення виходу 100%/0% при зростаючій помилці крену"
                        };
                    }
                } else if (motor_sat_count > 0) {
                    --motor_sat_count;
                }
            }

            // 4. Магнітні завади EKF
            if (f.ekf_mag_innov > 0.45f && f.bat_current_a > 30.0f) {
                if (is_angle_diverging(f.yaw_des_deg, f.yaw_act_deg, 15.0f)) {
                    if (++mag_fault_count > 20) {
                        return {
                            FaultType::MagneticInterference,
                            f.timestamp_us,
                            0.92f,
                            "Розходження курсу через магнітні наведення силового струму на компас"
                        };
                    }
                }
            } else if (mag_fault_count > 0) {
                --mag_fault_count;
            }
        }

        return {FaultType::None, 0, 0.0f, "Інцидентів не виявлено: параметри в межах норми"};
    }

private:
    static bool is_angle_diverging(float des, float act, float threshold_deg) noexcept {
        float err = std::abs(des - act);
        if (err > 180.0f) err = 360.0f - err;
        return err > threshold_deg;
    }
};

} // namespace postmortem
