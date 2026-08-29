#include <algorithm>
#include <array>

#include "sensors.hpp"

namespace node {
namespace {

constexpr std::uint8_t kRegId       = 0xD0;
constexpr std::uint8_t kRegReset    = 0xE0;
constexpr std::uint8_t kRegCtrlHum  = 0xF2;
constexpr std::uint8_t kRegStatus   = 0xF3;
constexpr std::uint8_t kRegCtrlMeas = 0xF4;
constexpr std::uint8_t kRegConfig   = 0xF5;
constexpr std::uint8_t kRegData     = 0xF7;

constexpr std::uint8_t kDsRegSeconds = 0x00;
constexpr std::uint8_t kDsRegControl = 0x0E;
constexpr std::uint8_t kDsRegStatus  = 0x0F;

constexpr std::uint16_t u16(std::byte lo, std::byte hi) noexcept {
    return static_cast<std::uint16_t>(static_cast<std::uint16_t>(lo) |
                                      (static_cast<std::uint16_t>(hi) << 8));
}
constexpr std::int16_t i16(std::byte lo, std::byte hi) noexcept {
    return static_cast<std::int16_t>(u16(lo, hi));
}
constexpr std::uint8_t u8(std::byte b) noexcept { return static_cast<std::uint8_t>(b); }

constexpr std::uint8_t bcdToBin(std::uint8_t bcd) noexcept {
    return static_cast<std::uint8_t>((bcd >> 4) * 10u + (bcd & 0x0Fu));
}

// Дні від 1970-01-01 — алгоритм Говарда Гіннанта, без таблиць і циклів.
constexpr std::uint32_t daysFromCivil(std::uint32_t y, std::uint32_t m, std::uint32_t d) noexcept {
    y -= (m <= 2u) ? 1u : 0u;
    const std::uint32_t era = y / 400u;
    const std::uint32_t yoe = y - era * 400u;
    const std::uint32_t doy = (153u * (m + (m > 2u ? -3u : 9u)) + 2u) / 5u + d - 1u;
    const std::uint32_t doe = yoe * 365u + yoe / 4u - yoe / 100u + doy;
    return era * 146'097u + doe - 719'468u;
}

}  // namespace

// ══ BME280 ═══════════════════════════════════════════════════════════════

SensorResult<void> Bme280::loadCalibration() noexcept {
    std::array<std::byte, 26> a{};
    std::array<std::byte, 7>  b{};

    if (!bus_.readRegisters(kAddress, 0x88, a)) return std::unexpected{SensorError::Bus};
    if (!bus_.readRegisters(kAddress, 0xE1, b)) return std::unexpected{SensorError::Bus};

    cal_.t1 = u16(a[0], a[1]);   cal_.t2 = i16(a[2], a[3]);   cal_.t3 = i16(a[4], a[5]);
    cal_.p1 = u16(a[6], a[7]);   cal_.p2 = i16(a[8], a[9]);   cal_.p3 = i16(a[10], a[11]);
    cal_.p4 = i16(a[12], a[13]); cal_.p5 = i16(a[14], a[15]); cal_.p6 = i16(a[16], a[17]);
    cal_.p7 = i16(a[18], a[19]); cal_.p8 = i16(a[20], a[21]); cal_.p9 = i16(a[22], a[23]);
    cal_.h1 = u8(a[25]);   // a[24] — резерв, dig_H1 лежить за адресою 0xA1

    cal_.h2 = i16(b[0], b[1]);
    cal_.h3 = u8(b[2]);
    // H4 і H5 упаковані в півбайти навколо 0xE5 — класична пастка датчика.
    cal_.h4 = static_cast<std::int16_t>((static_cast<std::int16_t>(static_cast<std::int8_t>(u8(b[3]))) << 4) |
                                        (u8(b[4]) & 0x0Fu));
    cal_.h5 = static_cast<std::int16_t>((static_cast<std::int16_t>(static_cast<std::int8_t>(u8(b[5]))) << 4) |
                                        (u8(b[4]) >> 4));
    cal_.h6 = static_cast<std::int8_t>(u8(b[6]));

    calibrated_ = true;
    return {};
}

SensorResult<void> Bme280::begin() noexcept {
    calibrated_ = false;

    std::array<std::byte, 1> id{};
    if (!bus_.readRegisters(kAddress, kRegId, id)) {
        // Найімовірніша причина мовчання — зависла шина після скидання ядра.
        bus_.recoverBus();
        if (!bus_.readRegisters(kAddress, kRegId, id)) {
            return std::unexpected{SensorError::Bus};
        }
    }
    if (u8(id[0]) != 0x60) return std::unexpected{SensorError::WrongId};

    if (!bus_.writeRegister(kAddress, kRegReset, 0xB6)) return std::unexpected{SensorError::Bus};

    // Копіювання NVM після скидання — 2 мс за паспортом.
    const std::uint32_t started = mcu::time::millis();
    while (!mcu::time::elapsed(started, 3)) { }

    if (auto cal = loadCalibration(); !cal) return cal;

    if (!bus_.writeRegister(kAddress, kRegCtrlHum, 0x01)) return std::unexpected{SensorError::Bus};
    if (!bus_.writeRegister(kAddress, kRegConfig, 0x00))  return std::unexpected{SensorError::Bus};
    return {};
}

SensorResult<void> Bme280::startMeasurement() noexcept {
    if (!calibrated_) return std::unexpected{SensorError::NotCalibrated};

    if (!bus_.writeRegister(kAddress, kRegCtrlHum, 0x01)) return std::unexpected{SensorError::Bus};
    // osrs_t = ×1, osrs_p = ×1, режим forced: одне вимірювання й знову сон.
    if (!bus_.writeRegister(kAddress, kRegCtrlMeas, 0x25)) return std::unexpected{SensorError::Bus};
    return {};
}

SensorResult<bool> Bme280::ready() noexcept {
    std::array<std::byte, 1> status{};

    if (!bus_.readRegisters(kAddress, kRegStatus, status)) {
        return std::unexpected{SensorError::Bus};
    }
    return (u8(status[0]) & 0x08u) == 0u;   // measuring == 0
}

// Компенсація за паспортом Bosch — цілочислова, без плаваючої крапки.
std::int32_t Bme280::compensateTemperature(std::int32_t adc) noexcept {
    const std::int32_t v1 = ((((adc >> 3) - (static_cast<std::int32_t>(cal_.t1) << 1))) *
                             static_cast<std::int32_t>(cal_.t2)) >> 11;
    const std::int32_t d  = (adc >> 4) - static_cast<std::int32_t>(cal_.t1);
    const std::int32_t v2 = (((d * d) >> 12) * static_cast<std::int32_t>(cal_.t3)) >> 14;

    tFine_ = v1 + v2;
    return (tFine_ * 5 + 128) >> 8;
}

std::uint32_t Bme280::compensatePressure(std::int32_t adc) const noexcept {
    std::int64_t v1 = static_cast<std::int64_t>(tFine_) - 128'000;
    std::int64_t v2 = v1 * v1 * static_cast<std::int64_t>(cal_.p6);

    v2 += (v1 * static_cast<std::int64_t>(cal_.p5)) << 17;
    v2 += static_cast<std::int64_t>(cal_.p4) << 35;
    v1 = ((v1 * v1 * static_cast<std::int64_t>(cal_.p3)) >> 8) +
         ((v1 * static_cast<std::int64_t>(cal_.p2)) << 12);
    v1 = (((static_cast<std::int64_t>(1) << 47) + v1) * static_cast<std::int64_t>(cal_.p1)) >> 33;

    if (v1 == 0) return 0;   // ділення на нуль при битій калібровці

    std::int64_t p = 1'048'576 - adc;
    p = (((p << 31) - v2) * 3125) / v1;
    v1 = (static_cast<std::int64_t>(cal_.p9) * (p >> 13) * (p >> 13)) >> 25;
    v2 = (static_cast<std::int64_t>(cal_.p8) * p) >> 19;
    p = ((p + v1 + v2) >> 8) + (static_cast<std::int64_t>(cal_.p7) << 4);   // Па у Q24.8

    if (p <= 0) return 0;
    return static_cast<std::uint32_t>((static_cast<std::uint64_t>(p) * 100u) >> 8);
}

std::uint32_t Bme280::compensateHumidity(std::int32_t adc) const noexcept {
    std::int32_t v = tFine_ - 76'800;

    v = ((((adc << 14) - (static_cast<std::int32_t>(cal_.h4) << 20) -
           (static_cast<std::int32_t>(cal_.h5) * v)) + 16'384) >> 15) *
        (((((((v * static_cast<std::int32_t>(cal_.h6)) >> 10) *
             (((v * static_cast<std::int32_t>(cal_.h3)) >> 11) + 32'768)) >> 10) + 2'097'152) *
             static_cast<std::int32_t>(cal_.h2) + 8'192) >> 14);
    v -= (((((v >> 15) * (v >> 15)) >> 7) * static_cast<std::int32_t>(cal_.h1)) >> 4);
    v = std::clamp(v, 0, 419'430'400);

    return static_cast<std::uint32_t>(v >> 12);   // %RH × 1024
}

SensorResult<Bme280::Sample> Bme280::read() noexcept {
    if (!calibrated_) return std::unexpected{SensorError::NotCalibrated};

    std::array<std::byte, 8> d{};
    if (!bus_.readRegisters(kAddress, kRegData, d)) return std::unexpected{SensorError::Bus};

    const std::int32_t adcP = (static_cast<std::int32_t>(u8(d[0])) << 12) |
                              (static_cast<std::int32_t>(u8(d[1])) << 4) | (u8(d[2]) >> 4);
    const std::int32_t adcT = (static_cast<std::int32_t>(u8(d[3])) << 12) |
                              (static_cast<std::int32_t>(u8(d[4])) << 4) | (u8(d[5]) >> 4);
    const std::int32_t adcH = (static_cast<std::int32_t>(u8(d[6])) << 8) |
                               static_cast<std::int32_t>(u8(d[7]));

    // 0x80000 і 0x8000 — значення після скидання: вимірювання не відбулося
    // або АЦП пішов за межу. Такі відліки в журнал не пускаємо.
    if (adcT == 0x80000 || adcP == 0x80000 || adcH == 0x8000) {
        return std::unexpected{SensorError::AdcInvalid};
    }

    Sample s{};
    s.temperatureC100 = compensateTemperature(adcT);   // спершу T: дає t_fine
    s.pressurePa100   = compensatePressure(adcP);
    s.humidityRh1024  = compensateHumidity(adcH);

    if (s.pressurePa100 == 0u) return std::unexpected{SensorError::AdcInvalid};
    return s;
}

// ══ DS3231 ═══════════════════════════════════════════════════════════════

SensorResult<void> Ds3231::begin() noexcept {
    std::array<std::byte, 1> ctl{};

    if (!bus_.readRegisters(kAddress, kDsRegControl, ctl)) {
        bus_.recoverBus();
        if (!bus_.readRegisters(kAddress, kDsRegControl, ctl)) {
            return std::unexpected{SensorError::Bus};
        }
    }

    // INTCN = 0 і RS2:RS1 = 00 → на виводі INT/SQW меандр 1 Гц. Саме цей
    // фронт будить ядро зі Stop 2: власний таймер вузлові не потрібен.
    std::uint8_t value = u8(ctl[0]);
    value &= static_cast<std::uint8_t>(~0x1Cu);   // INTCN, RS2, RS1
    value &= static_cast<std::uint8_t>(~0x80u);   // EOSC = 0, генератор іде й від батареї
    if (!bus_.writeRegister(kAddress, kDsRegControl, value)) {
        return std::unexpected{SensorError::Bus};
    }

    // Вихід 32 кГц вимикаємо — зайві мікроампери з резервної батареї.
    std::array<std::byte, 1> sts{};
    if (!bus_.readRegisters(kAddress, kDsRegStatus, sts)) return std::unexpected{SensorError::Bus};
    if (!bus_.writeRegister(kAddress, kDsRegStatus,
                            static_cast<std::uint8_t>(u8(sts[0]) & ~0x08u))) {
        return std::unexpected{SensorError::Bus};
    }
    return {};
}

SensorResult<Ds3231::Time> Ds3231::now() noexcept {
    std::array<std::byte, 7> r{};
    std::array<std::byte, 1> sts{};

    if (!bus_.readRegisters(kAddress, kDsRegSeconds, r)) return std::unexpected{SensorError::Bus};
    if (!bus_.readRegisters(kAddress, kDsRegStatus, sts)) return std::unexpected{SensorError::Bus};

    const std::uint32_t sec  = bcdToBin(u8(r[0]) & 0x7Fu);
    const std::uint32_t min  = bcdToBin(u8(r[1]) & 0x7Fu);
    const std::uint32_t hour = bcdToBin(u8(r[2]) & 0x3Fu);   // 24-годинний формат
    const std::uint32_t day  = bcdToBin(u8(r[4]) & 0x3Fu);
    const std::uint32_t mon  = bcdToBin(u8(r[5]) & 0x1Fu);
    const std::uint32_t year = 2000u + bcdToBin(u8(r[6])) + ((u8(r[5]) & 0x80u) ? 100u : 0u);

    if (sec > 59u || min > 59u || hour > 23u || day == 0u || day > 31u || mon == 0u || mon > 12u) {
        return std::unexpected{SensorError::BadTime};
    }

    Time t{};
    t.unix = daysFromCivil(year, mon, day) * 86'400u + hour * 3600u + min * 60u + sec;

    // OSF: генератор колись зупинявся — часу в чипі віри немає. Прапорець
    // скидаємо, щоб наступний запис показав уже відновлену синхронність.
    t.oscillatorValid = (u8(sts[0]) & 0x80u) == 0u;
    if (!t.oscillatorValid) {
        (void)bus_.writeRegister(kAddress, kDsRegStatus,
                                 static_cast<std::uint8_t>(u8(sts[0]) & ~0x80u));
    }
    return t;
}

}  // namespace node
