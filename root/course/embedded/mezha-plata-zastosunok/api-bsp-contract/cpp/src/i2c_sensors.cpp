#include "i2c_sensors.hpp"

#include <array>
#include <chrono>
#include <cstdint>

namespace bsp::detail {
namespace {

using namespace std::chrono_literals;

/* CRC-8 Sensirion: поліном 0x31, початкове значення 0xFF. */
[[nodiscard]] constexpr std::uint8_t sht_crc(std::span<const std::uint8_t> data) noexcept {
    std::uint8_t crc = 0xFF;
    for (std::uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x80U) != 0U ? static_cast<std::uint8_t>((crc << 1) ^ 0x31U)
                                      : static_cast<std::uint8_t>(crc << 1);
        }
    }
    return crc;
}

[[nodiscard]] constexpr std::uint16_t be16(std::span<const std::uint8_t, 2> raw) noexcept {
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(raw[0]) << 8) | raw[1]);
}

[[nodiscard]] constexpr std::uint16_t le16(std::span<const std::uint8_t> raw,
                                           std::size_t offset) noexcept {
    return static_cast<std::uint16_t>(raw[offset] |
                                      (static_cast<std::uint16_t>(raw[offset + 1]) << 8));
}

[[nodiscard]] constexpr std::int16_t le16s(std::span<const std::uint8_t> raw,
                                           std::size_t offset) noexcept {
    return static_cast<std::int16_t>(le16(raw, offset));
}

constexpr std::uint8_t kBmpRegId        = 0xD0;
constexpr std::uint8_t kBmpRegStatus    = 0xF3;
constexpr std::uint8_t kBmpRegCtrlMeas  = 0xF4;
constexpr std::uint8_t kBmpRegConfig    = 0xF5;
constexpr std::uint8_t kBmpRegCalib     = 0x88;
constexpr std::uint8_t kBmpRegData      = 0xF7;
constexpr std::uint8_t kBmpChipId       = 0x58;
constexpr std::uint8_t kBmpCtrlForced   = 0x25; // osrs_t x1, osrs_p x1, forced

} // namespace

std::expected<Sht3x::Reading, Status> Sht3x::measure() noexcept {
    constexpr std::array<std::uint8_t, 2> kCmdMeasure{0x24, 0x00};

    if (auto sent = platform_.i2c_write(address_, kCmdMeasure); !sent) {
        return fail(sent.error());
    }
    platform_.delay(15ms); // висока повторюваність, без розтягування такту

    std::array<std::uint8_t, 6> rx{};
    if (auto got = platform_.i2c_read(address_, rx); !got) {
        return fail(got.error());
    }

    const auto words = std::span<const std::uint8_t>{rx};
    if (sht_crc(words.subspan(0, 2)) != rx[2] || sht_crc(words.subspan(3, 2)) != rx[5]) {
        return fail(Status::BusFault);
    }

    const std::uint32_t raw_t = be16(words.subspan<0, 2>());
    const std::uint32_t raw_h = be16(words.subspan<3, 2>());

    return Reading{
        // T = -45 + 175 * raw / 65535, одразу в сотих частках градуса
        .temperature_centi_c =
            static_cast<std::int16_t>(static_cast<std::int32_t>((17500U * raw_t) / 65535U) - 4500),
        // RH = 100 * raw / 65535, у сотих частках відсотка
        .humidity_centi_pct = static_cast<std::uint16_t>((10000U * raw_h) / 65535U),
    };
}

Result Bmp280::read_regs(std::uint8_t reg, std::span<std::uint8_t> out) noexcept {
    const std::array<std::uint8_t, 1> tx{reg};
    return platform_.i2c_write_read(address_, tx, out);
}

Result Bmp280::write_reg(std::uint8_t reg, std::uint8_t value) noexcept {
    const std::array<std::uint8_t, 2> tx{reg, value};
    return platform_.i2c_write(address_, tx);
}

std::expected<Bmp280::Calibration, Status> Bmp280::load_calibration() noexcept {
    std::array<std::uint8_t, 1> id{};
    if (auto got = read_regs(kBmpRegId, id); !got) {
        return fail(got.error());
    }
    if (id[0] != kBmpChipId) {
        // Відповів хтось інший: інша адреса або інша ревізія плати.
        return fail(Status::Unsupported);
    }

    std::array<std::uint8_t, 24> raw{};
    if (auto got = read_regs(kBmpRegCalib, raw); !got) {
        return fail(got.error());
    }

    Calibration cal{
        .t1 = le16(raw, 0),   .t2 = le16s(raw, 2),  .t3 = le16s(raw, 4),
        .p1 = le16(raw, 6),   .p2 = le16s(raw, 8),  .p3 = le16s(raw, 10),
        .p4 = le16s(raw, 12), .p5 = le16s(raw, 14), .p6 = le16s(raw, 16),
        .p7 = le16s(raw, 18), .p8 = le16s(raw, 20), .p9 = le16s(raw, 22),
    };
    // Нулі в T1/P1 — ознака побитої сторінки: рахувати по ній не можна.
    if (cal.t1 == 0 || cal.p1 == 0) {
        return fail(Status::BusFault);
    }

    // Фільтр IIR вимкнено: у forced він лише розмазав би одиничний відлік.
    if (auto written = write_reg(kBmpRegConfig, 0x00); !written) {
        return fail(written.error());
    }
    return cal;
}

Result Bmp280::wait_ready() noexcept {
    // На x1/x1 перетворення триває ~6.4 мс; чекаємо з запасом.
    for (int attempt = 0; attempt < 20; ++attempt) {
        std::array<std::uint8_t, 1> status{};
        if (auto got = read_regs(kBmpRegStatus, status); !got) {
            return got;
        }
        if ((status[0] & 0x08U) == 0U) {
            return {};
        }
        platform_.delay(1ms);
    }
    return fail(Status::Timeout);
}

std::expected<std::uint32_t, Status> Bmp280::pressure_pa() noexcept {
    if (!calibration_.has_value()) {
        auto loaded = load_calibration();
        if (!loaded) {
            return fail(loaded.error());
        }
        calibration_ = *loaded;
    }
    const Calibration& cal = *calibration_;

    if (auto written = write_reg(kBmpRegCtrlMeas, kBmpCtrlForced); !written) {
        return fail(written.error());
    }
    if (auto ready = wait_ready(); !ready) {
        return fail(ready.error());
    }

    std::array<std::uint8_t, 6> raw{};
    if (auto got = read_regs(kBmpRegData, raw); !got) {
        return fail(got.error());
    }

    const auto adc_p = static_cast<std::int32_t>((static_cast<std::uint32_t>(raw[0]) << 12) |
                                                 (static_cast<std::uint32_t>(raw[1]) << 4) |
                                                 (static_cast<std::uint32_t>(raw[2]) >> 4));
    const auto adc_t = static_cast<std::int32_t>((static_cast<std::uint32_t>(raw[3]) << 12) |
                                                 (static_cast<std::uint32_t>(raw[4]) << 4) |
                                                 (static_cast<std::uint32_t>(raw[5]) >> 4));
    // 0x80000 — вміст регістрів після скидання: вимірювання не відбулося.
    if (adc_p == 0x80000 || adc_t == 0x80000) {
        return fail(Status::Timeout);
    }

    // Компенсація за документацією Bosch, цілочисельний варіант.
    const std::int32_t v1t = (((adc_t >> 3) - (static_cast<std::int32_t>(cal.t1) << 1)) *
                              static_cast<std::int32_t>(cal.t2)) >> 11;
    const std::int32_t v2t = ((((adc_t >> 4) - static_cast<std::int32_t>(cal.t1)) *
                               ((adc_t >> 4) - static_cast<std::int32_t>(cal.t1))) >> 12) *
                             static_cast<std::int32_t>(cal.t3) >> 14;
    const std::int32_t t_fine = v1t + v2t;

    std::int64_t v1 = static_cast<std::int64_t>(t_fine) - 128000;
    std::int64_t v2 = v1 * v1 * static_cast<std::int64_t>(cal.p6);
    v2 += (v1 * static_cast<std::int64_t>(cal.p5)) << 17;
    v2 += static_cast<std::int64_t>(cal.p4) << 35;
    v1 = ((v1 * v1 * static_cast<std::int64_t>(cal.p3)) >> 8) +
         ((v1 * static_cast<std::int64_t>(cal.p2)) << 12);
    v1 = (((static_cast<std::int64_t>(1) << 47) + v1) * static_cast<std::int64_t>(cal.p1)) >> 33;
    if (v1 == 0) {
        calibration_.reset();
        return fail(Status::BusFault);
    }

    std::int64_t p = 1048576 - adc_p;
    p = (((p << 31) - v2) * 3125) / v1;
    v1 = (static_cast<std::int64_t>(cal.p9) * (p >> 13) * (p >> 13)) >> 25;
    v2 = (static_cast<std::int64_t>(cal.p8) * p) >> 19;
    p = ((p + v1 + v2) >> 8) + (static_cast<std::int64_t>(cal.p7) << 4);

    const auto pascals = static_cast<std::uint32_t>(p >> 8); // Q24.8 → Па
    // Поза земними межами — отже читали сміття, а не тиск.
    if (pascals < 30000U || pascals > 120000U) {
        calibration_.reset();
        return fail(Status::BusFault);
    }
    return pascals;
}

} // namespace bsp::detail
