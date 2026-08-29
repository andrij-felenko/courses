#pragma once

/*
 * Порт плати для стенда: замість периферії мікроконтролера — модель станції на
 * настільній машині. Він відтворює саме той сценарій, з якого починається
 * стаття: водій вставляє штекер, прикладає картку, автомобіль просить струм,
 * а через секунду після замикання контактора — у розпал трисекундних
 * перехідних процесів — б'є по кнопці «Грибок».
 *
 * Для справжньої станції цей файл замінюють драйверами GPIO, таймера, АЦП і
 * UART. Жоден інший файл проєкту при цьому не міняється: концепт Board уже
 * описав, що саме від плати потрібно.
 */

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string_view>

#include "evse/board.hpp"
#include "evse/cp_line.hpp"
#include "evse/units.hpp"

#include "isr_sources.hpp"

namespace evse {

class HostBoard {
public:
    static constexpr Millis kSimulationEnd{9'000};

    [[nodiscard]] static HostBoard& instance() noexcept
    {
        static HostBoard board;
        return board;
    }

    /*
     * Критична секція як RAII-об'єкт. Деструктор відновлює саме той стан
     * маски, який був до входу, — а не вмикає переривання беззастережно,
     * інакше вкладений об'єкт розкрив би секцію зовнішнього.
     */
    class IrqLock {
    public:
        IrqLock() noexcept : saved_{instance().irqEnabled_} { instance().irqEnabled_ = false; }

        ~IrqLock()
        {
            instance().irqEnabled_ = saved_;
            if (saved_) {
                instance().servicePending();
            }
        }

        IrqLock(const IrqLock&)            = delete;
        IrqLock& operator=(const IrqLock&) = delete;

    private:
        bool saved_;
    };

    [[nodiscard]] Millis now() const noexcept { return now_; }

    void setRelay(bool closed)
    {
        if (closed == relayClosed_) {
            return;
        }
        relayClosed_ = closed;
        if (closed) {
            relayClosedAt_ = now_;
        }
        log(closed ? "силовий контактор ЗАМКНЕНО" : "силовий контактор розімкнено");
    }

    [[nodiscard]] bool relayClosed() const noexcept { return relayClosed_; }

    void setPilotDuty(Duty duty)
    {
        pilotLow_ = false;
        duty_     = duty;
    }

    void forcePilotLow()
    {
        pilotLow_ = true;
        /* Автомобіль зобов'язаний розімкнути власний контактор і відпустити
         * ключ, тож лінія повертається до класу A. */
        line_ = CpClass::A;
    }

    [[nodiscard]] Millivolts pilotHigh() const noexcept
    {
        if (pilotLow_) {
            return Millivolts{0};
        }
        switch (line_) {
            case CpClass::B: return Millivolts{9000};
            case CpClass::C: return Millivolts{6000};
            default:         return Millivolts{12000};
        }
    }

    /* Діод в автомобілі справний: від'ємний півперіод сягає −12 В. */
    [[nodiscard]] Millivolts pilotLow() const noexcept
    {
        return pilotLow_ ? Millivolts{0} : Millivolts{-12000};
    }

    [[nodiscard]] Micros pilotPeriod() const noexcept
    {
        return (duty_.pwmActive() && !pilotLow_) ? Micros{1000} : Micros{0};
    }

    /* Фоновий витік ємності кабелю. */
    [[nodiscard]] Milliamps leakage() const noexcept { return Milliamps{2}; }

    void setLed(Led led, bool on)
    {
        auto& slot = leds_[static_cast<std::size_t>(led)];
        if (slot == on) {
            return;
        }
        slot = on;
        std::printf("[%5lld мс] світлодіод %s %s\n", static_cast<long long>(now_.count()),
                    ledName(led).data(), on ? "увімкнено" : "вимкнено");
    }

    void setLock(bool locked)
    {
        if (locked == lockEngaged_) {
            return;
        }
        lockEngaged_ = locked;
        log(locked ? "замок роз'єму закрито" : "замок роз'єму відкрито");
    }

    /*
     * Модель інструкції WFI: час стоїть, поки не настане наступна апаратна
     * подія. На справжньому кристалі саме тут споживання падає з 25 мА до
     * одиниць мікроампер.
     *
     * Заявка стає в чергу NVIC, а обробник запуститься, коли головний цикл
     * зніме заборону переривань, — так само, як на Cortex-M із виставленим
     * PRIMASK: WFI прокидається, але ISR чекає на дозвіл.
     */
    void waitForInterrupt()
    {
        if (now_ >= kSimulationEnd) {
            log("кінець сценарію");
            std::exit(0);
        }
        now_ += Millis{1};
        ++pendingTicks_;
    }

private:
    HostBoard() { log("станція увімкнена"); }

    [[nodiscard]] static constexpr std::string_view ledName(Led led) noexcept
    {
        switch (led) {
            case Led::Green: return "зелений";
            case Led::Blue:  return "синій";
            default:         return "червоний";
        }
    }

    void log(std::string_view text) const
    {
        std::printf("[%5lld мс] %.*s\n", static_cast<long long>(now_.count()),
                    static_cast<int>(text.size()), text.data());
    }

    void servicePending()
    {
        if (inIsr_ || !irqEnabled_) {
            return;
        }
        inIsr_ = true;
        while (pendingTicks_ > 0) {
            --pendingTicks_;
            evse_isr_systick_1ms();
            runScenario();
        }
        inIsr_ = false;
    }

    void feedCard(std::uint32_t cardId)
    {
        static constexpr char kHex[] = "0123456789ABCDEF";

        std::uint8_t xored = 0;
        for (unsigned shift = 0; shift < 32; shift += 8) {
            xored ^= static_cast<std::uint8_t>(cardId >> shift);
        }

        evse_isr_rfid_rx(0x02);
        for (int shift = 28; shift >= 0; shift -= 4) {
            evse_isr_rfid_rx(static_cast<std::uint8_t>(kHex[(cardId >> shift) & 0xFu]));
        }
        evse_isr_rfid_rx(static_cast<std::uint8_t>(kHex[(xored >> 4) & 0xFu]));
        evse_isr_rfid_rx(static_cast<std::uint8_t>(kHex[xored & 0xFu]));
        evse_isr_rfid_rx(0x03);
    }

    /* Події зовнішнього світу, прив'язані до модельного часу. */
    void runScenario()
    {
        switch (now_.count()) {
            case 500:
                log("водій вставив штекер");
                line_ = CpClass::B;
                break;

            case 1200:
                log("прикладено картку 0x04A1B2C3");
                feedCard(0x04A1B2C3u);
                break;

            case 2000:
                log("автомобіль замкнув ключ: запит енергії");
                line_ = CpClass::C;
                break;

            case 3000:
                log("*** водій б'є по кнопці аварійної зупинки ***");
                evse_isr_emergency_button();
                break;

            default:
                break;
        }

        /* Компаратор струму опитує силову лінію щомилісекунди й заявляє
         * переривання лише понад 40 А. */
        if (relayClosed_) {
            const auto since   = (now_ - relayClosedAt_).count();
            const auto amperes = static_cast<std::uint16_t>(since < 200 ? 80 : 32);
            if (amperes > 40) {
                evse_isr_overcurrent(amperes);
            }
        }
    }

    Millis  now_{0};
    Millis  relayClosedAt_{0};
    Duty    duty_{Duty::steadyHigh()};
    CpClass line_{CpClass::A};

    bool relayClosed_{false};
    bool lockEngaged_{false};
    bool pilotLow_{false};

    bool          irqEnabled_{true};
    bool          inIsr_{false};
    std::uint32_t pendingTicks_{0};

    std::array<bool, 3> leds_{};
};

static_assert(Board<HostBoard>, "порт плати не задовольняє концепт Board");

} // namespace evse
