#include "controller.hpp"

#include <algorithm>
#include <cmath>

namespace servo {
namespace {

using namespace std::chrono_literals;

/* Довше за це без кадру — супровід утрачено. */
constexpr Seconds kTrackTimeout{0.5f};

/* Випередження на запізнення внутрішнього контуру: поки уставка пройде
 * мікшер і приводи, ціль устигає зміститися. */
constexpr Seconds kActuatorLead{0.03f};

/* Мітка часу старша за це означає, що годинники детектора й контуру поїхали. */
constexpr Seconds kMaxFrameAge{0.5f};

constexpr float kMinScalePx = 5.0f;

}  // namespace

VisualServoingController::VisualServoingController(CameraIntrinsics camera) noexcept
    : camera_{camera},
      pid_yaw_{{.kp = 1.8f, .ki = 0.1f, .kd = 0.15f,
                .max_output = 1.0f, .max_integral = 0.3f, .deadband = 0.008f}},
      pid_pitch_{{.kp = 1.8f, .ki = 0.1f, .kd = 0.15f,
                  .max_output = 0.8f, .max_integral = 0.2f, .deadband = 0.008f}},
      /* Поздовжній канал працює в пікселях розміру рамки — звідси дрібні
         коефіцієнти й широка зона нечутливості. */
      pid_forward_{{.kp = 0.02f, .ki = 0.001f, .kd = 0.005f,
                    .max_output = 3.0f, .max_integral = 0.5f, .deadband = 2.0f}} {}

void VisualServoingController::push_ego(TimePoint t) noexcept {
    ego_[ego_head_] = EgoSample{t, yaw_tracker_.body_angle(), pitch_tracker_.body_angle()};
    ego_head_ = (ego_head_ + 1) % ego_.size();
    if (ego_count_ < ego_.size()) {
        ++ego_count_;
    }
}

BodyRates VisualServoingController::ego_at(TimePoint t) const noexcept {
    if (ego_count_ == 0) {
        return {};
    }

    const EgoSample* newer = nullptr;
    for (std::size_t i = 1; i <= ego_count_; ++i) {
        const EgoSample& s = ego_[(ego_head_ + ego_.size() - i) % ego_.size()];
        if (s.t <= t) {
            if (newer != nullptr && newer->t > s.t) {
                const float a = Seconds(t - s.t).count() / Seconds(newer->t - s.t).count();
                return {s.yaw + a * (newer->yaw - s.yaw), s.pitch + a * (newer->pitch - s.pitch)};
            }
            return {s.yaw, s.pitch};
        }
        newer = &s;
    }
    /* Кадр старіший за всю історію: беремо найдавніший запис — компенсація
     * буде неповною, але таймаут однаково зніме такий супровід. */
    return {newer->yaw, newer->pitch};
}

void VisualServoingController::on_detection(const TargetDetection& det) {
    const bool sane =
        std::isfinite(det.u) && std::isfinite(det.v) &&
        det.width > 1.0f && det.height > 1.0f &&
        det.u >= 0.0f && det.u <= camera_.img_width &&
        det.v >= 0.0f && det.v <= camera_.img_height &&
        det.captured.time_since_epoch().count() != 0;

    if (!sane) {
        ++frames_rejected_;
        return;
    }

    if (last_tick_.time_since_epoch().count() != 0) {
        if (det.captured > last_tick_ || (last_tick_ - det.captured) > kMaxFrameAge) {
            ++frames_rejected_;      /* кадр із майбутнього або з позаминулого */
            return;
        }
    }
    if (tracking_ && det.captured <= last_frame_) {
        ++frames_rejected_;          /* дубль того самого кадру */
        return;
    }

    /* Рівень нормалізації: піксель → кут. Ділення на фокусну відстань дає
     * тангенс, arctan — сам кут; на краю кадру різниця вже помітна. */
    const float los_yaw = std::atan((det.u - camera_.cx) / camera_.fx);
    const float los_pitch = std::atan((det.v - camera_.cy) / camera_.fy);
    const BodyRates ego = ego_at(det.captured);

    if (!tracking_) {
        /* Захоплення: фільтри сіємо цим кадром, регулятори стартують з нуля —
         * інакше в них лишається інтеграл із минулого супроводу. */
        yaw_tracker_.acquire();
        pitch_tracker_.acquire();
        pid_yaw_.reset();
        pid_pitch_.reset();
        pid_forward_.reset();
        scale_px_ = det.scale();
        tracking_ = true;
    }

    const Seconds latency = (last_tick_ > det.captured) ? Seconds(last_tick_ - det.captured)
                                                        : Seconds{0.0f};
    const bool ok_yaw = yaw_tracker_.update(los_yaw, ego.yaw, latency);
    const bool ok_pitch = pitch_tracker_.update(los_pitch, ego.pitch, latency);

    if (!ok_yaw && !ok_pitch) {
        /* Обидві осі відкинув гейт — це чужий об'єкт, а не наша ціль. */
        ++frames_rejected_;
        return;
    }

    /* Розмір рамки шумить сильніше за центр (краї об'єкта «дихають»),
     * тому в поздовжній канал він іде згладженим. */
    scale_px_ += 0.3f * (det.scale() - scale_px_);
    last_frame_ = det.captured;
    ++frames_used_;
}

std::expected<GuidanceSetpoints, TrackingLoss> VisualServoingController::update(
    TimePoint now, BodyRates gyro) {
    if (last_tick_.time_since_epoch().count() == 0 || now <= last_tick_) {
        last_tick_ = now;            /* перший такт: dt немає */
        push_ego(now);
        return std::unexpected(TrackingLoss::no_target);
    }

    const Seconds dt{std::min(Seconds(now - last_tick_).count(), 0.5f)};
    last_tick_ = now;

    /* 1. Прогноз і інтегрування гіроскопів ідуть завжди: історія ракурсу має
     * бути суцільною ще до першого кадру. */
    yaw_tracker_.predict(dt, gyro.yaw);
    pitch_tracker_.predict(dt, gyro.pitch);
    push_ego(now);

    if (!tracking_) {
        return std::unexpected(TrackingLoss::no_target);
    }

    /* 2. Повна транспортна затримка: від експозиції матриці до цієї миті. */
    if (Seconds(now - last_frame_) > kTrackTimeout) {
        /* Кадри скінчилися: екстраполяція далі розганяла б апарат за
         * вигаданою ціллю. */
        tracking_ = false;
        pid_yaw_.reset();
        pid_pitch_.reset();
        pid_forward_.reset();
        return std::unexpected(TrackingLoss::stale_frame);
    }

    /* 3. Екстраполяція: стан фільтра фаза predict уже привела до «тепер»,
     * тут додається лише випередження на запізнення приводів. */
    const auto yaw = yaw_tracker_.extrapolate(kActuatorLead);
    const auto pitch = pitch_tracker_.extrapolate(kActuatorLead);

    GuidanceSetpoints sp{};
    /* Знак рискання інвертовано: додатна кутова швидкість повертає апарат
     * праворуч, а це ЗМЕНШУЄ кут візування на ціль, що праворуч. */
    sp.yaw_rate_rad_s = -pid_yaw_.update(0.0f, yaw.bearing, dt);
    /* Ціль нижче центра (додатний кут) вимагає опустити ніс, тобто від'ємної
     * швидкості тангажу — вихід регулятора вже такий. */
    sp.pitch_rate_rad_s = pid_pitch_.update(0.0f, pitch.bearing, dt);

    /* 4. Дальність — за видимим розміром цілі. Рамка менша за кілька пікселів
     * означає, що детектор чіпляється за шум. */
    if (scale_px_ > kMinScalePx) {
        sp.forward_vel_m_s = pid_forward_.update(desired_scale_px_, scale_px_, dt);
    }
    return sp;
}

}  // namespace servo
