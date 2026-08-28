#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

enum class FlightFault {
    None,
    MotorDesync,
    SensorClipping,
    ToiletBowl,
    MixerSaturation
};

struct FlightSample {
    double time_s{};
    double gyro_roll{};
    double setpoint_roll{};
    double acc_z{};
    double motor_cmd[4]{};    // 0.0 .. 1.0
    double motor_erpm[4]{};   // оберти за хвилину
    double roll_deg{};
    double pitch_deg{};
    int32_t clip_count{};
};

class FlightLogAnalyzer {
public:
    static constexpr size_t kMinWindow = 64;
    static constexpr double kGravAcc = 9.80665;

    [[nodiscard]] static FlightFault diagnose(std::span<const FlightSample> window) noexcept {
        if (window.size() < kMinWindow) {
            return FlightFault::None;
        }

        size_t desync_count = 0;
        size_t clip_count = 0;
        size_t saturation_count = 0;

        for (const auto& sample : window) {
            // Кліпінг акселерометра: лічильник відкинутих вибірок або наближення до +-16g
            if (sample.clip_count > 0 || std::abs(sample.acc_z) > 15.8 * kGravAcc) {
                ++clip_count;
            }

            // Десинхронізація: 100% запит газу при зупинці ротора (eRPM ~ 0) і зриві кута
            for (size_t m = 0; m < 4; ++m) {
                if (sample.motor_cmd[m] > 0.98 && sample.motor_erpm[m] < 100.0) {
                    const double err = std::abs(sample.gyro_roll - sample.setpoint_roll);
                    if (err > 300.0) {
                        ++desync_count;
                    }
                }
            }

            // Насичення мікшера: два або більше моторів одночасно на 100%
            size_t maxed_motors = 0;
            for (double cmd : sample.motor_cmd) {
                if (cmd > 0.98) ++maxed_motors;
            }
            if (maxed_motors >= 2) {
                ++saturation_count;
            }
        }

        if (desync_count >= 3) return FlightFault::MotorDesync;
        if (clip_count >= 5)   return FlightFault::SensorClipping;

        // Пошук розбіжної спіралі «унітазу» через кореляцію крену й тангажу з фазовим зсувом pi/2
        double sum_r2 = 0.0;
        double sum_p2 = 0.0;
        for (const auto& s : window) {
            sum_r2 += s.roll_deg * s.roll_deg;
            sum_p2 += s.pitch_deg * s.pitch_deg;
        }
        const double rms_r = std::sqrt(sum_r2 / static_cast<double>(window.size()));
        const double rms_p = std::sqrt(sum_p2 / static_cast<double>(window.size()));

        if (rms_r > 10.0 && rms_p > 10.0) {
            const size_t shift = window.size() / 4; // зсув фази на чверть періоду (90°)
            size_t matched_phases = 0;
            for (size_t i = 0; i < window.size() - shift; ++i) {
                if ((window[i].roll_deg * window[i + shift].pitch_deg) > 0.0) {
                    ++matched_phases;
                }
            }
            if (matched_phases > (window.size() - shift) * 3 / 4) {
                return FlightFault::ToiletBowl;
            }
        }

        if (saturation_count > window.size() / 2) {
            return FlightFault::MixerSaturation;
        }

        return FlightFault::None;
    }

    [[nodiscard]] static constexpr std::string_view name(FlightFault fault) noexcept {
        switch (fault) {
            case FlightFault::None:            return "Норма (без відмов)";
            case FlightFault::MotorDesync:      return "Десинхронізація мотора (ESC Desync)";
            case FlightFault::SensorClipping:   return "Кліпінг сенсора (VRE завал горизонту)";
            case FlightFault::ToiletBowl:       return "Патерн «Унітаз» (Розсинхрон компаса)";
            case FlightFault::MixerSaturation:  return "Насичення мікшера (Втрата авторитету)";
        }
        return "Невідома відмова";
    }
};
