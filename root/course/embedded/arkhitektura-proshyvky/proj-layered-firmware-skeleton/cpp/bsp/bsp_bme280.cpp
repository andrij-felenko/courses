// bsp/bsp_bme280.cpp — уся внутрішня кухня давача: адреси регістрів, карта
// калібрування й формули компенсації Bosch. Назовні не видно жодного числа.
#include "bsp/bsp_bme280.hpp"

#include <array>
#include <span>
#include <utility>

namespace bsp {
namespace {

// --- Карта регістрів мікросхеми ------------------------------------------------
constexpr std::uint8_t kRegCalibTp = 0x88;  // dig_T1..dig_T3, dig_P1..dig_P9 — 24 байти
constexpr std::uint8_t kRegCalibH1 = 0xA1;
constexpr std::uint8_t kRegChipId = 0xD0;
constexpr std::uint8_t kRegCalibH = 0xE1;  // dig_H2..dig_H6 — 7 байтів
constexpr std::uint8_t kRegCtrlHum = 0xF2;
constexpr std::uint8_t kRegStatus = 0xF3;
constexpr std::uint8_t kRegCtrlMeas = 0xF4;
constexpr std::uint8_t kRegConfig = 0xF5;
constexpr std::uint8_t kRegData = 0xF7;  // press msb .. hum lsb — 8 байтів поспіль

constexpr std::uint8_t kChipIdBme280 = 0x60;
constexpr std::uint8_t kCtrlHumOsrsX1 = 0x01;
// osrs_t = x1 (001), osrs_p = x1 (001), режим normal (11)
constexpr std::uint8_t kCtrlMeasNormalX1 = (1U << 5) | (1U << 2) | 0x03U;
constexpr std::uint8_t kConfigStandby1s = 0xA0;  // t_sb = 1000 мс, фільтр вимкнено

constexpr std::uint8_t kStatusMeasuring = 0x08;
constexpr std::uint8_t kStatusImUpdate = 0x01;
constexpr unsigned kStatusPollAttempts = 512;

// Значення, яким чип позначає «вибірки ще не було».
constexpr std::int32_t kAdcTpUnset = 0x80000;
constexpr std::int32_t kAdcHUnset = 0x8000;

constexpr std::uint16_t le_u16(std::span<const std::uint8_t> b, std::size_t at)
{
    return static_cast<std::uint16_t>(static_cast<std::uint16_t>(b[at + 1]) << 8 | b[at]);
}

constexpr std::int16_t le_i16(std::span<const std::uint8_t> b, std::size_t at)
{
    return static_cast<std::int16_t>(le_u16(b, at));
}

}  // namespace

std::expected<void, Bme280Error> Bme280::load_calibration()
{
    std::array<std::uint8_t, 24> tp{};
    if (auto res = bus_.read_reg(address_, kRegCalibTp, tp); !res) {
        last_bus_error_ = res.error();
        return std::unexpected(Bme280Error::Bus);
    }

    calib_.t1 = le_u16(tp, 0);
    calib_.t2 = le_i16(tp, 2);
    calib_.t3 = le_i16(tp, 4);
    calib_.p1 = le_u16(tp, 6);
    calib_.p2 = le_i16(tp, 8);
    calib_.p3 = le_i16(tp, 10);
    calib_.p4 = le_i16(tp, 12);
    calib_.p5 = le_i16(tp, 14);
    calib_.p6 = le_i16(tp, 16);
    calib_.p7 = le_i16(tp, 18);
    calib_.p8 = le_i16(tp, 20);
    calib_.p9 = le_i16(tp, 22);

    std::array<std::uint8_t, 1> h1{};
    if (auto res = bus_.read_reg(address_, kRegCalibH1, h1); !res) {
        last_bus_error_ = res.error();
        return std::unexpected(Bme280Error::Bus);
    }
    calib_.h1 = h1[0];

    std::array<std::uint8_t, 7> h{};
    if (auto res = bus_.read_reg(address_, kRegCalibH, h); !res) {
        last_bus_error_ = res.error();
        return std::unexpected(Bme280Error::Bus);
    }

    calib_.h2 = le_i16(h, 0);
    calib_.h3 = h[2];
    // dig_H4 і dig_H5 ділять півбайти регістра 0xE5 — саме тому калібрування
    // вологості не читається одним акуратним масивом.
    calib_.h4 = static_cast<std::int16_t>((static_cast<std::int16_t>(static_cast<std::int8_t>(h[3]))
                                           << 4) |
                                          static_cast<std::int16_t>(h[4] & 0x0FU));
    calib_.h5 = static_cast<std::int16_t>((static_cast<std::int16_t>(static_cast<std::int8_t>(h[5]))
                                           << 4) |
                                          static_cast<std::int16_t>(h[4] >> 4));
    calib_.h6 = static_cast<std::int8_t>(h[6]);

    // p1 == 0 означає порожню сторінку: з таким коефіцієнтом формула тиску
    // ділить на нуль.
    if (calib_.t1 == 0 || calib_.p1 == 0) {
        return std::unexpected(Bme280Error::BadCalibration);
    }
    return {};
}

std::expected<void, Bme280Error> Bme280::configure_chip()
{
    // ctrl_hum набирає чинності лише після запису ctrl_meas — порядок обовʼязковий.
    for (const auto [reg, value] : std::array<std::pair<std::uint8_t, std::uint8_t>, 3>{
             {{kRegCtrlHum, kCtrlHumOsrsX1},
              {kRegConfig, kConfigStandby1s},
              {kRegCtrlMeas, kCtrlMeasNormalX1}}}) {
        if (auto res = bus_.write_u8(address_, reg, value); !res) {
            last_bus_error_ = res.error();
            return std::unexpected(Bme280Error::Bus);
        }
    }

    // Чекаємо, доки чип перенесе калібрування з NVM і завершить першу вибірку.
    for (unsigned attempt = 0; attempt < kStatusPollAttempts; ++attempt) {
        std::array<std::uint8_t, 1> status{};
        if (auto res = bus_.read_reg(address_, kRegStatus, status); !res) {
            last_bus_error_ = res.error();
            return std::unexpected(Bme280Error::Bus);
        }
        if ((status[0] & (kStatusMeasuring | kStatusImUpdate)) == 0U) {
            return {};
        }
    }
    return std::unexpected(Bme280Error::NotReady);
}

std::expected<void, Bme280Error> Bme280::initialize()
{
    std::array<std::uint8_t, 1> chip_id{};
    if (auto res = bus_.read_reg(address_, kRegChipId, chip_id); !res) {
        last_bus_error_ = res.error();
        return std::unexpected(Bme280Error::Bus);
    }
    if (chip_id[0] != kChipIdBme280) {
        // Відповів хтось інший (BMP280 віддає 0x58). Мовчки рахувати його дані
        // за наші не можна: карта калібрування в них різна.
        return std::unexpected(Bme280Error::WrongChipId);
    }

    if (auto res = load_calibration(); !res) {
        return res;
    }
    return configure_chip();
}

// --- Компенсація за формулами Bosch у рухомій комі ---------------------------------
float Bme280::compensate_temperature(std::int32_t adc_t)
{
    const float t = static_cast<float>(adc_t);
    const float var1 = (t / 16384.0F - static_cast<float>(calib_.t1) / 1024.0F) *
                       static_cast<float>(calib_.t2);
    const float d = t / 131072.0F - static_cast<float>(calib_.t1) / 8192.0F;
    const float var2 = d * d * static_cast<float>(calib_.t3);
    t_fine_ = var1 + var2;
    return t_fine_ / 5120.0F;
}

float Bme280::compensate_pressure(std::int32_t adc_p) const
{
    float var1 = t_fine_ / 2.0F - 64000.0F;
    float var2 = var1 * var1 * static_cast<float>(calib_.p6) / 32768.0F;
    var2 = var2 + var1 * static_cast<float>(calib_.p5) * 2.0F;
    var2 = var2 / 4.0F + static_cast<float>(calib_.p4) * 65536.0F;
    var1 = (static_cast<float>(calib_.p3) * var1 * var1 / 524288.0F +
            static_cast<float>(calib_.p2) * var1) /
           524288.0F;
    var1 = (1.0F + var1 / 32768.0F) * static_cast<float>(calib_.p1);
    if (var1 == 0.0F) {
        return 0.0F;  // Ділення на нуль при негодящому калібруванні
    }

    float p = 1048576.0F - static_cast<float>(adc_p);
    p = (p - var2 / 4096.0F) * 6250.0F / var1;
    var1 = static_cast<float>(calib_.p9) * p * p / 2147483648.0F;
    var2 = p * static_cast<float>(calib_.p8) / 32768.0F;
    p = p + (var1 + var2 + static_cast<float>(calib_.p7)) / 16.0F;
    return p / 100.0F;  // Па → гПа
}

float Bme280::compensate_humidity(std::int32_t adc_h) const
{
    float h = t_fine_ - 76800.0F;
    h = (static_cast<float>(adc_h) -
         (static_cast<float>(calib_.h4) * 64.0F + static_cast<float>(calib_.h5) / 16384.0F * h)) *
        (static_cast<float>(calib_.h2) / 65536.0F *
         (1.0F + static_cast<float>(calib_.h6) / 67108864.0F * h *
                     (1.0F + static_cast<float>(calib_.h3) / 67108864.0F * h)));
    h = h * (1.0F - static_cast<float>(calib_.h1) * h / 524288.0F);

    if (h > 100.0F) return 100.0F;
    if (h < 0.0F) return 0.0F;
    return h;
}

std::optional<SensorReading> Bme280::read()
{
    std::array<std::uint8_t, 8> raw{};
    if (auto res = bus_.read_reg(address_, kRegData, raw); !res) {
        last_bus_error_ = res.error();
        // Шар BSP не рахує математику за сміттєвими байтами буфера.
        return std::nullopt;
    }
    last_bus_error_.reset();

    const auto adc_p = static_cast<std::int32_t>(
        (static_cast<std::uint32_t>(raw[0]) << 12) | (static_cast<std::uint32_t>(raw[1]) << 4) |
        (static_cast<std::uint32_t>(raw[2]) >> 4));
    const auto adc_t = static_cast<std::int32_t>(
        (static_cast<std::uint32_t>(raw[3]) << 12) | (static_cast<std::uint32_t>(raw[4]) << 4) |
        (static_cast<std::uint32_t>(raw[5]) >> 4));
    const auto adc_h = static_cast<std::int32_t>((static_cast<std::uint32_t>(raw[6]) << 8) |
                                                 static_cast<std::uint32_t>(raw[7]));

    if (adc_t == kAdcTpUnset) {
        return std::nullopt;  // Чип у режимі сну або ще не зробив вибірки
    }

    SensorReading reading{};
    reading.temperature_c = compensate_temperature(adc_t);
    reading.pressure_hpa = (adc_p == kAdcTpUnset) ? 0.0F : compensate_pressure(adc_p);
    reading.humidity_percent = (adc_h == kAdcHUnset) ? 0.0F : compensate_humidity(adc_h);
    return reading;
}

}  // namespace bsp
