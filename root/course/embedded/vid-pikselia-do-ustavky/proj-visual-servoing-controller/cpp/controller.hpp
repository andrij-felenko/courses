#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <expected>

#include "pid.hpp"
#include "tracker.hpp"

namespace servo {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

struct CameraIntrinsics {
    float fx{800.0f};
    float fy{800.0f};
    float cx{320.0f};
    float cy{240.0f};
    float img_width{640.0f};
    float img_height{480.0f};
};

/* Детекція з апаратною міткою початку експозиції. Без мітки затримку в
 * 110 мс компенсувати нічим, тому поля з типовим значенням тут немає. */
struct TargetDetection {
    float u{};
    float v{};
    float width{};
    float height{};
    TimePoint captured{};

    [[nodiscard]] float scale() const noexcept { return std::sqrt(width * height); }
};

struct BodyRates {
    float yaw{0.0f};
    float pitch{0.0f};
};

struct GuidanceSetpoints {
    float yaw_rate_rad_s{0.0f};
    float pitch_rate_rad_s{0.0f};
    float forward_vel_m_s{0.0f};
};

/* Чому уставок немає — це не «нуль», а різні стани системи, і викликач
 * мусить їх розрізняти: перший означає «ще шукаємо», другий — «щойно
 * втратили ціль, час переходити в зависання». */
enum class TrackingLoss {
    no_target,
    stale_frame,
};

class VisualServoingController {
public:
    explicit VisualServoingController(CameraIntrinsics camera) noexcept;

    /* Асинхронний вхід: кадр від детектора (20–30 Гц). */
    void on_detection(const TargetDetection& det);

    /* Синхронний вхід: крок контуру керування (100–250 Гц). */
    std::expected<GuidanceSetpoints, TrackingLoss> update(TimePoint now, BodyRates gyro);

    void set_desired_scale(float px) noexcept { desired_scale_px_ = px; }
    [[nodiscard]] bool tracking() const noexcept { return tracking_; }
    [[nodiscard]] unsigned frames_used() const noexcept { return frames_used_; }
    [[nodiscard]] unsigned frames_rejected() const noexcept { return frames_rejected_; }

private:
    /* Історія ракурсу апарата: кадр приходить із запізненням, а гіроскоп
     * інтегрується безперервно — ракурс на момент експозиції доводиться
     * діставати з минулого. 128 записів на 100 Гц це 1.28 с. */
    struct EgoSample {
        TimePoint t{};
        float yaw{0.0f};
        float pitch{0.0f};
    };

    void push_ego(TimePoint t) noexcept;
    [[nodiscard]] BodyRates ego_at(TimePoint t) const noexcept;

    CameraIntrinsics camera_;
    BearingTracker yaw_tracker_{};
    BearingTracker pitch_tracker_{};
    ServoingPid pid_yaw_;
    ServoingPid pid_pitch_;
    ServoingPid pid_forward_;

    std::array<EgoSample, 128> ego_{};
    std::size_t ego_head_{0};
    std::size_t ego_count_{0};

    float desired_scale_px_{80.0f};
    float scale_px_{0.0f};
    TimePoint last_frame_{};
    TimePoint last_tick_{};
    bool tracking_{false};
    unsigned frames_used_{0};
    unsigned frames_rejected_{0};
};

}  // namespace servo
