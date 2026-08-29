#include "ads1220.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>

namespace rtd {
namespace {

// Команди мікросхеми
constexpr std::uint8_t kCmdReset = 0x06;
constexpr std::uint8_t kCmdStart = 0x08;
constexpr std::uint8_t kCmdRdata = 0x10;

constexpr std::uint8_t readRegisters(std::uint8_t first, std::uint8_t count) noexcept {
    return static_cast<std::uint8_t>(0x20 | (first << 2) | (count - 1));
}
constexpr std::uint8_t writeRegisters(std::uint8_t first, std::uint8_t count) noexcept {
    return static_cast<std::uint8_t>(0x40 | (first << 2) | (count - 1));
}

// Робоча конфігурація для 3-провідного PT100 — розібрана в статті
constexpr std::uint8_t kReg0Measure = 0x38;  // вхід AIN1-AIN2, підсилення 16, PGA увімкнено
constexpr std::uint8_t kReg0Offset  = 0xE8;  // входи закорочені на (AVDD+AVSS)/2
constexpr std::uint8_t kReg1Work    = 0x00;  // 20 вибірок/с, одиничне перетворення
constexpr std::uint8_t kReg2Work    = 0x76;  // зовнішня опора, фільтр 50/60 Гц, IDAC 500 мкА
constexpr std::uint8_t kReg3Work    = 0x60;  // IDAC1 на AIN0, IDAC2 на AIN1, окремий DRDY

// 20 вибірок/с дають ~50 мс на перетворення, решта — запас
constexpr auto kConversionTimeout = std::chrono::milliseconds{100};

constexpr std::int32_t kPositiveFullScale =  0x7FFFFF;
constexpr std::int32_t kNegativeFullScale = -0x800000;
constexpr std::int32_t kRailMargin        =  16;

constexpr int kOffsetAverageCount = 8;

// Помилка шини цікавить виклик рівно настільки, наскільки вона зірвала вимір
constexpr AdcError asAdcError(BusError) noexcept { return AdcError::Bus; }

}  // namespace

std::string_view describe(AdcError error) noexcept {
    switch (error) {
        case AdcError::Bus:              return "збій обміну по SPI";
        case AdcError::ConfigMismatch:   return "регістри не підтвердилися";
        case AdcError::Timeout:          return "DRDY не відгукнувся";
        case AdcError::SensorOutOfRange: return "датчик обірваний або закорочений";
    }
    return "невідома помилка";
}

std::expected<void, AdcError> Ads1220::writeInputRegister(std::uint8_t value) noexcept {
    const std::array<std::uint8_t, 2> frame{writeRegisters(0, 1), value};
    return bus_->write(frame).transform_error(asAdcError);
}

std::expected<void, AdcError> Ads1220::init() noexcept {
    offsetCode_ = 0;
    dataReady_  = false;

    const std::array<std::uint8_t, 1> reset{kCmdReset};
    if (auto sent = bus_->write(reset); !sent) {
        return std::unexpected(asAdcError(sent.error()));
    }
    HAL_Delay(1);  // після скидання мікросхемі треба ~50 мкс плюс 32 такти

    const std::array<std::uint8_t, 5> config{
        writeRegisters(0, 4), kReg0Measure, kReg1Work, kReg2Work, kReg3Work};
    if (auto sent = bus_->write(config); !sent) {
        return std::unexpected(asAdcError(sent.error()));
    }

    // Перечитуємо записане. Обірваний MISO, переплутаний CS чи неправильний
    // режим SPI інакше виявляться аж на дивних показах температури, коли
    // шукати причину вже вчетверо дорожче.
    const std::array<std::uint8_t, 5> query{readRegisters(0, 4), 0, 0, 0, 0};
    std::array<std::uint8_t, 5> echo{};
    if (auto done = bus_->transfer(query, echo); !done) {
        return std::unexpected(asAdcError(done.error()));
    }
    if (!std::equal(echo.begin() + 1, echo.end(), config.begin() + 1)) {
        return std::unexpected(AdcError::ConfigMismatch);
    }

    return {};
}

std::expected<std::int32_t, AdcError> Ads1220::convertOnce() noexcept {
    dataReady_ = false;

    const std::array<std::uint8_t, 1> start{kCmdStart};
    if (auto sent = bus_->write(start); !sent) {
        return std::unexpected(asAdcError(sent.error()));
    }

    // Одиничне перетворення означає, що струми збудження течуть крізь
    // датчик лише ці ~50 мс — саме тому саморозігрів лишається мізерним.
    const std::uint32_t started = HAL_GetTick();
    while (!dataReady_) {
        if ((HAL_GetTick() - started) > static_cast<std::uint32_t>(kConversionTimeout.count())) {
            return std::unexpected(AdcError::Timeout);
        }
        __WFI();  // спимо до наступного переривання: DRDY або системний тик
    }

    const std::array<std::uint8_t, 4> request{kCmdRdata, 0, 0, 0};
    std::array<std::uint8_t, 4> response{};
    if (auto done = bus_->transfer(request, response); !done) {
        return std::unexpected(asAdcError(done.error()));
    }

    std::int32_t code = (static_cast<std::int32_t>(response[1]) << 16) |
                        (static_cast<std::int32_t>(response[2]) << 8) |
                        (static_cast<std::int32_t>(response[3]));
    if (code & 0x00800000) {
        code -= 0x01000000;  // доповнення знакового розряду до 32 біт
    }
    return code;
}

std::expected<void, AdcError> Ads1220::calibrateOffset() noexcept {
    if (auto switched = writeInputRegister(kReg0Offset); !switched) {
        return switched;
    }

    std::int64_t sum = 0;
    std::expected<std::int32_t, AdcError> sample = convertOnce();

    // Перший відлік після перемикання мультиплексора беремо й викидаємо:
    // вхідний ланцюг цифрового фільтра ще пам'ятає попередній сигнал.
    for (int taken = 0; sample && taken < kOffsetAverageCount; ++taken) {
        sample = convertOnce();
        if (sample) {
            sum += *sample;
        }
    }

    // Робочу конфігурацію входу повертаємо навіть після невдачі: інакше
    // наступний вимір мовчки читав би закорочені всередині входи.
    const auto restored = writeInputRegister(kReg0Measure);
    if (!sample) {
        return std::unexpected(sample.error());
    }
    if (!restored) {
        return restored;
    }

    offsetCode_ = static_cast<std::int32_t>(sum / kOffsetAverageCount);
    return {};
}

std::expected<float, AdcError> Ads1220::readResistance() noexcept {
    const auto code = convertOnce();
    if (!code) {
        return std::unexpected(code.error());
    }

    // Код, упертий у край шкали, — це не гаряча пічка, а обірваний дріт
    // або закорочений датчик: рахувати з нього температуру нема сенсу.
    if (*code >= (kPositiveFullScale - kRailMargin) ||
        *code <= (kNegativeFullScale + kRailMargin)) {
        return std::unexpected(AdcError::SensorOutOfRange);
    }

    // Логометричний перерахунок: струм збудження скорочується, лишається
    // відношення опору датчика до еталонного резистора.
    const auto corrected = static_cast<float>(*code - offsetCode_);
    return (corrected * 2.0F * refOhms_) / (8388608.0F * gain_);
}

}  // namespace rtd
