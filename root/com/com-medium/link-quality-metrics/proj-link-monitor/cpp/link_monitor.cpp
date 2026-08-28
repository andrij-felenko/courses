// link_monitor.cpp - Об'єктно-орієнтований модуль аналізу якості каналу на C++20
#include <iostream>
#include <array>
#include <numeric>
#include <format>
#include <cstdint>

enum class McsMode : uint8_t {
    Bpsk = 0,
    Qpsk,
    Qam16
};

enum class LinkHealth : uint8_t {
    Critical = 0,
    Fair,
    Excellent
};

template <std::size_t WindowSize = 32>
class LinkQualityMonitor {
public:
    explicit LinkQualityMonitor(float alpha = 0.125f) noexcept
        : alpha_(alpha), rssi_ema_(-100.0f), snr_ema_(0.0f), lqi_ema_(0.0f) {
        per_window_.fill(true);
    }

    void processPacket(float raw_rssi, float raw_snr, float raw_lqi, bool crc_ok) noexcept {
        // 1. Експоненційне згладжування EMA
        rssi_ema_ += alpha_ * (raw_rssi - rssi_ema_);
        snr_ema_  += alpha_ * (raw_snr - snr_ema_);
        lqi_ema_  += alpha_ * (raw_lqi - lqi_ema_);

        // 2. Оновлення ковзного вікна результатів CRC
        per_window_[window_index_] = crc_ok;
        window_index_ = (window_index_ + 1) % WindowSize;
        if (total_processed_ < WindowSize) {
            total_processed_++;
        }

        // 3. Обчислення поточного PER та передача у стан адаптації
        updateMcsState();
    }

    [[nodiscard]] float rssi() const noexcept { return rssi_ema_; }
    [[nodiscard]] float snr() const noexcept { return snr_ema_; }
    [[nodiscard]] float lqi() const noexcept { return lqi_ema_; }
    
    [[nodiscard]] float packetErrorRate() const noexcept {
        if (total_processed_ == 0) return 0.0f;
        std::size_t valid_count = 0;
        for (std::size_t i = 0; i < total_processed_; ++i) {
            if (per_window_[i]) valid_count++;
        }
        std::size_t errors = total_processed_ - valid_count;
        return (static_cast<float>(errors) / static_cast<float>(total_processed_)) * 100.0f;
    }

    [[nodiscard]] McsMode currentMcs() const noexcept { return current_mcs_; }
    
    [[nodiscard]] LinkHealth healthStatus() const noexcept {
        float per = packetErrorRate();
        if (per > 20.0f || snr_ema_ < 3.0f) {
            return LinkHealth::Critical;
        }
        if (per < 3.0f && snr_ema_ >= 12.0f && lqi_ema_ >= 180.0f) {
            return LinkHealth::Excellent;
        }
        return LinkHealth::Fair;
    }

private:
    void updateMcsState() noexcept {
        float per = packetErrorRate();

        switch (current_mcs_) {
            case McsMode::Bpsk:
                if (snr_ema_ >= 8.0f && lqi_ema_ >= 120.0f && per < 5.0f) {
                    current_mcs_ = McsMode::Qpsk;
                }
                break;

            case McsMode::Qpsk:
                if (per > 15.0f || snr_ema_ < 5.0f) {
                    current_mcs_ = McsMode::Bpsk;
                } else if (snr_ema_ >= 16.0f && lqi_ema_ >= 200.0f && per < 2.0f) {
                    current_mcs_ = McsMode::Qam16;
                }
                break;

            case McsMode::Qam16:
                if (per > 8.0f || snr_ema_ < 12.0f || lqi_ema_ < 150.0f) {
                    current_mcs_ = McsMode::Qpsk;
                }
                break;
        }
    }

    float alpha_;
    float rssi_ema_;
    float snr_ema_;
    float lqi_ema_;

    std::array<bool, WindowSize> per_window_{};
    std::size_t window_index_{0};
    std::size_t total_processed_{0};

    McsMode current_mcs_{McsMode::Bpsk};
};

int main() {
    LinkQualityMonitor<32> monitor(0.2f);

    struct PacketSample {
        float rssi;
        float snr;
        float lqi;
        bool crc;
    };

    const std::array samples = {
        PacketSample{-85.0f,  4.0f,  80.0f, true},
        PacketSample{-83.0f,  6.0f, 100.0f, true},
        PacketSample{-80.0f,  9.0f, 140.0f, true},
        PacketSample{-78.0f, 11.0f, 170.0f, true},
        PacketSample{-75.0f, 14.0f, 210.0f, true},
        PacketSample{-74.0f, 15.0f, 220.0f, true},
        PacketSample{-75.0f, 16.0f, 225.0f, true}
    };

    for (std::size_t idx = 0; const auto& sample : samples) {
        monitor.processPacket(sample.rssi, sample.snr, sample.lqi, sample.crc);
        std::cout << std::format("Крок {}: RSSI={:.1f} dBm, SNR={:.1f} dB, LQI={:.1f}, PER={:.1f}%, MCS={}\n",
                                 idx + 1,
                                 monitor.rssi(),
                                 monitor.snr(),
                                 monitor.lqi(),
                                 monitor.packetErrorRate(),
                                 static_cast<int>(monitor.currentMcs()));
        idx++;
    }

    return 0;
}
