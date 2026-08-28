#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <optional>
#include <expected>

namespace drone::payload {

constexpr size_t MaxPayloadEvents = 16;
constexpr uint8_t MaxDropRetries = 3;
constexpr uint32_t DefaultShutterPulseMs = 50;
constexpr uint32_t DropTimeoutMs = 400;
constexpr uint16_t CurrentStallThresholdMa = 2500;

enum class TriggerMode : uint8_t {
    Disabled = 0,
    Distance,
    Time,
    Manual
};

enum class DropState : uint8_t {
    Idle = 0,
    Armed,
    Triggered,
    Verifying,
    Success,
    Stalled,
    Fault
};

enum class DropError : uint8_t {
    Timeout,
    OvercurrentStall,
    SwitchMismatch
};

struct GeoPoint {
    double lat{0.0};
    double lon{0.0};
    float alt_ned{0.0f};
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct PayloadEventLog {
    uint32_t timestamp_ms{0};
    uint32_t sequence_id{0};
    uint8_t  event_type{0}; // 1: Shutter, 2: Drop Success, 3: Drop Fault, 4: ROI Lock
    GeoPoint position{};
    float pitch_deg{0.0f};
    float yaw_deg{0.0f};
    uint16_t current_ma{0};
};

// Абстрактний апаратний драйвер
class IPayloadHardware {
public:
    virtual ~IPayloadHardware() = default;
    virtual uint32_t getTimeMs() const = 0;
    virtual void setShutterGpio(bool active) = 0;
    virtual void setDropServoPwm(uint16_t pulse_us) = 0;
    virtual void setSolenoid(bool active) = 0;
    virtual bool readLimitSwitch() const = 0;
    virtual uint16_t readDropCurrentMa() const = 0;
    virtual void setGimbalAngles(float pitch_deg, float yaw_deg) = 0;
};

class PayloadManager {
public:
    explicit PayloadManager(IPayloadHardware& hw) : hw_(hw) {}

    void setDistanceTrigger(float distance_m) noexcept {
        trigger_dist_m_ = distance_m;
        cam_mode_ = (distance_m > 0.1f) ? TriggerMode::Distance : TriggerMode::Disabled;
    }

    void setRoiTarget(const GeoPoint& target) noexcept {
        roi_target_ = target;
        roi_active_ = true;
    }

    void clearRoi() noexcept {
        roi_active_ = false;
    }

    std::expected<void, DropError> startDropSequence() noexcept {
        if (drop_state_ == DropState::Idle || drop_state_ == DropState::Armed) {
            drop_state_ = DropState::Triggered;
            drop_start_time_ms_ = hw_.getTimeMs();
            drop_retry_count_ = 0;

            hw_.setDropServoPwm(2000);
            hw_.setSolenoid(true);
            return {};
        }
        return std::unexpected(DropError::SwitchMismatch);
    }

    void update(const Vector3f& pos_ned, const GeoPoint& current_geo, float roll_deg, float pitch_deg, float yaw_deg) noexcept {
        const uint32_t now = hw_.getTimeMs();

        // 1. Обробка тривалості імпульсу затвора
        if (shutter_active_ && now >= shutter_off_time_ms_) {
            hw_.setShutterGpio(false);
            shutter_active_ = false;
        }

        // 2. Розрахунок дистанційного тригера
        if (cam_mode_ == TriggerMode::Distance && trigger_dist_m_ > 0.1f) {
            if (std::abs(roll_deg) < 15.0f && std::abs(pitch_deg) < 20.0f) {
                const float dx = pos_ned.x - last_cam_pos_.x;
                const float dy = pos_ned.y - last_cam_pos_.y;
                const float dz = pos_ned.z - last_cam_pos_.z;
                const float dist = std::sqrt(dx * dx + dy * dy + dz * dz);

                if (dist >= trigger_dist_m_) {
                    last_cam_pos_ = pos_ned;
                    shutter_active_ = true;
                    shutter_off_time_ms_ = now + DefaultShutterPulseMs;
                    photo_count_++;
                    hw_.setShutterGpio(true);
                    logEvent(1, current_geo, gimbal_cmd_pitch_, gimbal_cmd_yaw_, 0);
                }
            }
        }

        // 3. Автомат скидання вантажу
        if (drop_state_ == DropState::Triggered) {
            const uint16_t current_ma = hw_.readDropCurrentMa();
            const bool limit_reached = hw_.readLimitSwitch();

            if (current_ma > CurrentStallThresholdMa) {
                hw_.setSolenoid(false);
                drop_state_ = DropState::Stalled;
                logEvent(3, current_geo, 0.0f, 0.0f, current_ma);
            } else if (limit_reached) {
                hw_.setSolenoid(false);
                drop_state_ = DropState::Success;
                logEvent(2, current_geo, 0.0f, 0.0f, current_ma);
            } else if (now - drop_start_time_ms_ > DropTimeoutMs) {
                if (drop_retry_count_ < MaxDropRetries) {
                    drop_retry_count_++;
                    drop_start_time_ms_ = now;
                    hw_.setDropServoPwm(1000);
                    hw_.setSolenoid(false);
                    hw_.setDropServoPwm(2000);
                    hw_.setSolenoid(true);
                } else {
                    hw_.setSolenoid(false);
                    drop_state_ = DropState::Fault;
                    logEvent(3, current_geo, 0.0f, 0.0f, current_ma);
                }
            }
        }

        // 4. Геометрія наведення підвісу
        if (roi_active_) {
            constexpr double MetersPerLat = 111132.95;
            constexpr double DegToRad = 0.017453292519943295;
            constexpr float RadToDeg = 57.29577951308232f;

            const double d_lat = (roi_target_.lat - current_geo.lat) * MetersPerLat;
            const double d_lon = (roi_target_.lon - current_geo.lon) * (111412.84 * std::cos(current_geo.lat * DegToRad));
            const float d_z = roi_target_.alt_ned - current_geo.alt_ned;

            const float dist_xy = std::sqrt(static_cast<float>(d_lat * d_lat + d_lon * d_lon));
            if (dist_xy > 1.0f) {
                gimbal_cmd_pitch_ = std::atan2(-d_z, dist_xy) * RadToDeg;
                gimbal_cmd_yaw   = std::atan2(static_cast<float>(d_lon), static_cast<float>(d_lat)) * RadToDeg;
                hw_.setGimbalAngles(gimbal_cmd_pitch_, gimbal_cmd_yaw_);
            }
        }
    }

    [[nodiscard]] DropState getDropState() const noexcept { return drop_state_; }
    [[nodiscard]] uint32_t getPhotoCount() const noexcept { return photo_count_; }
    [[nodiscard]] std::span<const PayloadEventLog> getRecentEvents() const noexcept {
        return std::span<const PayloadEventLog>(events_.data(), event_count_);
    }

private:
    void logEvent(uint8_t type, const GeoPoint& pos, float pitch, float yaw, uint16_t current_ma) noexcept {
        PayloadEventLog& e = events_[event_head_];
        e.timestamp_ms = hw_.getTimeMs();
        e.sequence_id = photo_count_;
        e.event_type = type;
        e.position = pos;
        e.pitch_deg = pitch;
        e.yaw_deg = yaw;
        e.current_ma = current_ma;

        event_head_ = (event_head_ + 1) % MaxPayloadEvents;
        if (event_count_ < MaxPayloadEvents) {
            event_count_++;
        }
    }

    IPayloadHardware& hw_;

    TriggerMode cam_mode_{TriggerMode::Disabled};
    float trigger_dist_m_{0.0f};
    Vector3f last_cam_pos_{};
    uint32_t shutter_off_time_ms_{0};
    bool shutter_active_{false};
    uint32_t photo_count_{0};

    DropState drop_state_{DropState::Idle};
    uint32_t drop_start_time_ms_{0};
    uint8_t drop_retry_count_{0};

    bool roi_active_{false};
    GeoPoint roi_target_{};
    float gimbal_cmd_pitch_{0.0f};
    float gimbal_cmd_yaw_{0.0f};

    std::array<PayloadEventLog, MaxPayloadEvents> events_{};
    size_t event_head_{0};
    size_t event_count_{0};
};

} // namespace drone::payload
