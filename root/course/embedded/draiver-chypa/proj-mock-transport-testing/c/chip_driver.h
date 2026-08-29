/* chip_driver.h — драйвер, який ми випробовуємо на комп'ютері.
 *
 * У ньому немає жодного заголовка виробника мікроконтролера: увесь доступ
 * до заліза йде через таблицю функцій chip_bus_ops_t. Саме ця дірка в дні
 * драйвера дозволяє підставити замість кремнію масив у пам'яті ПК.
 */
#ifndef CHIP_DRIVER_H
#define CHIP_DRIVER_H

#include <stdbool.h>
#include <stdint.h>

/* --- Таксономія кодів повернення ---------------------------------------- */
typedef enum {
    CHIP_OK                = 0,  /* операція завершена успішно               */
    CHIP_ERR_INVALID_PARAM = -1, /* нульовий покажчик або значення поза межами*/
    CHIP_ERR_COMM          = -2, /* апаратна помилка шини: NACK, обрив       */
    CHIP_ERR_NOT_FOUND     = -4, /* WHO_AM_I не збігся з очікуваним          */
    CHIP_ERR_NOT_INIT      = -5, /* робота з пристроєм до ініціалізації      */
    CHIP_ERR_NO_DATA       = -6  /* нового відліку ще немає (DRDY = 0)       */
} chip_status_t;

const char *chip_status_str(chip_status_t status);

/* --- Транспортна абстракція ---------------------------------------------- */
/* Контракт: 0 — успіх, будь-яке від'ємне число — апаратна помилка. Передача
 * або відбувається повністю, або не відбувається зовсім: часткове читання
 * драйвер зобов'язаний вважати збоєм і не використовувати буфер. */
typedef int32_t (*chip_bus_read_fn)(void *user_ctx, uint8_t dev_addr,
                                    uint8_t reg, uint8_t *data, uint16_t len);

typedef int32_t (*chip_bus_write_fn)(void *user_ctx, uint8_t dev_addr,
                                     uint8_t reg, const uint8_t *data, uint16_t len);

typedef void (*chip_delay_ms_fn)(uint32_t ms);

typedef struct {
    chip_bus_read_fn  read;
    chip_bus_write_fn write;
    chip_delay_ms_fn  delay_ms; /* може бути NULL: тоді пауз між спробами нема*/
} chip_bus_ops_t;

/* --- Дескриптор пристрою -------------------------------------------------- */
typedef struct {
    const chip_bus_ops_t *bus_ops;
    void                 *user_ctx;
    uint8_t               dev_addr;

    uint8_t  max_retries;    /* скільки разів повторити збиту транзакцію     */
    uint32_t retry_delay_ms; /* базова пауза; далі подвоюється               */

    uint8_t  active_range;   /* 2, 4, 8 або 16 g                             */
    float    scale_factor;   /* м/с² на один відлік для поточного діапазону  */

    uint8_t  shadow_ctrl1;   /* тіньові копії конфігураційних регістрів      */
    uint8_t  shadow_ctrl4;
    bool     is_initialized;
} chip_dev_t;

typedef struct {
    float x; /* м/с² */
    float y;
    float z;
} chip_axes_data_si_t;

/* --- Публічний контракт --------------------------------------------------- */
chip_status_t chip_init(chip_dev_t *dev, const chip_bus_ops_t *bus_ops,
                        void *user_ctx, uint8_t dev_addr);
chip_status_t chip_set_range(chip_dev_t *dev, uint8_t range_g);
chip_status_t chip_read_sample_si(chip_dev_t *dev, chip_axes_data_si_t *data_si);
chip_status_t chip_soft_reset(chip_dev_t *dev);

#endif /* CHIP_DRIVER_H */
