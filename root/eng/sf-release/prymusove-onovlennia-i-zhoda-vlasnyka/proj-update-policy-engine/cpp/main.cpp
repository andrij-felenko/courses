#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <expected>
#include <memory>
#include <thread>
#include <cstdint>
#include <filesystem>
#include <system_error>

namespace fleet::ota {

enum class UrgencyLevel : uint8_t {
    Standard = 0,
    Important = 1,
    Mandatory = 2,
    CriticalZeroDay = 3,
    EmergencyRecall = 4
};

enum class EngineState : uint8_t {
    Idle,
    Loaded,
    Deferred,
    Warning,
    ForcePending,
    SafetyHold,
    ReadyToActivate
};

struct InterlockFlags {
    static constexpr uint32_t SpeedZero     = 1U << 0;
    static constexpr uint32_t BrakeEngaged  = 1U << 1;
    static constexpr uint32_t BatteryOk     = 1U << 2;
    static constexpr uint32_t ActuatorsOff  = 1U << 3;
    static constexpr uint32_t FsDrained     = 1U << 4;
    static constexpr uint32_t AllDefault    = SpeedZero | BrakeEngaged | BatteryOk | ActuatorsOff | FsDrained;
};

struct PolicyManifest {
    std::string bundle_id;
    UrgencyLevel urgency{UrgencyLevel::Standard};
    std::chrono::system_clock::time_point issued_at;
    std::chrono::system_clock::time_point hard_deadline;
    uint32_t max_deferrals{3};
    std::chrono::seconds deferral_step{7200};
    uint32_t required_interlocks{InterlockFlags::AllDefault};
    std::chrono::seconds stability_hold{5};
    std::chrono::seconds safety_wait_timeout{3600};
};

struct PersistentState {
    uint32_t deferrals_used{0};
    std::chrono::system_clock::time_point next_prompt;
    std::chrono::system_clock::time_point hard_deadline;
    bool force_active{false};
};

struct VehicleTelemetry {
    double velocity_mps{0.0};
    bool parking_brake{false};
    uint8_t battery_soc_percent{0};
    bool is_ac_connected{false};
    double actuator_current_amps{0.0};
    bool filesystem_drained{false};

    [[nodiscard]] constexpr uint32_t evaluate_mask() const noexcept {
        uint32_t mask = 0;
        if (velocity_mps >= -0.01 && velocity_mps <= 0.01) {
            mask |= InterlockFlags::SpeedZero;
        }
        if (parking_brake) {
            mask |= InterlockFlags::BrakeEngaged;
        }
        if (battery_soc_percent >= 50 || is_ac_connected) {
            mask |= InterlockFlags::BatteryOk;
        }
        if (actuator_current_amps >= -0.05 && actuator_current_amps <= 0.05) {
            mask |= InterlockFlags::ActuatorsOff;
        }
        if (filesystem_drained) {
            mask |= InterlockFlags::FsDrained;
        }
        return mask;
    }
};

class StateStore {
public:
    explicit StateStore(std::filesystem::path path) : path_(std::move(path)) {}

    [[nodiscard]] bool save(const PersistentState& state) const noexcept {
        const auto tmp_path = path_.string() + ".tmp";
        {
            std::ofstream out(tmp_path, std::ios::binary | std::ios::trunc);
            if (!out.is_open()) return false;

            const auto next_p_count = state.next_prompt.time_since_epoch().count();
            const auto hard_d_count = state.hard_deadline.time_since_epoch().count();

            out.write(reinterpret_cast<const char*>(&state.deferrals_used), sizeof(state.deferrals_used));
            out.write(reinterpret_cast<const char*>(&next_p_count), sizeof(next_p_count));
            out.write(reinterpret_cast<const char*>(&hard_d_count), sizeof(hard_d_count));
            out.write(reinterpret_cast<const char*>(&state.force_active), sizeof(state.force_active));
            out.flush();
            if (!out.good()) return false;
        }

        std::error_code ec;
        std::filesystem::rename(tmp_path, path_, ec);
        return !ec;
    }

    [[nodiscard]] std::optional<PersistentState> load() const noexcept {
        std::ifstream in(path_, std::ios::binary);
        if (!in.is_open()) return std::nullopt;

        PersistentState state;
        decltype(std::chrono::system_clock::time_point{}.time_since_epoch().count()) next_p_count{0}, hard_d_count{0};

        in.read(reinterpret_cast<char*>(&state.deferrals_used), sizeof(state.deferrals_used));
        in.read(reinterpret_cast<char*>(&next_p_count), sizeof(next_p_count));
        in.read(reinterpret_cast<char*>(&hard_d_count), sizeof(hard_d_count));
        in.read(reinterpret_cast<char*>(&state.force_active), sizeof(state.force_active));

        if (!in.good()) return std::nullopt;

        state.next_prompt = std::chrono::system_clock::time_point{std::chrono::system_clock::duration{next_p_count}};
        state.hard_deadline = std::chrono::system_clock::time_point{std::chrono::system_clock::duration{hard_d_count}};
        return state;
    }

private:
    std::filesystem::path path_;
};

class PolicyEngine {
public:
    explicit PolicyEngine(std::filesystem::path state_path)
        : store_(std::move(state_path)), state_(EngineState::Idle) {}

    bool load_manifest(PolicyManifest manifest) {
        manifest_ = std::move(manifest);
        auto loaded = store_.load();
        if (loaded.has_value()) {
            persist_ = *loaded;
        } else {
            persist_.deferrals_used = 0;
            persist_.next_prompt = std::chrono::system_clock::now();
            persist_.hard_deadline = manifest_.hard_deadline;
            persist_.force_active = false;
            store_.save(persist_);
        }
        state_ = EngineState::Loaded;
        safe_start_time_.reset();
        return true;
    }

    [[nodiscard]] bool request_deferral(std::optional<std::chrono::seconds> custom_step = std::nullopt) {
        if (state_ == EngineState::Idle) return false;

        const auto now = std::chrono::system_clock::now();
        if (now >= manifest_.hard_deadline || 
            persist_.deferrals_used >= manifest_.max_deferrals ||
            manifest_.urgency == UrgencyLevel::EmergencyRecall) {
            return false;
        }

        const auto step = custom_step.value_or(manifest_.deferral_step);
        auto target = now + step;
        if (target > manifest_.hard_deadline) {
            target = manifest_.hard_deadline;
        }

        persist_.deferrals_used++;
        persist_.next_prompt = target;
        store_.save(persist_);

        state_ = EngineState::Deferred;
        return true;
    }

    [[nodiscard]] EngineState tick(
        const VehicleTelemetry& telemetry,
        std::chrono::system_clock::time_point sys_now,
        std::chrono::steady_clock::time_point steady_now) noexcept
    {
        if (state_ == EngineState::Idle) return EngineState::Idle;

        const bool deadline_reached = (sys_now >= manifest_.hard_deadline);
        const bool deferrals_out = (persist_.deferrals_used >= manifest_.max_deferrals);
        const bool is_emergency = (manifest_.urgency == UrgencyLevel::EmergencyRecall);

        if (deadline_reached || deferrals_out || is_emergency) {
            persist_.force_active = true;
        }

        const auto total_window = manifest_.hard_deadline - manifest_.issued_at;
        const auto elapsed = sys_now - manifest_.issued_at;
        const double progress = (total_window.count() > 0)
            ? (static_cast<double>(elapsed.count()) / static_cast<double>(total_window.count()))
            : 1.0;

        if (persist_.force_active) {
            state_ = EngineState::ForcePending;
        } else if (progress >= 0.80 || (manifest_.max_deferrals - persist_.deferrals_used <= 1)) {
            state_ = EngineState::Warning;
        } else if (sys_now < persist_.next_prompt) {
            state_ = EngineState::Deferred;
            return state_;
        } else {
            state_ = EngineState::Loaded;
        }

        const uint32_t current_mask = telemetry.evaluate_mask();
        const bool interlocks_passed = ((current_mask & manifest_.required_interlocks) == manifest_.required_interlocks);

        if (!interlocks_passed) {
            safe_start_time_.reset();
            if (persist_.force_active) {
                state_ = EngineState::SafetyHold;
            }
            return state_;
        }

        if (!safe_start_time_.has_value()) {
            safe_start_time_ = steady_now;
            if (persist_.force_active) {
                state_ = EngineState::SafetyHold;
            }
            return state_;
        }

        const auto hold_elapsed = std::chrono::duration_cast<std::chrono::seconds>(steady_now - *safe_start_time_);
        if (hold_elapsed >= manifest_.stability_hold) {
            if (persist_.force_active || state_ == EngineState::Loaded || state_ == EngineState::Warning) {
                state_ = EngineState::ReadyToActivate;
            }
        } else {
            if (persist_.force_active) {
                state_ = EngineState::SafetyHold;
            }
        }

        return state_;
    }

    [[nodiscard]] EngineState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t deferrals_used() const noexcept { return persist_.deferrals_used; }

private:
    StateStore store_;
    PolicyManifest manifest_;
    PersistentState persist_;
    EngineState state_;
    std::optional<std::chrono::steady_clock::time_point> safe_start_time_;
};

} // namespace fleet::ota

int main() {
    std::cout << "[C++20 Engine Test Harness] Initializing Policy Engine...\n";
    const std::filesystem::path state_path = "/tmp/ota_cpp_test_policy.dat";
    std::filesystem::remove(state_path);

    fleet::ota::PolicyEngine engine(state_path);

    const auto now = std::chrono::system_clock::now();
    fleet::ota::PolicyManifest manifest{
        .bundle_id = "com.fleet.firmware-amr-5.12.4",
        .urgency = fleet::ota::UrgencyLevel::CriticalZeroDay,
        .issued_at = now,
        .hard_deadline = now + std::chrono::seconds(10),
        .max_deferrals = 2,
        .deferral_step = std::chrono::seconds(4),
        .required_interlocks = fleet::ota::InterlockFlags::AllDefault,
        .stability_hold = std::chrono::seconds(2),
        .safety_wait_timeout = std::chrono::seconds(60)
    };

    engine.load_manifest(manifest);

    fleet::ota::VehicleTelemetry moving_telem{
        .velocity_mps = 2.1,
        .parking_brake = false,
        .battery_soc_percent = 85,
        .is_ac_connected = false,
        .actuator_current_amps = 14.5,
        .filesystem_drained = false
    };

    std::cout << "Step 1: Moving AMR -> Request Deferral 1...\n";
    engine.tick(moving_telem, std::chrono::system_clock::now(), std::chrono::steady_clock::now());
    bool d1 = engine.request_deferral(std::chrono::seconds(4));
    std::cout << "Deferral 1: " << (d1 ? "GRANTED" : "REJECTED") << ", count = " << engine.deferrals_used() << "\n";

    std::cout << "Step 2: Request Deferral 2...\n";
    bool d2 = engine.request_deferral(std::chrono::seconds(4));
    std::cout << "Deferral 2: " << (d2 ? "GRANTED" : "REJECTED") << ", count = " << engine.deferrals_used() << "\n";

    std::cout << "Step 3: Request Deferral 3 (exceeding limit)...\n";
    bool d3 = engine.request_deferral(std::chrono::seconds(4));
    std::cout << "Deferral 3: " << (d3 ? "GRANTED" : "REJECTED") << " (expected REJECTED)\n";

    std::cout << "Step 4: Park vehicle and hold interlocks for 2 seconds...\n";
    fleet::ota::VehicleTelemetry parked_telem{
        .velocity_mps = 0.0,
        .parking_brake = true,
        .battery_soc_percent = 84,
        .is_ac_connected = false,
        .actuator_current_amps = 0.0,
        .filesystem_drained = true
    };

    for (int i = 0; i < 3; ++i) {
        auto st = engine.tick(parked_telem, std::chrono::system_clock::now(), std::chrono::steady_clock::now());
        std::cout << "Tick " << (i + 1) << ": State = " << static_cast<int>(st) << "\n";
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    if (engine.state() == fleet::ota::EngineState::ReadyToActivate) {
        std::cout << "[SUCCESS] C++20 Policy Engine granted Safe Execution Window!\n";
    }

    std::filesystem::remove(state_path);
    return 0;
}
