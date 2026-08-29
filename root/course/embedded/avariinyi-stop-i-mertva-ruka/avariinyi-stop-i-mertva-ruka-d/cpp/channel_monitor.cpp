#include "channel_monitor.hpp"

namespace safety {

void ChannelMonitor::Debounced::feed(bool raw, Millis dt)
{
    if (raw != candidate_) {
        candidate_ = raw;
        settled_ = Millis{0};
        return;
    }
    if (stable_ == raw) {
        settled_ = Millis{0};
        return;
    }
    settled_ += dt;
    if (settled_ >= kDebounce) {
        stable_ = raw;
        settled_ = Millis{0};
    }
}

ChannelMonitor::ChannelMonitor(Hal& hal) : hal_{hal}
{
    hal_.setTestOutput(Channel::A, true);
    hal_.setTestOutput(Channel::B, true);
}

// Динамічний імпульсний тест зі зсувом фаз.
// Опорні рівні знімаються до тесту: діагностувати можна лише ЗАМКНЕНИЙ
// канал. На розімкненому вході й так нуль, і без цієї перевірки натиснутий
// грибок читався б як міжканальне замикання.
void ChannelMonitor::runPulseTest()
{
    const bool idleA = hal_.readEstopInput(Channel::A);
    const bool idleB = hal_.readEstopInput(Channel::B);

    const auto pulse = [this](Channel ch) {
        hal_.setTestOutput(ch, false);
        hal_.busyWait(kPulseWidth);
        const std::array<bool, 2> seen{
            hal_.readEstopInput(Channel::A),
            hal_.readEstopInput(Channel::B),
        };
        hal_.setTestOutput(ch, true);
        hal_.busyWait(kPulseGap);   // лінії встигають відновитися
        return seen;
    };

    const auto duringA = pulse(Channel::A);
    const auto duringB = pulse(Channel::B);

    // Замкнений канал, що впав під ЧУЖИЙ імпульс, зрощений із сусіднім.
    // Судимо це першим: зрощення підживлює вхід і виглядає ще й як
    // замикання на живлення.
    if ((idleA && !duringB[index(Channel::A)]) || (idleB && !duringA[index(Channel::B)])) {
        fault_ = LineFault::CrossCircuit;
        return;
    }

    // Замкнений канал, що НЕ впав під власний імпульс, живиться збоку.
    if ((idleA && duringA[index(Channel::A)]) || (idleB && duringB[index(Channel::B)])) {
        fault_ = LineFault::ShortToSupply;
    }
}

std::expected<bool, LineFault> ChannelMonitor::update(Millis dt)
{
    if (fault_) {
        return std::unexpected{*fault_};   // дефект лінії залипає до обслуговування
    }

    pulseTimer_ += dt;
    if (pulseTimer_ >= kPulsePeriod) {
        pulseTimer_ = Millis{0};
        runPulseTest();
        if (fault_) {
            return std::unexpected{*fault_};
        }
    }

    inputs_[index(Channel::A)].feed(hal_.readEstopInput(Channel::A), dt);
    inputs_[index(Channel::B)].feed(hal_.readEstopInput(Channel::B), dt);

    const bool a = inputs_[index(Channel::A)].stable();
    const bool b = inputs_[index(Channel::B)].stable();

    if (a != b) {
        if (!mismatching_) {
            mismatching_ = true;
            mismatchTimer_ = Millis{0};
        } else {
            mismatchTimer_ += dt;
            if (mismatchTimer_ >= kDiscrepancy) {
                fault_ = LineFault::Discordance;
                return std::unexpected{*fault_};
            }
        }
        return false;   // безпека не чекає: розбіжність уже знімає дозвіл
    }

    mismatching_ = false;
    mismatchTimer_ = Millis{0};
    return a && b;
}

}  // namespace safety
