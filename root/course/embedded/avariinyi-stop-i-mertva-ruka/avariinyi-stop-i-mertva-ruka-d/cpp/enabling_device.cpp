#include "enabling_device.hpp"

namespace safety {

std::expected<Grip, EnableFault> EnablingDevice::update(Millis dt)
{
    if (faulted_) {
        return std::unexpected{EnableFault::ContactDiscordance};
    }

    const EnablingContacts contacts = hal_.readEnablingContacts();
    const bool panicPosition = !contacts.panicClosed;

    // Паніка старша за розбіжність: продавлена кнопка розмикає NO-кола не
    // синхронно, і чекати тут на збіг каналів не можна.
    split_ = !panicPosition && (contacts.circuitA != contacts.circuitB);

    if (split_) {
        splitTimer_ += dt;
        if (splitTimer_ >= kSplitLimit) {
            faulted_ = true;
            indicators_ = {};
            return std::unexpected{EnableFault::ContactDiscordance};
        }
    } else {
        splitTimer_ = Millis{0};

        if (panicPosition) {
            panicLatch_ = true;              // Позиція 3 зводить блокування
            grip_ = Grip::Panic;
        } else if (contacts.circuitA && contacts.circuitB) {
            if (panicLatch_) {
                grip_ = Grip::Panic;         // зворотний хід крізь Позицію 2 не вмикає
            } else if (grip_ != Grip::Dozed) {
                grip_ = Grip::Enabled;
            }
        } else {
            // Лише повне повернення в Позицію 1 знімає обидва блокування —
            // і паніку, і пропущену пильність.
            panicLatch_ = false;
            grip_ = Grip::Released;
        }
    }

    updateVigilance(dt);
    return grip_;
}

// Ескалація: спокій → лампа → зумер → зняття дозволу. Таймер скидає лише
// ФРОНТ кнопки підтвердження або справжня дія оператора: затиснута стяжкою
// кнопка тримає постійний рівень і доказом присутності не є.
void EnablingDevice::updateVigilance(Millis dt)
{
    const bool ack = hal_.readAckButton();
    const bool ackEdge = ack && !ackPrev_;
    ackPrev_ = ack;

    if (grip_ != Grip::Enabled && grip_ != Grip::Dozed) {
        idleTimer_ = Millis{0};
        indicators_ = {};
        return;
    }

    if (grip_ == Grip::Dozed) {
        // Тримаємо, доки кнопку не повернуть у Позицію 1: інакше сонний
        // оператор поновив би рух самим лише підтвердженням.
        indicators_ = {.lamp = true, .buzzer = true};
        return;
    }

    if (ackEdge || hal_.operatorActive()) {
        idleTimer_ = Millis{0};
    } else {
        idleTimer_ += dt;
    }

    indicators_.lamp = idleTimer_ >= kVigilanceCycle;
    indicators_.buzzer = idleTimer_ >= kVigilanceCycle + kVigilanceWarn;
    if (idleTimer_ >= kVigilanceCycle + kVigilanceWarn + kVigilanceAlarm) {
        grip_ = Grip::Dozed;
    }
}

}  // namespace safety
