/*
 * Таксономія статусів драйвера.
 *
 * Нуль — успіх, усе інше відʼємне: перевірка `if (st != CHIP_STATUS_OK)`
 * читається однаково для будь-якої функції, а `int` як код повернення
 * заборонено — тип каже читачеві, що саме він тримає в руках.
 */
#ifndef CHIP_STATUS_H
#define CHIP_STATUS_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CHIP_STATUS_OK               =  0,  /* Операція успішно завершена */
    CHIP_ERR_INVALID_PARAM       = -1,  /* NULL-вказівник або значення поза діапазоном */
    CHIP_ERR_COMM_FAIL           = -2,  /* NACK, втрата арбітражу, зависла шина */
    CHIP_ERR_TIMEOUT             = -3,  /* Вичерпано очікування готовності або зняття скидання */
    CHIP_ERR_DEVICE_NOT_FOUND    = -4,  /* WHO_AM_I містить неочікуваний ідентифікатор */
    CHIP_ERR_NOT_INITIALIZED     = -5,  /* Виклик прикладної функції до chip_init() */
    CHIP_ERR_DATA_NOT_READY      = -6,  /* Нова вибірка ще не готова (ZYXDA скинутий) */
    CHIP_ERR_SELF_TEST_FAILED    = -7,  /* Вбудований самотест вийшов за паспортне вікно */
    CHIP_ERR_CALIBRATION_INVALID = -8   /* Коефіцієнти підстроювання з NVM не піднялися */
} chip_status_t;

/* Коротка назва статусу для журналу. Таблиця всередині — const-дані в .rodata,
 * а не змінний стан: реентерабельності це не порушує. */
const char *chip_status_str(chip_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* CHIP_STATUS_H */
