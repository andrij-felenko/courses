#include "bus_recovery.hpp"

#include "open_drain_pin.hpp"
#include "timing.hpp"

#include "stm32f10x.h"

namespace hw {
namespace {

using namespace std::chrono_literals;

/* Напівперіод ручного тактування. Стандартний режим вимагає щонайменше 4.7 мкс
   утримання рівня: коротший імпульс вхідний фільтр веденого має право прийняти
   за голку й проковтнути — тоді байт у ньому не зсунеться. */
constexpr auto kHalfPeriod = 5us;

/* Запас на пологий фронт: 10 кОм підтяжки на 200 пФ ємності шини дають постійну
   часу близько 2 мкс, і одиниця з'являється помітно пізніше за команду
   «відпустити». Сюди ж потрапляє й розтягування такту веденим. */
constexpr auto kRiseTimeout = 100us;

constexpr std::uint8_t kClockPulses = 9U;

bool wait_high(const OpenDrainPin& pin) noexcept {
    return bsp::wait_until([&pin]() noexcept { return pin.high(); }, kRiseTimeout);
}

} // namespace

std::expected<RecoveryReport, BusFault> recover_i2c1_bus() noexcept {
    /* Тактування порту й AFIO: без нього запис у CRL просто нікуди не піде */
    RCC->APB2ENR |= RCC_APB2ENR_IOPBEN | RCC_APB2ENR_AFIOEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* Модуль тримаємо у скиданні протягом усього ручного тактування. Це чистить
       залиплий скінченний автомат з аналоговим фільтром і не дає контролеру
       побачити чужі фронти на власних виводах та знову впасти в BERR. */
    RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
    bsp::delay(2us);

    i2c1_scl.set_mode(OpenDrainPin::Mode::Gpio);
    i2c1_sda.set_mode(OpenDrainPin::Mode::Gpio);
    i2c1_scl.release();
    i2c1_sda.release();

    if (!wait_high(i2c1_scl)) {
        return std::unexpected{BusFault::SclStuckLow};   /* тактувати нічим */
    }
    bsp::delay(kHalfPeriod);

    /* До дев'яти тактів, доки ведений не догортає свій байт і не відпустить SDA.
       Стан лінії перевіряємо ПЕРЕД кожним тактом: звільнилася на третьому —
       решту шести видавати немає потреби. */
    RecoveryReport report{.pulses = 0U};
    while (!i2c1_sda.high() && report.pulses < kClockPulses) {
        i2c1_scl.pull_low();
        bsp::delay(kHalfPeriod);

        i2c1_scl.release();
        if (!wait_high(i2c1_scl)) {
            return std::unexpected{BusFault::SclStuckLow};
        }
        bsp::delay(kHalfPeriod);

        ++report.pulses;
    }

    if (!i2c1_sda.high()) {
        /* Дев'ять тактів догортають будь-який байт. Якщо дані досі внизу, це вже
           не протокол: коротке замикання на платі або мертвий кристал. */
        return std::unexpected{BusFault::SdaStuckLow};
    }

    /* Ручний STOP: при високому SCL переводимо SDA з нуля в одиницю. Усі ведені
       сприймуть це як кінець транзакції й підуть чекати нової адреси. */
    i2c1_sda.pull_low();
    bsp::delay(kHalfPeriod);
    i2c1_scl.release();               /* SCL і так високий — тримаємо його таким */
    bsp::delay(kHalfPeriod);
    i2c1_sda.release();
    if (!wait_high(i2c1_sda)) {
        return std::unexpected{BusFault::SdaStuckLow};
    }
    bsp::delay(kHalfPeriod);

    if (!i2c1_scl.high()) {
        return std::unexpected{BusFault::SclStuckLow};
    }

    /* Обидві лінії у спокої — віддаємо виводи периферії й знімаємо скидання */
    i2c1_scl.set_mode(OpenDrainPin::Mode::AlternateFunction);
    i2c1_sda.set_mode(OpenDrainPin::Mode::AlternateFunction);
    RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;

    return report;
}

} // namespace hw
