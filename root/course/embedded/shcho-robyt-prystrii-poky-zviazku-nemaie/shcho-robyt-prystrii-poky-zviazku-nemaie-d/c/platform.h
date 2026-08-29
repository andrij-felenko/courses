#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Псевдо-залізо візка: 12 секторів Flash по 256 байтів, силовий каскад,
// лінія ENABLE із зовнішнім супервізором і радіоканал. У справжній платі це
// драйвер SPI-NOR, регістри таймера ШІМ і модем; тут — модель у пам'яті,
// щоб приклад із статті справді запускався й показував поведінку в часі.
#define FLASH_SECTOR_SIZE    256U
#define FLASH_SECTOR_COUNT    12U

// Витримка моностабільного мультивібратора на вході ENABLE. Поки прошивка
// тактує лінію частіше — ключі під напругою; зникли імпульси — каскад гасне.
#define INTERLOCK_HOLD_MS     60U

// Скільки байтів приймає черга передавача за один виклик.
#define RADIO_MTU             64U

typedef enum {
    FLASH_OK = 0,
    FLASH_ERR_RANGE,       // вихід за межі сектора
    FLASH_ERR_NOT_ERASED   // спроба писати в нестерті байти
} flash_status_t;

void plat_init(void);

uint32_t plat_now_ms(void);
void plat_advance_ms(uint32_t dt_ms);   // існує лише в настільній симуляції

// Силовий каскад
void plat_set_power_enable(bool on);
bool plat_power_enabled(void);
void plat_set_actuators(float throttle, float steering);
float plat_throttle_out(void);
float plat_steering_out(void);
void plat_set_brake(bool on);
bool plat_brake(void);

// Лінія heartbeat і сам супервізор (у залізі це окрема мікросхема)
void plat_pulse_interlock(void);
void plat_interlock_service(void);
bool plat_interlock_enabled(void);

// Периферія безпечного стану
void plat_set_beacon(bool on);
bool plat_beacon(void);
void plat_set_low_power(bool on);
bool plat_low_power(void);

// Flash
flash_status_t plat_flash_erase(uint16_t sector);
flash_status_t plat_flash_write(uint16_t sector, uint16_t offset, const void *src, uint16_t len);
flash_status_t plat_flash_read(uint16_t sector, uint16_t offset, void *dst, uint16_t len);
uint32_t plat_flash_erase_count(uint16_t sector);

// Радіо
void plat_radio_set_up(bool up);
size_t plat_radio_send(const void *data, size_t len);
uint32_t plat_radio_bytes_sent(void);

#endif /* PLATFORM_H */
