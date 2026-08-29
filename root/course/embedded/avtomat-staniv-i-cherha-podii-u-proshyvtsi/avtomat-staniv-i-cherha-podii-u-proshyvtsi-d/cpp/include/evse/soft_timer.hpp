#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <utility>

#include "evse/board.hpp"
#include "evse/units.hpp"

namespace evse {

/*
 * Програмні одноразові таймери — заміна delay(). Автомат не спалює такти в
 * лічильному циклі, а зводить таймер; коли термін спливає, служба повідомляє
 * про це через переданий приймач, а той кладе подію в чергу.
 *
 * Служба навмисно не знає ні про чергу, ні про події: тік викликається з
 * переривання, і що менше він тягне за собою, то коротший обробник.
 */
template <class Id, std::size_t Count, class Lock = NoLock>
class TimerService {
public:
    void arm(Id id, Millis delay, Millis now) noexcept
    {
        /*
         * Термін і сам факт зведення мусять стати видимими для тіку одним
         * шматком: якби переривання вклинилося між ними, воно побачило б
         * зведений таймер зі старим терміном і вистрілило б негайно.
         */
        [[maybe_unused]] const Lock guard{};
        deadlines_[index(id)] = now + delay;
    }

    void disarm(Id id) noexcept
    {
        [[maybe_unused]] const Lock guard{};
        deadlines_[index(id)].reset();
    }

    [[nodiscard]] bool isArmed(Id id) const noexcept
    {
        return deadlines_[index(id)].has_value();
    }

    /*
     * Викликається з обробника системного таймера. Приймач дістає номер
     * таймера, чий термін настав.
     */
    template <class Sink>
    void tick(Millis now, Sink&& expired)
    {
        for (std::size_t i = 0; i < Count; ++i) {
            auto& deadline = deadlines_[i];
            if (!deadline) {
                continue;
            }

            /*
             * Порівнюється різниця, а не самі моменти: std::chrono тут теж
             * рахує в 64-бітних мілісекундах, але на 32-бітному лічильнику
             * плати саме така форма переживає переповнення.
             */
            if ((now - *deadline).count() >= 0) {
                deadline.reset();
                expired(static_cast<Id>(i));
            }
        }
    }

private:
    [[nodiscard]] static constexpr std::size_t index(Id id) noexcept
    {
        return static_cast<std::size_t>(id);
    }

    std::array<std::optional<Millis>, Count> deadlines_{};
};

} // namespace evse
