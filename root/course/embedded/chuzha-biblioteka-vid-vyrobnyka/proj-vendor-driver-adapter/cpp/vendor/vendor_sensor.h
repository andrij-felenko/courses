/*
 * Офіційний драйвер виробника комбінованого давача тиску й температури.
 * Файл приїхав у постачанні SDK і НЕ редагується: будь-яка правка тут
 * загине під час наступного оновлення бібліотеки.
 *
 * Контракт типовий для цього класу SDK (Bosch Sensor API, ST MEMS drivers):
 * драйвер нічого не знає про платформу й ходить до чипа виключно через
 * три колбеки, які прошивка кладе в дескриптор пристрою.
 */
#ifndef VENDOR_SENSOR_H
#define VENDOR_SENSOR_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define VENDOR_OK               0
#define VENDOR_E_NULL_PTR     (-1)
#define VENDOR_E_COMM_FAIL    (-2)
#define VENDOR_E_DEV_NOT_FOUND (-3)
#define VENDOR_E_CALIB        (-4)

/* Ідентифікатори кремнію, які підтримує ця версія драйвера. */
#define VENDOR_CHIP_ID_BMP280 0x58U
#define VENDOR_CHIP_ID_BME280 0x60U

/* Режими роботи перетворювача. */
#define VENDOR_MODE_SLEEP  0x00U
#define VENDOR_MODE_FORCED 0x01U
#define VENDOR_MODE_NORMAL 0x03U

/* Колбеки платформи. Останній аргумент intf_ptr драйвер повертає незміненим —
   через нього прошивка впізнає, до якого саме екземпляра йде звертання. */
typedef int8_t (*vendor_read_fn)(uint8_t reg_addr, uint8_t *data,
                                 uint32_t len, void *intf_ptr);
typedef int8_t (*vendor_write_fn)(uint8_t reg_addr, const uint8_t *data,
                                  uint32_t len, void *intf_ptr);
typedef void (*vendor_delay_us_fn)(uint32_t period_us, void *intf_ptr);

/* Заводські коефіцієнти компенсації, прошиті в NVM кожного примірника. */
typedef struct {
    uint16_t dig_t1;
    int16_t dig_t2, dig_t3;
    uint16_t dig_p1;
    int16_t dig_p2, dig_p3, dig_p4, dig_p5, dig_p6, dig_p7, dig_p8, dig_p9;
    int32_t t_fine;   /* проміжок, спільний для компенсації T і P */
} vendor_calib_t;

typedef struct {
    uint8_t chip_id;
    void *intf_ptr;
    vendor_read_fn read;
    vendor_write_fn write;
    vendor_delay_us_fn delay_us;
    vendor_calib_t calib;
} vendor_sensor_dev_t;

/* Вихід драйвера: власні одиниці виробника, не SI. */
typedef struct {
    int32_t temperature;      /* соті частки °C */
    uint32_t pressure_q24_8;  /* Паскалі у форматі з фіксованою комою Q24.8 */
} vendor_data_t;

/* Скидання, перевірка ідентифікатора, вичитування коефіцієнтів. */
int8_t vendor_sensor_init(vendor_sensor_dev_t *dev);

int8_t vendor_sensor_set_mode(vendor_sensor_dev_t *dev, uint8_t mode);

/* busy = 1, поки перетворення триває. */
int8_t vendor_sensor_is_measuring(vendor_sensor_dev_t *dev, uint8_t *busy);

/* Читання сирого відліку й повна поліноміальна компенсація. */
int8_t vendor_sensor_get_data(vendor_sensor_dev_t *dev, vendor_data_t *out);

#ifdef __cplusplus
}
#endif

#endif /* VENDOR_SENSOR_H */
