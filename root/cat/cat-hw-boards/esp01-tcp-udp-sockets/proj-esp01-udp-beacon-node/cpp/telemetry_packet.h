#ifndef TELEMETRY_PACKET_H
#define TELEMETRY_PACKET_H

#include <Arduino.h>
#include <cstdint>
#include <cstddef>

// Магічний заголовок для ідентифікації телеметричних пакетів ESP-01
constexpr uint16_t TELEMETRY_MAGIC = 0x4550; // "EP"

#pragma pack(push, 1)
// Упакована структура бінарного кадру телеметрії (без вирівнювання полів компілятором)
struct TelemetryPacket {
    uint16_t magic;          // Магічна мітка кадру (0x4550)
    uint32_t sequence;       // Порядковий номер пакета
    uint32_t uptime_ms;      // Uptime пристрою у мілісекундах
    int16_t  temperature;    // Температура (фіксована крапка: значення * 100)
    uint16_t humidity;       // Відносна вологість (значення * 100)
    uint16_t crc16;          // Контрольна сума CRC-16 (покриває всі попередні поля)

    // Обчислення контрольної суми CRC16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
    static uint16_t calculateCRC16(const uint8_t* data, size_t length) {
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < length; ++i) {
            crc ^= (static_cast<uint16_t>(data[i]) << 8);
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

    // Заповнення контрольної суми перед відправкою пакета
    void finalize() {
        magic = TELEMETRY_MAGIC;
        size_t payload_size = sizeof(TelemetryPacket) - sizeof(crc16);
        crc16 = calculateCRC16(reinterpret_cast<const uint8_t*>(this), payload_size);
    }

    // Перевірка цілісності отриманого пакета
    bool isValid() const {
        if (magic != TELEMETRY_MAGIC) {
            return false;
        }
        size_t payload_size = sizeof(TelemetryPacket) - sizeof(crc16);
        uint16_t expected_crc = calculateCRC16(reinterpret_cast<const uint8_t*>(this), payload_size);
        return (crc16 == expected_crc);
    }
};
#pragma pack(pop)

#endif // TELEMETRY_PACKET_H
