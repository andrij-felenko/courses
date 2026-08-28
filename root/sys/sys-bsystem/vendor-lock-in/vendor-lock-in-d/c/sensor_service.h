/* inc/sensor_service.h — Приклад ізольованого драйвера мовою C */
#ifndef SENSOR_SERVICE_H
#define SENSOR_SERVICE_H

#include <stdint.h>
#include <stdbool.h>

/* Використовуємо уніфікований макрос упакування структур замість вендорних прагм */
#if defined(__GNUC__) || defined(__clang__)
    #define PORT_PACKED struct __attribute__((packed))
    #define PORT_RAM_SECTION __attribute__((section(".ramfunc"), noinline))
#elif defined(__ICCARM__)
    #define PORT_PACKED __packed struct
    #define PORT_RAM_SECTION __ramfunc
#else
    #define PORT_PACKED struct
    #define PORT_RAM_SECTION
#endif

PORT_PACKED SensorDataPacket {
    uint32_t timestamp_ms;
    int16_t  temperature_raw;
    uint16_t crc16;
};

/* Абстрактний інтерфейс апаратного порту передачі даних (контракт) */
typedef struct {
    bool (*write_bytes)(const uint8_t *data, uint16_t length);
    void (*delay_ms)(uint32_t ms);
} I2CBusPort;

/* Функція сервісу: не містить жодного виклику регістрів конкретного МК */
PORT_RAM_SECTION
bool sensor_service_read_packet(const I2CBusPort *bus, struct SensorDataPacket *out_packet);

#endif /* SENSOR_SERVICE_H */
