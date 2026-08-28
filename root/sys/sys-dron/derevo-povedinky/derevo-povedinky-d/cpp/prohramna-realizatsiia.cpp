#include <cstdint>
#include <string_view>
#include <optional>
#include <span>
#include <array>

namespace autopilot::bt {

enum class NodeStatus : uint8_t {
    Success = 0,
    Failure,
    Running
};

struct DroneTelemetry {
    float battery_voltage{15.2f};
    float obstacle_distance{10.0f};
    bool geofence_breached{false};
};

class INode {
public:
    virtual ~INode() = default;
    [[nodiscard]] virtual NodeStatus tick(DroneTelemetry& telemetry) noexcept = 0;
    virtual void halt(DroneTelemetry& telemetry) noexcept = 0;
};

class LowBatteryCondition final : public INode {
public:
    [[nodiscard]] NodeStatus tick(DroneTelemetry& telemetry) noexcept override {
        return (telemetry.battery_voltage < 14.0f) ? NodeStatus::Success : NodeStatus::Failure;
    }

    void halt(DroneTelemetry&) noexcept override {}
};

class EmergencyLandAction final : public INode {
public:
    [[nodiscard]] NodeStatus tick(DroneTelemetry&) noexcept override {
        /* Формування команди аварійного зниження Vz = -0.5 м/с */
        return NodeStatus::Running;
    }

    void halt(DroneTelemetry&) noexcept override {
        /* Очищення прапорців аварійної посадки */
    }
};

class CruiseMissionAction final : public INode {
public:
    [[nodiscard]] NodeStatus tick(DroneTelemetry&) noexcept override {
        /* Проходження сегменту місії за вектором швидкості */
        return NodeStatus::Running;
    }

    void halt(DroneTelemetry&) noexcept override {
        /* Скидання уставки горизонтальної швидкості до зависання */
    }
};

template <size_t MaxChildren>
class ReactiveFallback final : public INode {
public:
    void add_child(INode* child) noexcept {
        if (count_ < MaxChildren && child != nullptr) {
            children_[count_++] = child;
        }
    }

    [[nodiscard]] NodeStatus tick(DroneTelemetry& telemetry) noexcept override {
        for (size_t i = 0; i < count_; ++i) {
            const auto status = children_[i]->tick(telemetry);

            if (status == NodeStatus::Running) {
                if (running_idx_.has_value() && *running_idx_ > i) {
                    children_[*running_idx_]->halt(telemetry);
                }
                running_idx_ = i;
                return NodeStatus::Running;
            }

            if (status == NodeStatus::Success) {
                if (running_idx_.has_value() && *running_idx_ != i) {
                    children_[*running_idx_]->halt(telemetry);
                }
                running_idx_.reset();
                return NodeStatus::Success;
            }
        }

        running_idx_.reset();
        return NodeStatus::Failure;
    }

    void halt(DroneTelemetry& telemetry) noexcept override {
        if (running_idx_.has_value()) {
            children_[*running_idx_]->halt(telemetry);
            running_idx_.reset();
        }
    }

private:
    std::array<INode*, MaxChildren> children_{};
    size_t count_{0};
    std::optional<size_t> running_idx_{std::nullopt};
};

} // namespace autopilot::bt
