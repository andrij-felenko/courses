#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define HIL_SYNC0 0xB5u          // маркер початку — як преамбула u-blox UBX
#define HIL_SYNC1 0x62u
#define HIL_N_MOTORS 4

// Вимір IMU — той самий тип, що логіка керування читає через imu_read().
typedef struct {
    float roll, pitch, yaw;   // кути, рад
    float ax, ay, az;         // прискорення, м/с²
    uint32_t t_us;            // мітка часу виміру (дублює кадрову — див. нижче)
} imu_sample_t;

// КАДР ДАВАЧІВ: модель → плата. Рівно один такий кадр = рівно один крок.
typedef struct __attribute__((packed)) {
    uint8_t  sync0, sync1;    // 0xB5 0x62 — знайти початок у потоці
    uint16_t seq;             // лічильник кадрів — ловить втрату/дубль
    uint32_t t_us;            // МОДЕЛЬНИЙ час цього такту — стане now_us()
    float    roll, pitch, yaw;
    float    ax, ay, az;      // 6×float = IMU-вимір
    double   lat, lon;        // координати від «GPS» моделі (8 Б)
    uint16_t crc;             // CRC-16 усього, що вище
} hil_sensors_t;              // разом 42 байти

// КАДР АКТУАТОРІВ: плата → модель. Ехо seq/t_us каже, на що це відповідь.
typedef struct __attribute__((packed)) {
    uint8_t  sync0, sync1;
    uint16_t seq;             // ЕХО seq того виміру, що обробили
    uint32_t t_us;            // ЕХО модельного часу
    float    thr[HIL_N_MOTORS]; // тяга 0..1 на кожен мотор
    uint16_t crc;
} hil_actuators_t;            // разом 26 байтів
