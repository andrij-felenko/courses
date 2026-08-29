/* chip_accel.h — Рівень 3: прикладний інтерфейс предметної області.
 *
 * Викликач не бачить ні адрес регістрів, ні бітових масок, ні порядку байтів:
 * він просить частоту в герцах і отримує прискорення в метрах на секунду в
 * квадраті — уже з урахуванням діапазону повної шкали та калібрування.
 */
#ifndef CHIP_ACCEL_H
#define CHIP_ACCEL_H

#include <stdbool.h>
#include <stdint.h>

#include "chip_dev.h"
#include "chip_status.h"

/* Усе, що потрібно знати драйверу про конкретний екземпляр чипа на платі. */
typedef struct {
    const chip_bus_ops_t  *bus_ops;
    const chip_gpio_ops_t *gpio_ops; /* може бути NULL: без скидання шини     */
    void                  *user_ctx;
    void                  *gpio_ctx; /* контекст ліній SCL/SDA                */
    uint8_t                dev_addr;

    chip_range_t      range;
    chip_odr_t        odr;
    chip_resolution_t resolution;

    uint8_t  max_retries;    /* 0 — узяти типове значення 3                   */
    uint32_t retry_delay_ms; /* 0 — узяти типове значення 1 мс                */
} chip_config_t;

/* Життєвий цикл ---------------------------------------------------------- */

/* Перевіряє WHO_AM_I, зчитує справжній стан регістрів у тінь, вмикає BDU,
 * виставляє діапазон, частоту й осі. Пам'ять під dev виділяє викликач. */
chip_status_t chip_init(chip_dev_t *dev, const chip_config_t *cfg);

/* Переводить чип у режим спокою (ODR = 0) і знімає прапорець готовності. */
chip_status_t chip_shutdown(chip_dev_t *dev);

/* Конфігурація ----------------------------------------------------------- */
chip_status_t chip_set_range(chip_dev_t *dev, chip_range_t range);
chip_status_t chip_set_odr(chip_dev_t *dev, chip_odr_t odr);
chip_status_t chip_set_low_power(chip_dev_t *dev, bool enable);
chip_status_t chip_set_calibration(chip_dev_t *dev, const chip_calib_t *calib);

/* Маршрутизація сигналу готовності даних на вивід INT1 (DRDY). Обробник
 * переривання лише сигналить задачі; шину читає задача, не обробник. */
chip_status_t chip_enable_drdy_interrupt(chip_dev_t *dev, bool enable);

/* Читання ---------------------------------------------------------------- */
chip_status_t chip_data_ready(chip_dev_t *dev, bool *ready, bool *overrun);
chip_status_t chip_wait_data_ready(chip_dev_t *dev, uint32_t timeout_ms);

chip_status_t chip_read_raw(chip_dev_t *dev, int16_t raw[3]);
chip_status_t chip_read_accel_si(chip_dev_t *dev, chip_accel_si_t *accel);

/* Два цілочисельні шляхи для ядер без FPU: у мілігравітаціях (звичний для
 * даташита вимір) і одразу в SI, у міліметрах на секунду в квадраті. */
chip_status_t chip_read_accel_mg(chip_dev_t *dev, chip_accel_mg_t *accel);
chip_status_t chip_read_accel_mm_s2(chip_dev_t *dev, chip_accel_mm_s2_t *accel);

/* Аварійне відновлення --------------------------------------------------- */

/* Дотактовує завислий чип лініями GPIO, формує STOP і повертає в кремній
 * конфігурацію з тіньових регістрів. Без gpio_ops — CHIP_ERR_INVALID_PARAM. */
chip_status_t chip_recover_bus(chip_dev_t *dev);

/* Внутрішні перетворення, спільні з модулем FIFO -------------------------- */

/* Шість байтів блоку OUT_* → три сирі відліки з розширеним знаком і знятим
 * зміщенням нуля. */
void chip_sample_to_raw(const chip_dev_t *dev, const uint8_t buf[6], int16_t raw[3]);

/* Сирі відліки → фізичні величини SI із застосуванням масштабу й підсилення. */
void chip_raw_to_si(const chip_dev_t *dev, const int16_t raw[3], chip_accel_si_t *accel);

/* Сирі відліки → мілігравітації для ядер без FPU. */
void chip_raw_to_accel_mg(const chip_dev_t *dev, const int16_t raw[3], chip_accel_mg_t *accel);

/* Сирі відліки → міліметри на секунду в квадраті, теж без плаваючої коми. */
void chip_raw_to_accel_mm_s2(const chip_dev_t *dev, const int16_t raw[3],
                             chip_accel_mm_s2_t *accel);

#endif /* CHIP_ACCEL_H */
