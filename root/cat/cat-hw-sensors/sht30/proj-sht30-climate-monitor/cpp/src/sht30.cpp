#include "sht30.hpp"
#include <thread>
#include <chrono>
#include <algorithm>

namespace sensors {

SHT30::SHT30(I2CBus& bus, Address address)
    : bus_(bus), address_(address) {}

uint8_t SHT30::calculate_crc8(const uint8_t* data, size_t length) noexcept {
    uint8_t crc = 0xFF; // Початкове значення за специфікацією Sensirion
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = static_cast<uint8_t>((crc << 1) ^ 0x31); // Поліном x^8 + x^5 + x^4 + 1
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

uint16_t SHT30::get_measure_command(Repeatability level) const noexcept {
    switch (level) {
        case Repeatability::Low:    return CMD_MEASURE_LOW_REP;
        case Repeatability::Medium: return CMD_MEASURE_MED_REP;
        case Repeatability::High:
        default:                    return CMD_MEASURE_HIGH_REP;
    }
}

float SHT30::raw_to_temperature(uint16_t raw_t) noexcept {
    // Формула Sensirion: T = -45 + 175 * (S_T / (2^16 - 1))
    return -45.0f + 175.0f * (static_cast<float>(raw_t) / 65535.0f);
}

float SHT30::raw_to_humidity(uint16_t raw_rh) noexcept {
    // Формула Sensirion: RH = 100 * (S_RH / (2^16 - 1))
    const float rh = 100.0f * (static_cast<float>(raw_rh) / 65535.0f);
    return std::clamp(rh, 0.0f, 100.0f);
}

Sht30Data SHT30::read_measurement(Repeatability level) {
    Sht30Data result{};

    if (!bus_.set_slave_address(static_cast<uint8_t>(address_))) {
        return result;
    }

    const uint16_t cmd = get_measure_command(level);
    if (!bus_.write_command(cmd)) {
        return result;
    }

    // Затримка на вимірювання за специфікацією (High ~15ms)
    std::this_thread::sleep_for(std::chrono::milliseconds(15));

    uint8_t buffer[6] = {0};
    if (!bus_.read_bytes(buffer, 6)) {
        return result;
    }

    // Перевірка CRC-8 для температури (байти 0, 1 vs байт 2)
    const uint8_t temp_crc = calculate_crc8(&buffer[0], 2);
    if (temp_crc != buffer[2]) {
        return result; // CRC помилка
    }

    // Перевірка CRC-8 для вологості (байти 3, 4 vs байт 5)
    const uint8_t hum_crc = calculate_crc8(&buffer[3], 2);
    if (hum_crc != buffer[5]) {
        return result; // CRC помилка
    }

    const uint16_t raw_temp = static_cast<uint16_t>((buffer[0] << 8) | buffer[1]);
    const uint16_t raw_hum  = static_cast<uint16_t>((buffer[3] << 8) | buffer[4]);

    result.temperature_c = raw_to_temperature(raw_temp);
    result.humidity_percent = raw_to_humidity(raw_hum);
    result.is_valid = true;

    return result;
}

bool SHT30::set_heater(bool enable) {
    if (!bus_.set_slave_address(static_cast<uint8_t>(address_))) {
        return false;
    }
    const uint16_t cmd = enable ? CMD_HEATER_ENABLE : CMD_HEATER_DISABLE;
    return bus_.write_command(cmd);
}

bool SHT30::soft_reset() {
    if (!bus_.set_slave_address(static_cast<uint8_t>(address_))) {
        return false;
    }
    if (!bus_.write_command(CMD_SOFT_RESET)) {
        return false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(2));
    return true;
}

bool SHT30::sleep() {
    if (!bus_.set_slave_address(static_cast<uint8_t>(address_))) {
        return false;
    }
    return bus_.write_command(CMD_SLEEP);
}

} // namespace sensors
