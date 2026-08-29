#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <string_view>

#include "evse/units.hpp"

namespace evse::patterns {

/*
 * Патерн 2: декларативна матриця переходів. Граф живе не в коді, а в сталій
 * таблиці; диспетчер — шість рядків, які не змінюються ніколи.
 *
 * У C++ таблиця будується constexpr-функцією та лягає в секцію сталих даних
 * (тобто у Flash, а не в RAM), а «переходу немає» виражається через
 * std::optional — тому неможливо сплутати порожню клітинку з переходом у стан
 * із кодом нуль, на чому ловляться сирі реалізації цього патерну.
 *
 * Приклад — охоронний шлейф із сиреною.
 */

enum class SecState : std::uint8_t { Idle, Armed, EntryDelay, Triggered, Count };
enum class SecSignal : std::uint8_t { Motion, Code, Timeout, Count };

[[nodiscard]] constexpr std::string_view name(SecState s) noexcept
{
    switch (s) {
        case SecState::Idle:       return "IDLE";
        case SecState::Armed:      return "ARMED";
        case SecState::EntryDelay: return "ENTRY_DELAY";
        default:                   return "TRIGGERED";
    }
}

class SecurityFsm {
public:
    static constexpr Millis kEntryDelay{20'000};
    static constexpr Millis kSirenTimeout{180'000};

    using Action = void (*)(SecurityFsm&);

    struct Transition {
        SecState next{SecState::Idle};
        Action   action{nullptr};
    };

    static constexpr std::size_t kStates  = static_cast<std::size_t>(SecState::Count);
    static constexpr std::size_t kSignals = static_cast<std::size_t>(SecSignal::Count);

    using Row   = std::array<std::optional<Transition>, kSignals>;
    using Table = std::array<Row, kStates>;

    void dispatch(SecSignal signal)
    {
        const auto& cell = kTable[index(state_)][index(signal)];
        if (!cell) {
            return; /* стан свідомо ігнорує цей сигнал */
        }
        if (cell->action != nullptr) {
            cell->action(*this);
        }
        state_ = cell->next;
    }

    /* Плин часу: заведений таймер, дійшовши до нуля, породжує Timeout — так
     * само, як у прошивці його дістав би з черги обробник таймера. */
    void tick(Millis elapsed)
    {
        if (remaining_.count() == 0) {
            return;
        }
        if (remaining_ <= elapsed) {
            remaining_ = Millis{0};
            dispatch(SecSignal::Timeout);
        } else {
            remaining_ -= elapsed;
        }
    }

    [[nodiscard]] SecState state() const noexcept { return state_; }
    [[nodiscard]] bool     sirenActive() const noexcept { return siren_; }
    [[nodiscard]] std::uint16_t alarmCount() const noexcept { return alarms_; }

    /*
     * Матриця — звичайні дані, тому граф можна пройти обходом і довести, що з
     * кожного стану існує шлях назад у Idle. Перевірка виконується під час
     * компіляції: глухий кут у графі стає помилкою збірки, а не дзвінком з
     * майданчика.
     */
    [[nodiscard]] static constexpr bool graphIsSane() noexcept
    {
        for (std::size_t start = 0; start < kStates; ++start) {
            std::array<bool, kStates>        seen{};
            std::array<std::size_t, kStates> queue{};
            std::size_t head = 0, tail = 0;
            bool        reachedIdle = false;

            seen[start]   = true;
            queue[tail++] = start;

            while (head < tail) {
                const std::size_t s = queue[head++];
                if (s == index(SecState::Idle)) {
                    reachedIdle = true;
                    break;
                }
                for (std::size_t sig = 0; sig < kSignals; ++sig) {
                    const auto& cell = kTable[s][sig];
                    if (cell && !seen[index(cell->next)]) {
                        seen[index(cell->next)] = true;
                        queue[tail++]           = index(cell->next);
                    }
                }
            }

            if (!reachedIdle) {
                return false; /* стан, з якого нема виходу */
            }
        }
        return true;
    }

private:
    static constexpr std::size_t index(SecState s) noexcept
    {
        return static_cast<std::size_t>(s);
    }
    static constexpr std::size_t index(SecSignal s) noexcept
    {
        return static_cast<std::size_t>(s);
    }

    static constexpr void armSystem(SecurityFsm& fsm) noexcept
    {
        fsm.remaining_ = Millis{0};
    }
    static constexpr void startEntryDelay(SecurityFsm& fsm) noexcept
    {
        fsm.remaining_ = kEntryDelay;
    }
    static constexpr void soundSiren(SecurityFsm& fsm) noexcept
    {
        fsm.siren_     = true;
        fsm.remaining_ = kSirenTimeout;
        ++fsm.alarms_;
    }
    static constexpr void silence(SecurityFsm& fsm) noexcept
    {
        fsm.siren_     = false;
        fsm.remaining_ = Millis{0};
    }

    /* Увесь граф автомата — тут і більше ніде. */
    static constexpr Table buildTable() noexcept
    {
        Table t{};

        t[index(SecState::Idle)][index(SecSignal::Code)] =
            Transition{SecState::Armed, &SecurityFsm::armSystem};

        t[index(SecState::Armed)][index(SecSignal::Motion)] =
            Transition{SecState::EntryDelay, &SecurityFsm::startEntryDelay};
        t[index(SecState::Armed)][index(SecSignal::Code)] =
            Transition{SecState::Idle, &SecurityFsm::silence};

        t[index(SecState::EntryDelay)][index(SecSignal::Code)] =
            Transition{SecState::Idle, &SecurityFsm::silence};
        t[index(SecState::EntryDelay)][index(SecSignal::Timeout)] =
            Transition{SecState::Triggered, &SecurityFsm::soundSiren};

        t[index(SecState::Triggered)][index(SecSignal::Code)] =
            Transition{SecState::Idle, &SecurityFsm::silence};
        /* Сирена не виє вічно: за три хвилини вертаємося під охорону. */
        t[index(SecState::Triggered)][index(SecSignal::Timeout)] =
            Transition{SecState::Armed, &SecurityFsm::silence};

        return t;
    }

    static constexpr Table kTable = buildTable();

    SecState      state_{SecState::Idle};
    bool          siren_{false};
    std::uint16_t alarms_{0};
    Millis        remaining_{0};
};

static_assert(SecurityFsm::graphIsSane(), "у графі автомата є глухий кут");

} // namespace evse::patterns
