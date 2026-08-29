// ads1220.hpp — 24-бітний дельта-сигма АЦП TI ADS1220 як об'єкт.
//
// Кожна дія, що ходить по шині, повертає std::expected: помилку не можна
// тихо не помітити, а успішне значення не існує окремо від успіху. Сирий
// код загорнуто в тип Code, щоб його не можна було випадково передати туди,
// де чекають нановольти.
#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <string_view>

#include "board.hpp"

namespace ads1220 {

enum class Error {
    spi,               // контролер SPI не завершив обмін
    timeout,           // DRDY мовчить: чип скинувся або втратив живлення
    config_mismatch,   // прочитана назад конфігурація не збіглася із записаною
    over_range         // вхід вийшов за межі шкали
};

[[nodiscard]] std::string_view describe(Error error) noexcept;

// Значення поля GAIN у регістрі 0 — воно ж показник степеня двійки.
enum class Gain : std::uint8_t { x1 = 0, x2, x4, x8, x16, x32, x64, x128 };

// Сирий диференційний код перетворювача.
struct Code {
    static constexpr std::int32_t full_scale = 8'388'607;  // 2^23 − 1

    std::int32_t value{};

    [[nodiscard]] constexpr bool saturated() const noexcept
    {
        return value >= full_scale || value <= -full_scale;
    }
};

class Driver {
public:
    // Опорна напруга з окремого малошумного LDO аналогового домену.
    static constexpr std::int64_t vref_nanovolts = 3'300'000'000;

    // Диференційний вхід AIN0/AIN1, підсилення 32: діапазон ±103.125 мВ —
    // типовий розмах тензометричного мосту.
    static constexpr Gain gain = Gain::x32;

    explicit Driver(board::SpiBus& bus) noexcept : bus_{bus} {}

    // Скидання, запис конфігурації і читання її назад для звірки.
    [[nodiscard]] std::expected<void, Error> configure();

    // Команда START/SYNC — запуск неперервних перетворень.
    [[nodiscard]] std::expected<void, Error> start();

    // Чекає на DRDY і зчитує код із розширенням знака.
    [[nodiscard]] std::expected<Code, Error> read(
        std::chrono::milliseconds timeout = std::chrono::milliseconds{200});

    // Нановольти на вході, вже з урахуванням підсилення. Молодший розряд
    // при G = 32 важить близько 12.3 нВ, тож мікровольти були б грубішими
    // за сам перетворювач.
    [[nodiscard]] static constexpr std::int32_t to_nanovolts(Code code) noexcept
    {
        // Ділимо опору на підсилення першою дією: 3.3·10⁹ ділиться на 32
        // без остачі, а добуток лишається далеко в межах int64.
        constexpr std::int64_t full_scale_nv = vref_nanovolts >> static_cast<int>(gain);

        return static_cast<std::int32_t>((std::int64_t{code.value} * full_scale_nv)
                                         / Code::full_scale);
    }

private:
    [[nodiscard]] std::expected<void, Error> command(std::uint8_t opcode);

    board::SpiBus& bus_;
};

}  // namespace ads1220
