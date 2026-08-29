#include "ads1220.hpp"

#include <algorithm>
#include <array>

namespace ads1220 {
namespace {

// Команди інтерфейсу (даташит TI SBAS501, розділ «Command Definitions»).
constexpr std::uint8_t cmd_reset = 0x06;
constexpr std::uint8_t cmd_start = 0x08;
constexpr std::uint8_t cmd_rdata = 0x10;

constexpr std::size_t register_count = 4;

// RREG/WREG несуть у молодших бітах адресу регістра і кількість байтів
// мінус один. Читаємо й пишемо всі чотири регістри одним пакетом.
constexpr std::uint8_t rreg(std::uint8_t first, std::uint8_t count) noexcept
{
    return static_cast<std::uint8_t>(0x20 | (first << 2) | (count - 1));
}

constexpr std::uint8_t wreg(std::uint8_t first, std::uint8_t count) noexcept
{
    return static_cast<std::uint8_t>(0x40 | (first << 2) | (count - 1));
}

// Регістр 0: MUX = 0000 (диференційна пара AIN0/AIN1), GAIN = 101 (32),
//            PGA_BYPASS = 0 — PGA увімкнено, вхід високоомний.
// Регістр 1: DR = 000 (20 SPS у нормальному режимі), MODE = 00 (нормальний),
//            CM = 1 (неперервні перетворення), TS = 0, BCS = 0.
// Регістр 2: VREF = 01 (зовнішня опора REFP0/REFN0), 50/60 = 01 (одночасне
//            придушення 50 і 60 Гц, доступне саме при 20 SPS), PSW = 0, IDAC = 000.
// Регістр 3: усі поля нульові — DRDY віддається окремою лінією, а не поверх DOUT.
constexpr std::array<std::uint8_t, register_count> configuration{0x0A, 0x04, 0x50, 0x00};

}  // namespace

std::string_view describe(Error error) noexcept
{
    switch (error) {
        case Error::spi:             return "обмін SPI не завершився";
        case Error::timeout:         return "DRDY мовчить";
        case Error::config_mismatch: return "конфігурація не записалася";
        case Error::over_range:      return "вхід за межами шкали";
    }
    return "невідомий стан";
}

std::expected<void, Error> Driver::command(std::uint8_t opcode)
{
    const std::array<std::uint8_t, 1> tx{opcode};
    std::array<std::uint8_t, 1> rx{};

    auto cs = bus_.select();
    if (!bus_.transfer(tx, rx)) {
        return std::unexpected(Error::spi);
    }
    return {};
}

std::expected<void, Error> Driver::configure()
{
    if (auto reset = command(cmd_reset); !reset) {
        return reset;
    }

    // Даташит вимагає витримати після скидання 50 мкс плюс 32 такти
    // модулятора; двох мілісекунд вистачає з великим запасом.
    board::sleep(std::chrono::milliseconds{2});

    const std::array<std::uint8_t, 1 + register_count> tx{
        wreg(0, register_count), configuration[0], configuration[1],
        configuration[2], configuration[3]};
    std::array<std::uint8_t, 1 + register_count> rx{};
    {
        auto cs = bus_.select();
        if (!bus_.transfer(tx, rx)) {
            return std::unexpected(Error::spi);
        }
    }

    // Читаємо конфігурацію назад і звіряємо. Це не параноя: якщо лінію CS
    // розвели через розріз полігону і на її зворотний струм наклався дзвін,
    // чип половину команд не побачить. Він лишиться в стандартному
    // ввімкненні — підсилення 1, внутрішня опора 2.048 В, — і всі виміри
    // поїдуть у смітник, жодного разу не поскаржившись.
    const std::array<std::uint8_t, 1 + register_count> query{
        rreg(0, register_count), 0xFF, 0xFF, 0xFF, 0xFF};  // DIN чип під час читання ігнорує
    std::array<std::uint8_t, 1 + register_count> answer{};
    {
        auto cs = bus_.select();
        if (!bus_.transfer(query, answer)) {
            return std::unexpected(Error::spi);
        }
    }

    if (!std::ranges::equal(std::span{answer}.subspan(1), configuration)) {
        return std::unexpected(Error::config_mismatch);
    }
    return {};
}

std::expected<void, Error> Driver::start()
{
    return command(cmd_start);
}

std::expected<Code, Error> Driver::read(std::chrono::milliseconds timeout)
{
    const auto deadline = board::uptime() + timeout;
    while (!board::data_ready()) {
        if (board::uptime() > deadline) {
            return std::unexpected(Error::timeout);
        }
    }

    const std::array<std::uint8_t, 4> tx{cmd_rdata, 0, 0, 0};
    std::array<std::uint8_t, 4> rx{};
    {
        auto cs = bus_.select();
        if (!bus_.transfer(tx, rx)) {
            return std::unexpected(Error::spi);
        }
    }

    // Три байти результату йдуть старшим уперед, у доповняльному коді.
    std::int32_t value = (std::int32_t{rx[1]} << 16)
                       | (std::int32_t{rx[2]} << 8)
                       | std::int32_t{rx[3]};
    if ((value & 0x0080'0000) != 0) {
        value -= 0x0100'0000;
    }

    const Code code{value};
    if (code.saturated()) {
        return std::unexpected(Error::over_range);
    }
    return code;
}

}  // namespace ads1220
