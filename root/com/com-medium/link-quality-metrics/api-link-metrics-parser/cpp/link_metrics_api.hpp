// link_metrics_api.hpp - C++20 API інтерфейс для моніторингу та телеметрії лінку
#ifndef LINK_METRICS_API_HPP
#define LINK_METRICS_API_HPP

#include <cstdint>
#include <string>
#include <string_view>
#include <span>
#include <optional>

namespace comms::metrics {

enum class LinkHealth : uint8_t {
    Critical = 0,
    Degraded,
    Good,
    Excellent
};

[[nodiscard]] constexpr std::string_view to_string(LinkHealth health) noexcept {
    switch (health) {
        case LinkHealth::Critical:  return "CRITICAL";
        case LinkHealth::Degraded:  return "DEGRADED";
        case LinkHealth::Good:      return "GOOD";
        case LinkHealth::Excellent: return "EXCELLENT";
    }
    return "UNKNOWN";
}

struct RadioLinkMetrics {
    float rssi_dbm{-100.0f};
    float snr_db{0.0f};
    uint8_t lqi{0};
    float per_percent{0.0f};
    LinkHealth health{LinkHealth::Critical};
};

struct PacketFrameSample {
    float rssi_dbm;
    float snr_db;
    uint8_t lqi;
    bool crc_valid;
};

class ILinkMetricsCollector {
public:
    virtual ~ILinkMetricsCollector() = default;

    virtual void recordSample(const PacketFrameSample& sample) noexcept = 0;
    [[nodiscard]] virtual RadioLinkMetrics snapshot() const noexcept = 0;
    [[nodiscard]] virtual std::string formatJsonReport() const = 0;
};

class LinkMetricsCollector final : public ILinkMetricsCollector {
public:
    explicit LinkMetricsCollector(std::size_t history_depth = 64)
        : history_depth_(history_depth) {}

    void recordSample(const PacketFrameSample& sample) noexcept override {
        total_frames_++;
        if (!sample.crc_valid) {
            crc_errors_++;
        }

        // Оновлення ковзних показників
        metrics_.rssi_dbm += 0.1f * (sample.rssi_dbm - metrics_.rssi_dbm);
        metrics_.snr_db  += 0.1f * (sample.snr_db - metrics_.snr_db);
        metrics_.lqi     = static_cast<uint8_t>(metrics_.lqi + 0.1f * (sample.lqi - metrics_.lqi));

        if (total_frames_ > 0) {
            metrics_.per_percent = (static_cast<float>(crc_errors_) / static_cast<float>(total_frames_)) * 100.0f;
        }

        classifyHealth();
    }

    [[nodiscard]] RadioLinkMetrics snapshot() const noexcept override {
        return metrics_;
    }

    [[nodiscard]] std::string formatJsonReport() const override {
        return std::string("{\"rssi\":") + std::to_string(metrics_.rssi_dbm) +
               ",\"snr\":" + std::to_string(metrics_.snr_db) +
               ",\"lqi\":" + std::to_string(metrics_.lqi) +
               ",\"per\":" + std::to_string(metrics_.per_percent) +
               ",\"health\":\"" + std::string(to_string(metrics_.health)) + "\"}";
    }

private:
    void classifyHealth() noexcept {
        if (metrics_.per_percent > 15.0f || metrics_.snr_db < 2.0f) {
            metrics_.health = LinkHealth::Critical;
        } else if (metrics_.per_percent > 5.0f || metrics_.snr_db < 8.0f) {
            metrics_.health = LinkHealth::Degraded;
        } else if (metrics_.snr_db < 15.0f || metrics_.lqi < 180) {
            metrics_.health = LinkHealth::Good;
        } else {
            metrics_.health = LinkHealth::Excellent;
        }
    }

    std::size_t history_depth_;
    std::size_t total_frames_{0};
    std::size_t crc_errors_{0};
    RadioLinkMetrics metrics_{};
};

} // namespace comms::metrics

#endif // LINK_METRICS_API_HPP
