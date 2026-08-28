#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace smbus {

inline constexpr uint8_t POLYNOMIAL = 0x07;

/* Генерація таблиці пошуку на етапі компіляції (zero runtime overhead) */
consteval std::array<uint8_t, 256> generate_crc8_table() noexcept {
    std::array<uint8_t, 256> table{};
    for (size_t i = 0; i < 256; ++i) {
        auto curr = static_cast<uint8_t>(i);
        for (size_t bit = 0; bit < 8; ++bit) {
            if (curr & 0x80) {
                curr = static_cast<uint8_t>((curr << 1) ^ POLYNOMIAL);
            } else {
                curr = static_cast<uint8_t>(curr << 1);
            }
        }
        table[i] = curr;
    }
    return table;
}

inline constexpr auto CRC8_LUT = generate_crc8_table();

/* Клас потокового обчислювача PEC */
class PecCalculator {
public:
    constexpr PecCalculator() noexcept = default;

    constexpr void update(uint8_t byte) noexcept {
        m_crc = CRC8_LUT[m_crc ^ byte];
    }

    constexpr void update(std::span<const uint8_t> bytes) noexcept {
        for (uint8_t b : bytes) {
            m_crc = CRC8_LUT[m_crc ^ b];
        }
    }

    [[nodiscard]] constexpr uint8_t value() const noexcept {
        return m_crc;
    }

    constexpr void reset() noexcept {
        m_crc = 0x00;
    }

private:
    uint8_t m_crc{0x00};
};

enum class Error {
    PecMismatch,
    BusTimeout,
    NackReceived
};

/* Обчислення PEC для транзакції Write Word */
[[nodiscard]] constexpr uint8_t calc_write_word_pec(uint8_t slave_addr_7bit,
                                                    uint8_t cmd,
                                                    uint16_t value) noexcept {
    PecCalculator calc;
    const uint8_t addr_wr = static_cast<uint8_t>(slave_addr_7bit << 1);
    const auto data_low = static_cast<uint8_t>(value & 0xFF);
    const auto data_high = static_cast<uint8_t>((value >> 8) & 0xFF);

    calc.update(addr_wr);
    calc.update(cmd);
    calc.update(data_low);
    calc.update(data_high);
    return calc.value();
}

/* Перевірка цілісності транзакції Read Word */
[[nodiscard]] constexpr std::expected<uint16_t, Error> verify_read_word(
    uint8_t slave_addr_7bit,
    uint8_t cmd,
    uint8_t data_low,
    uint8_t data_high,
    uint8_t rx_pec) noexcept {

    PecCalculator calc;
    const uint8_t addr_wr = static_cast<uint8_t>(slave_addr_7bit << 1);
    const uint8_t addr_rd = static_cast<uint8_t>((slave_addr_7bit << 1) | 0x01);

    calc.update(addr_wr);
    calc.update(cmd);
    calc.update(addr_rd);
    calc.update(data_low);
    calc.update(data_high);

    if (calc.value() != rx_pec) {
        return std::unexpected(Error::PecMismatch);
    }

    const auto result = static_cast<uint16_t>((static_cast<uint16_t>(data_high) << 8) | data_low);
    return result;
}

/* Обчислення PEC для транзакції Block Write */
[[nodiscard]] constexpr uint8_t calc_block_write_pec(uint8_t slave_addr_7bit,
                                                     uint8_t cmd,
                                                     std::span<const uint8_t> data) noexcept {
    PecCalculator calc;
    const uint8_t addr_wr = static_cast<uint8_t>(slave_addr_7bit << 1);
    const auto length = static_cast<uint8_t>(data.size());

    calc.update(addr_wr);
    calc.update(cmd);
    calc.update(length);
    calc.update(data);
    return calc.value();
}

/* Логіка обробки прийому кадру Write Word веденим пристроєм у C++ */
[[nodiscard]] constexpr std::expected<uint16_t, Error> slave_process_write_word(
    uint8_t slave_addr_7bit,
    uint8_t cmd,
    uint8_t low,
    uint8_t high,
    uint8_t rx_pec) noexcept {

    const uint16_t val = static_cast<uint16_t>((static_cast<uint16_t>(high) << 8) | low);
    const uint8_t expected = calc_write_word_pec(slave_addr_7bit, cmd, val);
    if (expected != rx_pec) {
        return std::unexpected(Error::PecMismatch);
    }
    return val;
}

/* Compile-time перевірка еталонного вектора та логіки верифікації */
static_assert([]() consteval {
    constexpr std::array<uint8_t, 9> test_vec = {0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39};
    PecCalculator calc;
    calc.update(test_vec);
    if (calc.value() != 0xF4) return false;

    auto res = slave_process_write_word(0x16, 0x09, 0xA0, 0x0F, calc_write_word_pec(0x16, 0x09, 0x0FA0));
    return res.has_value() && res.value() == 0x0FA0;
}(), "Помилка розрахунку еталонного вектора SMBus PEC");

} // namespace smbus
