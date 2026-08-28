#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

enum class QSignal : uint16_t {
    Entry = 1,
    Exit  = 2,
    Init  = 3,
    User  = 4
};

enum class QResult : uint8_t {
    Handled,
    Ignored,
    Transition,
    Super
};

struct QEvt {
    QSignal sig;
    uintptr_t param{0};
};

class HsmBase {
public:
    using StateHandler = QResult (HsmBase::*)(const QEvt&);
    static constexpr size_t MaxDepth = 8;

    explicit HsmBase(StateHandler initial) : state_(&HsmBase::topState), initial_(initial) {}

    void init() {
        (this->*initial_)(QEvt{QSignal::Init});
        auto target = temp_;

        std::array<StateHandler, MaxDepth> entry_path{};
        int8_t depth = 0;

        auto s = target;
        while (s != &HsmBase::topState && depth < static_cast<int8_t>(MaxDepth)) {
            entry_path[depth++] = s;
            temp_ = &HsmBase::topState;
            (this->*s)(QEvt{QSignal::Entry});
            s = temp_;
        }

        while (--depth >= 0) {
            (this->*entry_path[depth])(QEvt{QSignal::Entry});
        }
        state_ = target;
        (this->*state_)(QEvt{QSignal::Init});
    }

    void dispatch(const QEvt& e) {
        auto s = state_;
        while (s != &HsmBase::topState) {
            temp_ = &HsmBase::topState;
            QResult res = (this->*s)(e);

            if (res == QResult::Handled || res == QResult::Ignored) {
                return;
            }

            if (res == QResult::Transition) {
                auto target = temp_;
                auto source = s;

                for (auto c = state_; c != source; ) {
                    (this->*c)(QEvt{QSignal::Exit});
                    temp_ = &HsmBase::topState;
                    (this->*c)(QEvt{QSignal::Entry});
                    c = temp_;
                }
                (this->*source)(QEvt{QSignal::Exit});

                std::array<StateHandler, MaxDepth> entry_path{};
                int8_t depth = 0;
                auto t = target;

                while (t != &HsmBase::topState && depth < static_cast<int8_t>(MaxDepth)) {
                    entry_path[depth++] = t;
                    temp_ = &HsmBase::topState;
                    (this->*t)(QEvt{QSignal::Entry});
                    t = temp_;
                }

                while (--depth >= 0) {
                    (this->*entry_path[depth])(QEvt{QSignal::Entry});
                }

                state_ = target;
                (this->*state_)(QEvt{QSignal::Init});
                return;
            }

            s = temp_;
        }
    }

protected:
    QResult topState(const QEvt&) { return QResult::Ignored; }
    
    QResult handled() const { return QResult::Handled; }
    QResult ignored() const { return QResult::Ignored; }
    QResult tran(StateHandler target) { temp_ = target; return QResult::Transition; }
    QResult super(StateHandler parent) { temp_ = parent; return QResult::Super; }

    StateHandler state_{&HsmBase::topState};
    StateHandler temp_{&HsmBase::topState};
    StateHandler initial_;
};
