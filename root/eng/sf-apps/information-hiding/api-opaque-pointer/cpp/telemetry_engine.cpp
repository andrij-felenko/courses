/* telemetry_engine.cpp — прихована реалізація PIMPL */
#include "telemetry_engine.hpp"
#include <vector>
#include <numeric>
#include <array>

struct ChannelData {
    static constexpr size_t kCapacity = 64;
    std::array<float, kCapacity> ring{};
    size_t head{0};
    size_t count{0};
    double sum{0.0};

    void push(float val) noexcept {
        if (count == kCapacity) {
            sum -= ring[head];
        } else {
            ++count;
        }
        ring[head] = val;
        sum += val;
        head = (head + 1) % kCapacity;
    }

    [[nodiscard]] float mean() const noexcept {
        return count == 0 ? 0.0f : static_cast<float>(sum / count);
    }

    void reset() noexcept {
        ring.fill(0.0f);
        head = count = 0;
        sum = 0.0;
    }
};

struct TelemetryEngine::Impl {
    uint32_t rate_hz;
    std::vector<ChannelData> channels;

    explicit Impl(const TelemetryConfig &cfg)
        : rate_hz(cfg.sample_rate_hz), channels(cfg.max_channels) {}
};

TelemetryEngine::TelemetryEngine(const TelemetryConfig &config)
    : pimpl_(std::make_unique<Impl>(config)) {}

TelemetryEngine::~TelemetryEngine() = default;
TelemetryEngine::TelemetryEngine(TelemetryEngine &&) noexcept = default;
TelemetryEngine &TelemetryEngine::operator=(TelemetryEngine &&) noexcept = default;

std::expected<void, TelemetryError> 
TelemetryEngine::push_sample(uint16_t channel_id, float value) noexcept {
    if (!pimpl_ || channel_id >= pimpl_->channels.size()) {
        return std::unexpected(TelemetryError::InvalidArg);
    }
    pimpl_->channels[channel_id].push(value);
    return {};
}

std::expected<float, TelemetryError> 
TelemetryEngine::get_channel_mean(uint16_t channel_id) const noexcept {
    if (!pimpl_ || channel_id >= pimpl_->channels.size()) {
        return std::unexpected(TelemetryError::InvalidArg);
    }
    return pimpl_->channels[channel_id].mean();
}

void TelemetryEngine::reset() noexcept {
    if (!pimpl_) return;
    for (auto &ch : pimpl_->channels) {
        ch.reset();
    }
}
