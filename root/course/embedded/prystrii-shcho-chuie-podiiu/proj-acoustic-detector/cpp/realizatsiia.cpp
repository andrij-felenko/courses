#include "acoustic_detector.hpp"
#include <algorithm>
#include <numeric>
#include <cmath>

namespace acoustic {

namespace {

constexpr std::int16_t PreEmphasisAlphaQ15 = 31130; // 0.95 * 32768

constexpr std::array<std::int8_t, MelBins * 9> DsConvWeights = {
    12, -45, 88, 3, -15, 62, -4, 19, -33,
    54, -22, 10, -89, 45, 12, 77, -30, 4,
    -12, 90, -65, 34, 11, -8, -55, 72, 18,
    41, -19, 82, -3, 17, 60, -28, 9, -51
};

constexpr std::array<std::int32_t, NumClasses> DsConvBias = {
    124, -850, 420, -15
};

} // namespace

EventDetector::EventDetector() noexcept {
    reset();
}

void EventDetector::reset() noexcept {
    energy_threshold_ = 120000;
    background_noise_ = 40000;
    frames_recorded_ = 0;
    event_in_progress_ = false;
    pre_emphasis_prev_ = 0;
    for (auto &frame : feature_matrix_) {
        frame.fill(0);
    }
}

std::uint32_t EventDetector::computeEnergy(std::span<const std::int16_t> frame) const noexcept {
    std::uint32_t sum = 0;
    for (const auto sample : frame) {
        const auto val = static_cast<std::int32_t>(sample >> 4);
        sum += static_cast<std::uint32_t>(val * val);
    }
    return frame.empty() ? 0 : (sum / static_cast<std::uint32_t>(frame.size()));
}

void EventDetector::extractMelFeatures(std::span<const std::int16_t> frame,
                                      std::span<std::int8_t, MelBins> out_mel) noexcept {
    std::array<std::int16_t, FrameSamples> windowed{};

    for (std::size_t i = 0; i < frame.size() && i < windowed.size(); ++i) {
        const auto pre = static_cast<std::int32_t>(frame[i]) -
                         ((static_cast<std::int32_t>(pre_emphasis_prev_) * PreEmphasisAlphaQ15) >> 15);
        pre_emphasis_prev_ = frame[i];

        const auto win = std::clamp((pre * 28000) >> 15, -32768, 32767);
        windowed[i] = static_cast<std::int16_t>(win);
    }

    constexpr std::size_t step = FrameSamples / MelBins;
    for (std::size_t bin = 0; bin < MelBins; ++bin) {
        std::int32_t bin_energy = 0;
        const std::size_t start = bin * step;
        const std::size_t end = std::min(start + step, windowed.size());

        for (std::size_t s = start; s < end; ++s) {
            const auto v = static_cast<std::int32_t>(windowed[s] >> 7);
            bin_energy += v * v;
        }

        const auto lz = (bin_energy > 0) ? __builtin_clz(static_cast<unsigned int>(bin_energy)) : 32;
        const auto log_val = (bin_energy > 0) ? (31 - lz) * 8 - 64 : -128;
        out_mel[bin] = static_cast<std::int8_t>(std::clamp(log_val, -128, 127));
    }
}

void EventDetector::processHalfBuffer(std::span<const std::int16_t> audio_frame) noexcept {
    if (audio_frame.size() < FrameSamples) return;

    const auto energy = computeEnergy(audio_frame);

    if (energy < energy_threshold_) {
        background_noise_ = ((background_noise_ * 31) + energy) >> 5;
        energy_threshold_ = background_noise_ * 3 + 20000;

        if (event_in_progress_) {
            frames_recorded_ = 0;
            event_in_progress_ = false;
        }
        return;
    }

    event_in_progress_ = true;

    if (frames_recorded_ < NumFrames) {
        extractMelFeatures(audio_frame, feature_matrix_[frames_recorded_]);
        ++frames_recorded_;
    }
}

DetectionResult EventDetector::runInference() const noexcept {
    std::array<std::int32_t, NumClasses> logits{};

    for (std::size_t c = 0; c < NumClasses; ++c) {
        std::int32_t acc = DsConvBias[c];
        for (std::size_t f = 0; f < NumFrames; f += 2) {
            for (std::size_t b = 0; b < MelBins; b += 2) {
                const auto in_val = static_cast<std::int32_t>(feature_matrix_[f][b]);
                const auto wt_val = static_cast<std::int32_t>(DsConvWeights[(c * 32 + b) % DsConvWeights.size()]);
                acc += in_val * wt_val;
            }
        }
        logits[c] = acc;
    }

    const auto max_it = std::max_element(logits.begin(), logits.end());
    const auto best_idx = static_cast<std::size_t>(std::distance(logits.begin(), max_it));
    const auto conf = (*max_it > 0) ? (static_cast<float>(*max_it) / 10000.0f) : 0.0f;

    return DetectionResult{
        .event = static_cast<EventClass>(best_idx),
        .confidence = std::clamp(conf, 0.0f, 1.0f)
    };
}

std::optional<DetectionResult> EventDetector::pollEvent() noexcept {
    if (frames_recorded_ < NumFrames) {
        return std::nullopt;
    }

    const auto result = runInference();
    frames_recorded_ = 0;
    event_in_progress_ = false;

    if (result.event == EventClass::Background) {
        return std::nullopt;
    }

    return result;
}

} // namespace acoustic
