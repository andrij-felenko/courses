#include <cstdint>
#include <array>
#include <functional>

enum class SecState : uint8_t {
    Idle,
    Armed,
    Triggered,
    Count
};

enum class SecSignal : uint8_t {
    SensorPir,
    CodeEntered,
    Timeout,
    Count
};

class SecurityFsm {
public:
    using ActionFn = void (*)(SecurityFsm&);

    struct Transition {
        SecState next{SecState::Idle};
        ActionFn action{nullptr};
        bool valid{false};
    };

    static void soundAlarm(SecurityFsm& fsm) noexcept { fsm.siren_active_ = true; }
    static void silenceAlarm(SecurityFsm& fsm) noexcept { fsm.siren_active_ = false; }

    void dispatch(SecSignal sig) noexcept {
        const auto& tr = table_[static_cast<size_t>(state_)][static_cast<size_t>(sig)];
        if (tr.valid) {
            if (tr.action) {
                tr.action(*this);
            }
            state_ = tr.next;
        }
    }

    [[nodiscard]] SecState state() const noexcept { return state_; }

private:
    SecState state_{SecState::Idle};
    bool siren_active_{false};

    static constexpr auto createTable() {
        std::array<std::array<Transition, static_cast<size_t>(SecSignal::Count)>, static_cast<size_t>(SecState::Count)> t{};
        
        t[static_cast<size_t>(SecState::Idle)][static_cast<size_t>(SecSignal::CodeEntered)] = 
            Transition{SecState::Armed, nullptr, true};
            
        t[static_cast<size_t>(SecState::Armed)][static_cast<size_t>(SecSignal::SensorPir)] = 
            Transition{SecState::Triggered, &SecurityFsm::soundAlarm, true};
        t[static_cast<size_t>(SecState::Armed)][static_cast<size_t>(SecSignal::CodeEntered)] = 
            Transition{SecState::Idle, nullptr, true};
            
        t[static_cast<size_t>(SecState::Triggered)][static_cast<size_t>(SecSignal::CodeEntered)] = 
            Transition{SecState::Idle, &SecurityFsm::silenceAlarm, true};
        t[static_cast<size_t>(SecState::Triggered)][static_cast<size_t>(SecSignal::Timeout)] = 
            Transition{SecState::Armed, &SecurityFsm::silenceAlarm, true};
            
        return t;
    }

    static constexpr auto table_ = createTable();
};
