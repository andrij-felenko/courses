#include "compensation.hpp"

#include <algorithm>

namespace bmp280 {
namespace {

constexpr std::uint16_t le_u16(std::span<const std::uint8_t, 2> p) noexcept {
    return static_cast<std::uint16_t>(p[0] | (static_cast<std::uint16_t>(p[1]) << 8));
}

// Знакове значення складаємо з беззнакового: зсув у int16_t на межі
// 0x8000 — це переповнення, а не від'ємне число.
constexpr std::int16_t le_s16(std::span<const std::uint8_t, 2> p) noexcept {
    return static_cast<std::int16_t>(le_u16(p));
}

// MSB<<12 | LSB<<4 | XLSB>>4 — молодші 4 біти XLSB відкидаємо.
constexpr std::int32_t unpack20(std::span<const std::uint8_t, 3> p) noexcept {
    return static_cast<std::int32_t>((static_cast<std::uint32_t>(p[0]) << 12) |
                                     (static_cast<std::uint32_t>(p[1]) <<  4) |
                                     (static_cast<std::uint32_t>(p[2]) >>  4));
}

// Зручний зріз фіксованої довжини з великого буфера.
template <std::size_t N>
constexpr std::span<const std::uint8_t, N>
chunk(std::span<const std::uint8_t> src, std::size_t offset) noexcept {
    return src.subspan(offset).first<N>();
}

} // namespace

std::expected<Calibration, Error>
parse_calibration(std::span<const std::uint8_t, calibration_bytes> raw) noexcept
{
    // Мертва шина віддає суцільні 0x00 (лінія притиснута) або 0xFF
    // (лінія лише підтягнута) — обидва випадки це обрив, не калібрування.
    const bool all_zero = std::ranges::all_of(raw, [](std::uint8_t b) { return b == 0x00; });
    const bool all_ones = std::ranges::all_of(raw, [](std::uint8_t b) { return b == 0xFF; });
    if (all_zero || all_ones) {
        return std::unexpected{Error::bad_calibration};
    }

    const std::span<const std::uint8_t> bytes{raw};
    Calibration c{};
    c.dig_T1 = le_u16(chunk<2>(bytes,  0));
    c.dig_T2 = le_s16(chunk<2>(bytes,  2));
    c.dig_T3 = le_s16(chunk<2>(bytes,  4));
    c.dig_P1 = le_u16(chunk<2>(bytes,  6));
    c.dig_P2 = le_s16(chunk<2>(bytes,  8));
    c.dig_P3 = le_s16(chunk<2>(bytes, 10));
    c.dig_P4 = le_s16(chunk<2>(bytes, 12));
    c.dig_P5 = le_s16(chunk<2>(bytes, 14));
    c.dig_P6 = le_s16(chunk<2>(bytes, 16));
    c.dig_P7 = le_s16(chunk<2>(bytes, 18));
    c.dig_P8 = le_s16(chunk<2>(bytes, 20));
    c.dig_P9 = le_s16(chunk<2>(bytes, 22));

    // dig_T1 і dig_P1 — беззнакові масштаби, нуль там фізично неможливий.
    if (c.dig_T1 == 0 || c.dig_P1 == 0) {
        return std::unexpected{Error::bad_calibration};
    }
    return c;
}

std::expected<RawSample, Error>
unpack_frame(std::span<const std::uint8_t, frame_bytes> raw) noexcept
{
    const std::span<const std::uint8_t> bytes{raw};
    const RawSample sample{
        .pressure    = unpack20(chunk<3>(bytes, 0)), // 0xF7..0xF9
        .temperature = unpack20(chunk<3>(bytes, 3))  // 0xFA..0xFC
    };

    // Скидання лишає в обох полях 0x80000: даних ще немає.
    if (sample.pressure == raw_reset_value || sample.temperature == raw_reset_value) {
        return std::unexpected{Error::no_measurement};
    }
    return sample;
}

std::int32_t Compensator::temperature(std::int32_t adc_t) noexcept
{
    // Лінійна складова: (adc_T/8 - dig_T1*2) * dig_T2 / 2048.
    const std::int32_t var1 =
        (((adc_t >> 3) - (static_cast<std::int32_t>(calib_.dig_T1) << 1)) *
         static_cast<std::int32_t>(calib_.dig_T2)) >> 11;

    // Квадратична нелінійність кристала, зважена dig_T3.
    const std::int32_t diff = (adc_t >> 4) - static_cast<std::int32_t>(calib_.dig_T1);
    const std::int32_t var2 =
        (((diff * diff) >> 12) * static_cast<std::int32_t>(calib_.dig_T3)) >> 14;

    t_fine_ = var1 + var2;

    // Соті градуса: t_fine * 5 / 256 з округленням до найближчого.
    return (t_fine_ * 5 + 128) >> 8;
}

std::expected<std::uint32_t, Error>
Compensator::pressure_q24_8(std::int32_t adc_p) const noexcept
{
    std::int64_t var1 = static_cast<std::int64_t>(t_fine_) - 128000;

    // Поліном нульового зміщення: тепловий дрейф нуля тензомоста.
    std::int64_t var2 = var1 * var1 * static_cast<std::int64_t>(calib_.dig_P6);
    var2 += (var1 * static_cast<std::int64_t>(calib_.dig_P5)) << 17;
    var2 += static_cast<std::int64_t>(calib_.dig_P4) << 35;

    // Поліном чутливості: зміна крутизни характеристики від температури.
    var1 = ((var1 * var1 * static_cast<std::int64_t>(calib_.dig_P3)) >> 8) +
           ((var1 * static_cast<std::int64_t>(calib_.dig_P2)) << 12);
    // Зсув знакового вправо тут арифметичний — так задумано в datasheet.
    var1 = ((static_cast<std::int64_t>(1) << 47) + var1) *
           static_cast<std::int64_t>(calib_.dig_P1) >> 33;

    if (var1 == 0) {
        return std::unexpected{Error::degenerate_calibration};
    }

    // Нормалізація відліку різницею з максимумом 20-бітної шкали.
    std::int64_t p = 1048576 - static_cast<std::int64_t>(adc_p);
    p = (((p << 31) - var2) * 3125) / var1;

    // Корекція нелінійності третього порядку (dig_P9, dig_P8, dig_P7).
    const std::int64_t p13 = p >> 13;
    var1 = (static_cast<std::int64_t>(calib_.dig_P9) * p13 * p13) >> 25;
    var2 = (static_cast<std::int64_t>(calib_.dig_P8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (static_cast<std::int64_t>(calib_.dig_P7) << 4);

    // Q24.8 не має знака: від'ємний тиск означає зіпсовані коефіцієнти.
    if (p < 0) {
        return std::unexpected{Error::degenerate_calibration};
    }
    return static_cast<std::uint32_t>(p);
}

std::expected<Measurement, Error> Compensator::apply(RawSample sample) noexcept
{
    // Порядок обов'язковий: тиск компенсується вже відомою t_fine.
    const std::int32_t centi = temperature(sample.temperature);
    return pressure_q24_8(sample.pressure).transform([&](std::uint32_t q24) {
        return Measurement{
            .temperature_centi_c = centi,
            .pressure_q24_8      = q24,
            .t_fine              = t_fine_
        };
    });
}

} // namespace bmp280
