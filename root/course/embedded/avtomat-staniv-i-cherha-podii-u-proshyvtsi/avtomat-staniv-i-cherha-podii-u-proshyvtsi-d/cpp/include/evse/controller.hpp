#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <string_view>
#include <utility>
#include <variant>

#include "evse/board.hpp"
#include "evse/cp_line.hpp"
#include "evse/event.hpp"
#include "evse/soft_timer.hpp"
#include "evse/state_machine.hpp"
#include "evse/units.hpp"

namespace evse {

enum class FaultReason : std::uint8_t {
    None,
    EmergencyButton,
    Overcurrent,
    Leakage,
    PilotInvalid,
    QueueOverflow
};

[[nodiscard]] constexpr std::string_view name(FaultReason r) noexcept
{
    switch (r) {
        case FaultReason::EmergencyButton: return "кнопка аварійної зупинки";
        case FaultReason::Overcurrent:     return "перевищення струму";
        case FaultReason::Leakage:         return "струм витоку";
        case FaultReason::PilotInvalid:    return "несправність лінії пілота";
        case FaultReason::QueueOverflow:   return "переповнення черги подій";
        default:                           return "без аварії";
    }
}

/*
 * Контролер зарядної станції. Плата підставляється параметром шаблону, тож
 * виклики апаратури вбудовуються в код автомата, а не йдуть через таблицю
 * віртуальних методів.
 */
template <Board B>
class EvseController {
public:
    using Timers = TimerService<TimerId, static_cast<std::size_t>(TimerId::Count),
                                typename B::IrqLock>;

    static constexpr Millis  kAuthWindow{60'000};
    static constexpr Millis  kContactorSettle{3'000};
    static constexpr Millis  kFaultLockout{5'000};
    static constexpr Amperes kCurrentLimit{32};

    /* Пусковий струм контактора й автомобіля втричі перевищує робочий, тож
     * поки тривають перехідні процеси, поріг вважається піднятим. */
    static constexpr Amperes   kInrushTolerance{90};
    static constexpr Milliamps kLeakageTrip{30};

    /* Список дозволених карток. У серійній станції його місце — у сховищі або
     * у відповіді сервера OCPP; для прикладу досить сталої таблиці. */
    static constexpr std::array<std::uint32_t, 3> kAllowedCards{
        0x04A1B2C3u, 0x04FE1122u, 0x0455AA01u};

    // ------------------------------------------------------------- стани ---

    struct Standby {
        [[nodiscard]] static constexpr std::string_view name() noexcept { return "STANDBY"; }

        void onEnter(EvseController& c)
        {
            /* Інваріант стану: контактор розімкнено, замок відпущено, на
             * пілоті постійні +12 В. */
            c.board().setRelay(false);
            c.board().setLock(false);
            c.board().setPilotDuty(Duty::steadyHigh());
            c.setLeds(true, false, false);
        }

        void on(EvseController& c, const CpChanged& e)
        {
            if (e.level == CpClass::B) {
                c.template transitionTo<Connected>();
            }
        }
    };

    struct Connected {
        /* Дані живуть рівно стільки, скільки триває стан: варіант знищує їх
         * на виході, і жодного «забутого прапорця» від минулої сесії. */
        std::uint32_t card{0};
        bool          authorized{false};

        [[nodiscard]] static constexpr std::string_view name() noexcept { return "CONNECTED"; }

        void onEnter(EvseController& c)
        {
            c.board().setLock(true);
            c.board().setPilotDuty(Duty::fromCurrent(c.currentLimit()));
            c.setLeds(true, false, false);
            c.timers().arm(TimerId::AuthWindow, kAuthWindow, c.board().now());
        }

        void onExit(EvseController& c) { c.timers().disarm(TimerId::AuthWindow); }

        void on(EvseController& c, const RfidTag& e)
        {
            const bool allowed = std::find(kAllowedCards.begin(), kAllowedCards.end(),
                                           e.id) != kAllowedCards.end();
            card       = e.id;
            authorized = allowed;

            if (allowed) {
                c.timers().disarm(TimerId::AuthWindow);
                c.setLeds(true, true, false);
            } else {
                c.setLeds(false, false, true); /* картку відхилено */
            }
        }

        void on(EvseController& c, const CpChanged& e)
        {
            if (e.level == CpClass::C && authorized) {
                c.template transitionTo<Charging>();
            } else if (e.level == CpClass::A) {
                c.template transitionTo<Standby>();
            }
            /* Запит енергії без авторизації лишає автомат на місці: пілот уже
             * показує дозволений струм, автомобіль почекає. */
        }

        void on(EvseController& c, const Expired& e)
        {
            if (e.id == TimerId::AuthWindow) {
                c.template transitionTo<Standby>(); /* картку так і не приклали */
            }
        }
    };

    struct Charging {
        bool settling{true}; /* тривають перехідні процеси після замикання */

        [[nodiscard]] static constexpr std::string_view name() noexcept { return "CHARGING"; }

        void onEnter(EvseController& c)
        {
            c.board().setRelay(true);
            c.setLeds(false, true, false);
            /* Замість delay(3000): станція лишається живою всі три секунди
             * перехідного процесу й реагує на кнопку за десятки мікросекунд. */
            c.timers().arm(TimerId::ContactorSettle, kContactorSettle, c.board().now());
        }

        void onExit(EvseController& c)
        {
            /* Єдине місце в прошивці, де розмикається силовий контактор під
             * навантаженням. Виконується на будь-якому виході зі стану — хоч
             * за штатним завершенням, хоч за аварією, хоч за висмикнутим
             * штекером. Забути його в котромусь із переходів неможливо. */
            c.board().setRelay(false);
            c.timers().disarm(TimerId::ContactorSettle);
        }

        void on(EvseController&, const Expired& e)
        {
            if (e.id == TimerId::ContactorSettle) {
                settling = false; /* пусковий струм ущух, поріг знову робочий */
            }
        }

        void on(EvseController& c, const CpChanged& e)
        {
            if (e.level == CpClass::B) {
                c.template transitionTo<Connected>(); /* акумулятор набрався */
            } else if (e.level == CpClass::A) {
                c.template transitionTo<Standby>(); /* штекер висмикнули */
            }
        }
    };

    struct Fault {
        FaultReason reason{FaultReason::None};

        constexpr Fault() noexcept = default;
        constexpr explicit Fault(FaultReason r) noexcept : reason{r} {}

        [[nodiscard]] static constexpr std::string_view name() noexcept { return "FAULT"; }

        void onEnter(EvseController& c)
        {
            /* Пілот притискаємо до нуля: автомобіль зобов'язаний трактувати це
             * як заборону заряджання й розімкнути власний контактор. */
            c.board().setRelay(false);
            c.board().forcePilotLow();
            c.board().setLock(false);
            c.setLeds(false, false, true);
            c.timers().arm(TimerId::FaultLockout, kFaultLockout, c.board().now());
        }

        void onExit(EvseController& c) { c.timers().disarm(TimerId::FaultLockout); }

        void on(EvseController& c, const ResetButton&)
        {
            /* Скидання приймаємо лише після витримки й лише коли пілот знову
             * показує від'єднаний кабель: інакше ризикуємо подати напругу на
             * несправне з'єднання. */
            if (!c.timers().isArmed(TimerId::FaultLockout) && c.line() == CpClass::A) {
                c.template transitionTo<Standby>();
            }
        }
    };

    using Machine = StateMachine<EvseController, Standby, Connected, Charging, Fault>;

    // --------------------------------------------------------- контролер ---

    EvseController(B& board, Timers& timers) noexcept
        : board_{board}, timers_{timers}, machine_{*this}
    {
    }

    void start() { machine_.start(); }

    /* Точка входу з головного циклу: подія розпаковується з варіанта, і далі
     * її тип відомий на етапі компіляції. */
    void dispatch(const Event& event)
    {
        std::visit([this](const auto& e) { this->handle(e); }, event);
    }

    /* Останній підтверджений клас лінії: його оновлює обробник CpChanged. */
    [[nodiscard]] CpClass line() const noexcept { return line_; }

    [[nodiscard]] B&      board() noexcept { return board_; }
    [[nodiscard]] Timers& timers() noexcept { return timers_; }
    [[nodiscard]] Amperes currentLimit() const noexcept { return kCurrentLimit; }
    [[nodiscard]] FaultReason fault() const noexcept { return fault_; }
    [[nodiscard]] std::string_view stateName() const { return machine_.stateName(); }

    template <class S, class... Args>
    void transitionTo(Args&&... args)
    {
        machine_.template transitionTo<S>(std::forward<Args>(args)...);
    }

    void setLeds(bool green, bool blue, bool red)
    {
        board_.setLed(Led::Green, green);
        board_.setLed(Led::Blue, blue);
        board_.setLed(Led::Red, red);
    }

private:
    /*
     * Аварійні події перехоплюються до того, як подія дійде до поточного
     * стану: один запис замість чотирьох однакових гілок у кожному стані.
     * Перевантаження за типом події замінює тут ланцюг if-ів.
     */
    void handle(const EmergencyStop&) { trip(FaultReason::EmergencyButton); }

    void handle(const Overcurrent& e)
    {
        if (auto* charging = machine_.template stateIf<Charging>();
            charging != nullptr && charging->settling && e.peak < kInrushTolerance) {
            return; /* пусковий струм, а не аварія */
        }
        trip(FaultReason::Overcurrent);
    }

    void handle(const LeakageTrip& e)
    {
        if (e.leak < kLeakageTrip) {
            return; /* фоновий витік ємності кабелю */
        }
        trip(FaultReason::Leakage);
    }

    void handle(const QueueOverflow&) { trip(FaultReason::QueueOverflow); }

    void handle(const CpChanged& e)
    {
        line_ = e.level;
        if (e.level == CpClass::Invalid) {
            trip(FaultReason::PilotInvalid);
            return;
        }
        machine_.dispatch(e);
    }

    template <class E>
    void handle(const E& e)
    {
        machine_.dispatch(e);
    }

    void trip(FaultReason reason)
    {
        if (machine_.template isIn<Fault>()) {
            return; /* уже в аварії: код першої причини не затираємо */
        }
        fault_ = reason;
        machine_.template transitionTo<Fault>(reason);
        machine_.commit();
    }

    B&          board_;
    Timers&     timers_;
    Machine     machine_;
    CpClass     line_{CpClass::A};
    FaultReason fault_{FaultReason::None};
};

} // namespace evse
