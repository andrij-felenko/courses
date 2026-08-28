/* Обслуговування шини I2C: відновлення ліній та сканування адрес */
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* Визначення абстрактного апаратного інтерфейсу GPIO для відновлення */
typedef struct {
    void (*set_scl_output)(void);
    void (*set_scl_level)(bool high);
    bool (*read_sda_level)(void);
    void (*set_sda_output)(void);
    void (*set_sda_level)(bool high);
    void (*restore_i2c_peripheral)(void);
    void (*delay_us)(uint32_t us);
} i2c_bus_recovery_io_t;

/* Процедура апаратного виведення веденого чіпа із затиснутого стану SDA */
bool i2c_recover_bus(const i2c_bus_recovery_io_t *io) {
    /* 1. Якщо SDA висока — шина вільна, скидання не потрібне */
    if (io->read_sda_level()) {
        return true;
    }

    /* 2. Переводимо SCL у режим GPIO виходу, SDA залишається входом */
    io->set_scl_output();
    io->set_scl_level(true);
    io->delay_us(5);

    /* 3. Тактуємо лінію SCL до 9 разів, очікуючи відпускання SDA */
    bool sda_released = false;
    for (uint8_t i = 0; i < 9; ++i) {
        io->set_scl_level(false);
        io->delay_us(5);
        io->set_scl_level(true);
        io->delay_us(5);

        if (io->read_sda_level()) {
            sda_released = true;
            break;
        }
    }

    /* Якщо ведений не відпустив лінію навіть після 9 тактів — апаратне КЗ або дефект */
    if (!sda_released) {
        io->restore_i2c_peripheral();
        return false;
    }

    /* 4. Формуємо примусову умову STOP: перехід SDA з 0 в 1 при SCL = 1 */
    io->set_sda_output();
    io->set_sda_level(false);
    io->delay_us(5);
    io->set_scl_level(true);
    io->delay_us(5);
    io->set_sda_level(true);
    io->delay_us(5);

    /* 5. Повертаємо виводи під контроль апаратного I2C блоку */
    io->restore_i2c_peripheral();
    return true;
}

/* Структура звіту сканування */
typedef struct {
    uint8_t addresses[112];
    uint8_t count;
} i2c_scan_result_t;

/* Тип функції перевірки адреси апаратним периферійним драйвером */
typedef bool (*i2c_ping_fn_t)(uint8_t addr_7bit, uint32_t timeout_ms);

/* Запуск повного циклу опитування простору адрес */
i2c_scan_result_t i2c_scan_bus(i2c_ping_fn_t ping_fn, uint32_t timeout_ms) {
    i2c_scan_result_t result = {.count = 0};

    printf("Початок сканування шини I2C (діапазон 0x08..0x77)...\r\n");

    for (uint8_t addr = 0x08; addr <= 0x77; ++addr) {
        if (ping_fn(addr, timeout_ms)) {
            result.addresses[result.count++] = addr;
            printf(" -> Знайдено пристрій за 7-бітною адресою: 0x%02X (8-бітний запис: 0x%02X)\r\n",
                   addr, (uint8_t)(addr << 1));
        }
    }

    printf("Сканування завершено. Знайдено пристроїв: %u\r\n", result.count);
    return result;
}
