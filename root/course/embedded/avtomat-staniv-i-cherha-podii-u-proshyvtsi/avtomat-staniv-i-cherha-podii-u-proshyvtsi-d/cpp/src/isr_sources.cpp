#include "isr_sources.hpp"

#include "evse/rfid.hpp"
#include "evse/units.hpp"

#include "system.hpp"

namespace {

/* Механічний контакт кнопки деренчить одиниці мілісекунд. */
constexpr evse::Millis kButtonDebounce{50};

evse::Millis g_lastEmergency{-1000};
evse::Millis g_lastReset{-1000};

evse::RfidFrameParser g_rfid;

unsigned g_tickCounter = 0;

/*
 * Придушення деренчання просто в обробнику: подія народжується лише з першого
 * фронту, решта імпульсів у вікні відкидається, не займаючи місця в черзі.
 */
bool debouncePassed(evse::Millis& last) noexcept
{
    const auto now = app::board().now();
    if (now - last < kButtonDebounce) {
        return false;
    }
    last = now;
    return true;
}

} // namespace

extern "C" {

void evse_isr_systick_1ms()
{
    const auto now = app::board().now();

    /* Служба таймерів не знає ні про чергу, ні про події — вона лише називає
     * номер таймера, чий термін настав. Перетворення на подію робиться тут. */
    app::g_timers.tick(now, [](evse::TimerId id) { app::post(evse::Expired{id}); });

    if (++g_tickCounter >= 10) {
        g_tickCounter = 0;
        /* Сам вимір лінії пілота робить головний цикл: тут лише позначка, що
         * час настав. Читання трьох каналів АЦП у перериванні затримало б
         * приймач UART і зіпсувало б кадр картки. */
        app::post(evse::Tick10ms{});
    }
}

void evse_isr_emergency_button()
{
    if (debouncePassed(g_lastEmergency)) {
        app::post(evse::EmergencyStop{});
    }
}

void evse_isr_reset_button()
{
    if (debouncePassed(g_lastReset)) {
        app::post(evse::ResetButton{});
    }
}

void evse_isr_overcurrent(std::uint16_t amperes)
{
    app::post(evse::Overcurrent{evse::Amperes{amperes}});
}

void evse_isr_leakage(std::uint16_t milliamps)
{
    app::post(evse::LeakageTrip{evse::Milliamps{milliamps}});
}

void evse_isr_rfid_rx(std::uint8_t byte)
{
    /* Розбір кадру — це порівняння байтів і зсуви: рівно та робота, яку можна
     * робити в перериванні. Подія народжується лише тоді, коли кадр зібрався
     * цілим і контрольна сума збіглася. */
    if (const auto card = g_rfid.feed(byte)) {
        app::post(evse::RfidTag{*card});
    }
}

} // extern "C"
