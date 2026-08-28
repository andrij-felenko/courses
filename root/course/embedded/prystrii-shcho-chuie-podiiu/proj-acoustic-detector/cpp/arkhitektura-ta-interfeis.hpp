#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace acoustic {

inline constexpr std::size_t SampleRate     = 16000;
inline constexpr std::size_t FrameSamples   = 256;
inline constexpr std::size_t FftSize        = 512;
inline constexpr std::size_t MelBins        = 32;
inline constexpr std::size_t NumFrames      = 40;
inline constexpr std::size_t NumClasses     = 4;

enum class EventClass : std::uint8_t {
    Background = 0,
    GlassBreak = 1,
    Gunshot    = 2,
    AlarmSiren = 3
};

struct DetectionResult {
    EventClass event{EventClass::Background};
    float confidence{0.0f};
};

class EventDetector {
public:
    EventDetector() noexcept;

    void reset() noexcept;
    void processHalfBuffer(std::span<const std::int16_t> audio_frame) noexcept;
    [[nodiscard]] std::optional<DetectionResult> pollEvent() noexcept;

private:
    std::uint32_t energy_threshold_{120000};
    std::uint32_t background_noise_{40000};
    std::size_t   frames_recorded_{0};
    bool          event_in_progress_{false};
    std::int16_t  pre_emphasis_prev_{0};

    std::array<std::array<std::int8_t, MelBins>, NumFrames> feature_matrix_{};

    [[nodiscard]] std::uint32_t computeEnergy(std::span<const std::int16_t> frame) const noexcept;
    void extractMelFeatures(std::span<const std::int16_t> frame, std::span<std::int8_t, MelBins> out_mel) noexcept;
    [[nodiscard]] DetectionResult runInference() const noexcept;
};

} // namespace acoustic
