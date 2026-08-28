/* gnss_rf_controller.hpp / .cpp - C++20 версія з типізованими класами та RAII */
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <string>
#include <format>
#include <expected>

constexpr double GPS_L1_FREQ_HZ  = 1575420000.0;
constexpr double SPEED_OF_LIGHT  = 299792458.0;
constexpr double SAMPLE_RATE_SPS = 2600000.0;

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
    [[nodiscard]] Vector3D operator-(const Vector3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }
    [[nodiscard]] double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }
};

struct SatelliteChannel {
    int prn{0};
    Vector3D position;
    Vector3D velocity;
    double doppler_hz{0.0};
    double carrier_phase_rad{0.0};
};

class RfAttenuator {
public:
    enum class Error { CommunicationFailed, OutOfRange };

    explicit RfAttenuator(std::string port_name) : port_{std::move(port_name)} {}

    [[nodiscard]] std::expected<void, Error> set_attenuation_db(double db) noexcept {
        if (db < 0.0 || db > 95.0) {
            return std::unexpected(Error::OutOfRange);
        }
        attenuation_db_ = db;
        std::string scpi_command = std::format(":ATT:VAL {:.2f}\n", db);
        
        /* Надсилання SCPI команди в апаратний порт */
        std::cout << "[SCPI C++ TX] " << scpi_command;
        return {};
    }

    [[nodiscard]] double current_db() const noexcept { return attenuation_db_; }

private:
    std::string port_;
    double attenuation_db_{0.0};
};

class GnssSignalSynthesizer {
public:
    explicit GnssSignalSynthesizer(std::vector<SatelliteChannel> channels)
        : channels_{std::move(channels)} {}

    void update_user_state(const Vector3D& user_pos, const Vector3D& user_vel) noexcept {
        for (auto& sat : channels_) {
            Vector3D los = sat.position - user_pos;
            double range = los.norm();
            if (range < 1.0) continue;

            Vector3D los_unit = {los.x / range, los.y / range, los.z / range};
            Vector3D rel_vel = sat.velocity - user_vel;
            sat.doppler_hz = -GPS_L1_FREQ_HZ * (rel_vel.dot(los_unit) / SPEED_OF_LIGHT);
        }
    }

    void generate_iq_samples(std::span<int16_t> interleaved_iq) noexcept {
        const double dt = 1.0 / SAMPLE_RATE_SPS;
        const size_t sample_count = interleaved_iq.size() / 2;

        for (size_t n = 0; n < sample_count; ++n) {
            double i_acc = 0.0;
            double q_acc = 0.0;

            for (auto& sat : channels_) {
                sat.carrier_phase_rad += 2.0 * std::numbers::pi * sat.doppler_hz * dt;
                if (sat.carrier_phase_rad > 2.0 * std::numbers::pi) {
                    sat.carrier_phase_rad -= 2.0 * std::numbers::pi;
                }
                i_acc += std::cos(sat.carrier_phase_rad);
                q_acc += std::sin(sat.carrier_phase_rad);
            }

            interleaved_iq[2 * n]     = static_cast<int16_t>(i_acc * 1000.0);
            interleaved_iq[2 * n + 1] = static_cast<int16_t>(q_acc * 1000.0);
        }
    }

private:
    std::vector<SatelliteChannel> channels_;
};
