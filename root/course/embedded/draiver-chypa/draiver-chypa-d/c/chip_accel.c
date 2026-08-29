#include <stddef.h>
#include <string.h>

#include "chip_accel.h"
#include "chip_fixed.h"
#include "chip_io.h"
#include "chip_recovery.h"
#include "chip_regops.h"

#define CHIP_DEFAULT_RETRIES       3u
#define CHIP_DEFAULT_RETRY_DELAY   1u
#define CHIP_POWER_ON_DELAY_MS     10u  /* вихід аналогового ядра на режим    */
#define CHIP_TURN_ON_SAMPLES       2u   /* скільки відліків після зміни ODR
                                         * чип віддає ще старим фільтром      */

/* --- внутрішні помічники ------------------------------------------------- */

static void apply_scale(chip_dev_t *dev)
{
    dev->scale_ug = chip_sensitivity_ug(dev->range);
    dev->scale_si = ((float)dev->scale_ug * 1e-6f) * CHIP_STANDARD_GRAVITY;
}

static void default_calibration(chip_calib_t *calib)
{
    for (int axis = 0; axis < 3; ++axis) {
        calib->offset_raw[axis] = 0;
        calib->gain[axis] = 1.0f;
        calib->gain_milli[axis] = 1000;
    }
}

static int16_t clamp_to_i16(int32_t value)
{
    if (value > INT16_MAX) return INT16_MAX;
    if (value < INT16_MIN) return INT16_MIN;
    return (int16_t)value;
}

/* Повертає в кремній усе, що лежить у тіньових регістрах. Потрібно після
 * скидання шини або після того, як чип пережив просідання живлення. */
static chip_status_t reapply_config(chip_dev_t *dev)
{
    static const uint8_t order[] = {
        CHIP_REG_CTRL_REG4, CHIP_REG_CTRL_REG1, CHIP_REG_CTRL_REG3,
        CHIP_REG_FIFO_CTRL, CHIP_REG_CTRL_REG5
    };

    for (size_t i = 0; i < sizeof(order) / sizeof(order[0]); ++i) {
        const uint8_t *shadow = chip_reg_shadow(dev, order[i]);
        if (shadow == NULL) {
            continue;
        }
        chip_status_t st = chip_io_write_byte(dev, order[i], *shadow);
        if (st != CHIP_OK) {
            return st;
        }
    }
    return CHIP_OK;
}

/* --- життєвий цикл ------------------------------------------------------- */

chip_status_t chip_init(chip_dev_t *dev, const chip_config_t *cfg)
{
    if (dev == NULL || cfg == NULL || cfg->bus_ops == NULL ||
        cfg->bus_ops->read == NULL || cfg->bus_ops->write == NULL ||
        cfg->bus_ops->delay_ms == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (cfg->range > CHIP_RANGE_16G || cfg->odr > CHIP_ODR_400_HZ) {
        return CHIP_ERR_INVALID_PARAM;
    }

    memset(dev, 0, sizeof(*dev));
    dev->bus_ops = cfg->bus_ops;
    dev->gpio_ops = cfg->gpio_ops;
    dev->user_ctx = cfg->user_ctx;
    dev->gpio_ctx = cfg->gpio_ctx;
    dev->dev_addr = cfg->dev_addr;
    dev->range = cfg->range;
    dev->odr = cfg->odr;
    dev->resolution = cfg->resolution;
    dev->max_retries = cfg->max_retries ? cfg->max_retries : CHIP_DEFAULT_RETRIES;
    dev->retry_delay_ms = cfg->retry_delay_ms ? cfg->retry_delay_ms : CHIP_DEFAULT_RETRY_DELAY;
    default_calibration(&dev->calib);
    apply_scale(dev);

    dev->bus_ops->delay_ms(CHIP_POWER_ON_DELAY_MS);

    /* Крок 1: чи це взагалі той чип? Неправильно змонтована мікросхема або
     * підробка з чужим ідентифікатором мусить упасти тут, а не в польоті. */
    uint8_t who = 0u;
    chip_status_t st = chip_io_read_byte(dev, CHIP_REG_WHO_AM_I, &who);
    if (st != CHIP_OK) {
        return st;
    }
    if (who != CHIP_WHO_AM_I_VALUE) {
        return CHIP_ERR_NOT_FOUND;
    }

    /* Крок 2: тінь стартує зі справжнього вмісту кремнію, а не з нулів —
     * інакше перший же update_field затер би заводські біти. */
    st = chip_reg_sync_shadow(dev);
    if (st != CHIP_OK) {
        return st;
    }

    /* Крок 3: CTRL_REG4 — BDU, діапазон, висока роздільність.
     * BDU замикає вихідні регістри до кінця вичитування блоку: без нього
     * молодший і старший байти можуть належати різним вибіркам. */
    uint8_t ctrl4 = (uint8_t)((dev->shadow_ctrl4 & (uint8_t)~(CTRL4_FS_MASK | CTRL4_HR)) |
                              CTRL4_BDU |
                              (uint8_t)((uint8_t)dev->range << CTRL4_FS_SHIFT));
    if (dev->resolution == CHIP_RES_16BIT) {
        ctrl4 |= CTRL4_HR;
    }
    st = chip_reg_write(dev, CHIP_REG_CTRL_REG4, ctrl4);
    if (st != CHIP_OK) {
        return st;
    }

    /* Крок 4: буфер поки що в обхід — читаємо останній відлік напряму. */
    st = chip_reg_write(dev, CHIP_REG_FIFO_CTRL,
                        (uint8_t)(CHIP_FIFO_BYPASS << FIFO_CTRL_MODE_SHIFT));
    if (st != CHIP_OK) {
        return st;
    }
    st = chip_reg_clear_bits(dev, CHIP_REG_CTRL_REG5, CTRL5_FIFO_EN);
    if (st != CHIP_OK) {
        return st;
    }

    /* Крок 5: жодних переривань, поки прикладний код їх не попросить. */
    st = chip_reg_clear_bits(dev, CHIP_REG_CTRL_REG3,
                             (uint8_t)(CTRL3_I1_ZYXDA | CTRL3_I1_WTM | CTRL3_I1_OVERRUN));
    if (st != CHIP_OK) {
        return st;
    }

    /* Крок 6: осі й частота — саме цей запис виводить чип із режиму спокою. */
    uint8_t ctrl1 = (uint8_t)((dev->shadow_ctrl1 & (uint8_t)~CTRL1_ODR_MASK) |
                              (uint8_t)((uint8_t)dev->odr << CTRL1_ODR_SHIFT) |
                              CTRL1_XYZ_EN);
    st = chip_reg_write(dev, CHIP_REG_CTRL_REG1, ctrl1);
    if (st != CHIP_OK) {
        return st;
    }

    dev->is_initialized = true;

    /* Крок 7: перші відліки після пуску проходять недозаповненим цифровим
     * фільтром — викидаємо їх, щоб прикладна логіка не побачила сходинки. */
    for (unsigned i = 0; i < CHIP_TURN_ON_SAMPLES; ++i) {
        int16_t discard[3];
        (void)chip_wait_data_ready(dev, 50u);
        (void)chip_read_raw(dev, discard);
    }

    return CHIP_OK;
}

chip_status_t chip_shutdown(chip_dev_t *dev)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }

    chip_status_t st = chip_reg_update_field(dev, CHIP_REG_CTRL_REG1,
                                             CTRL1_ODR_MASK, CTRL1_ODR_SHIFT,
                                             (uint8_t)CHIP_ODR_POWER_DOWN);
    dev->is_initialized = false;
    return st;
}

/* --- конфігурація -------------------------------------------------------- */

chip_status_t chip_set_range(chip_dev_t *dev, chip_range_t range)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    if (range > CHIP_RANGE_16G) {
        return CHIP_ERR_INVALID_PARAM;
    }

    chip_status_t st = chip_reg_update_field(dev, CHIP_REG_CTRL_REG4,
                                             CTRL4_FS_MASK, CTRL4_FS_SHIFT,
                                             (uint8_t)range);
    if (st != CHIP_OK) {
        return st; /* масштаб не чіпаємо: у кремнії лишився старий діапазон */
    }

    dev->range = range;
    apply_scale(dev);
    return CHIP_OK;
}

chip_status_t chip_set_odr(chip_dev_t *dev, chip_odr_t odr)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    if (odr > CHIP_ODR_400_HZ) {
        return CHIP_ERR_INVALID_PARAM;
    }

    chip_status_t st = chip_reg_update_field(dev, CHIP_REG_CTRL_REG1,
                                             CTRL1_ODR_MASK, CTRL1_ODR_SHIFT,
                                             (uint8_t)odr);
    if (st != CHIP_OK) {
        return st;
    }
    dev->odr = odr;
    return CHIP_OK;
}

chip_status_t chip_set_low_power(chip_dev_t *dev, bool enable)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    return enable ? chip_reg_set_bits(dev, CHIP_REG_CTRL_REG1, CTRL1_LPEN)
                  : chip_reg_clear_bits(dev, CHIP_REG_CTRL_REG1, CTRL1_LPEN);
}

chip_status_t chip_set_calibration(chip_dev_t *dev, const chip_calib_t *calib)
{
    if (dev == NULL || calib == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    chip_calib_t local = *calib;
    for (int axis = 0; axis < 3; ++axis) {
        /* Викликач заповнює або float, або цілий коефіцієнт — другий
         * добудовуємо самі, щоб обидва шляхи давали однакову корекцію. */
        if (local.gain[axis] == 0.0f && local.gain_milli[axis] == 0) {
            local.gain[axis] = 1.0f;
            local.gain_milli[axis] = 1000;
        } else if (local.gain[axis] == 0.0f) {
            local.gain[axis] = (float)local.gain_milli[axis] / 1000.0f;
        } else if (local.gain_milli[axis] == 0) {
            local.gain_milli[axis] = (int32_t)(local.gain[axis] * 1000.0f + 0.5f);
        }
    }

    dev->calib = local;
    return CHIP_OK;
}

chip_status_t chip_enable_drdy_interrupt(chip_dev_t *dev, bool enable)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    return enable ? chip_reg_set_bits(dev, CHIP_REG_CTRL_REG3, CTRL3_I1_ZYXDA)
                  : chip_reg_clear_bits(dev, CHIP_REG_CTRL_REG3, CTRL3_I1_ZYXDA);
}

/* --- читання ------------------------------------------------------------- */

chip_status_t chip_data_ready(chip_dev_t *dev, bool *ready, bool *overrun)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    if (ready == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    uint8_t status = 0u;
    chip_status_t st = chip_io_read_byte(dev, CHIP_REG_STATUS, &status);
    if (st != CHIP_OK) {
        return st;
    }

    *ready = (status & STATUS_ZYXDA) != 0u;
    if (overrun != NULL) {
        /* Прапорець перезапису каже, що попередній відлік ми проґавили:
         * задача збору не встигає за обраною частотою. */
        *overrun = (status & STATUS_ZYXOR) != 0u;
    }
    return CHIP_OK;
}

chip_status_t chip_wait_data_ready(chip_dev_t *dev, uint32_t timeout_ms)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    return chip_io_wait_flag(dev, CHIP_REG_STATUS, STATUS_ZYXDA, timeout_ms, 1u);
}

void chip_sample_to_raw(const chip_dev_t *dev, const uint8_t buf[6], int16_t raw[3])
{
    for (int axis = 0; axis < 3; ++axis) {
        uint16_t word = chip_le16(&buf[axis * 2]);
        int16_t code = chip_sign_extend(word, dev->resolution);
        raw[axis] = clamp_to_i16((int32_t)code - (int32_t)dev->calib.offset_raw[axis]);
    }
}

void chip_raw_to_si(const chip_dev_t *dev, const int16_t raw[3], chip_accel_si_t *accel)
{
    accel->x = (float)raw[0] * dev->scale_si * dev->calib.gain[0];
    accel->y = (float)raw[1] * dev->scale_si * dev->calib.gain[1];
    accel->z = (float)raw[2] * dev->scale_si * dev->calib.gain[2];
}

void chip_raw_to_accel_mg(const chip_dev_t *dev, const int16_t raw[3], chip_accel_mg_t *accel)
{
    int32_t *out[3] = { &accel->x, &accel->y, &accel->z };
    for (int axis = 0; axis < 3; ++axis) {
        int32_t mg = chip_raw_to_mg(raw[axis], dev->range);
        *out[axis] = chip_div_round((int64_t)mg * dev->calib.gain_milli[axis], 1000);
    }
}

void chip_raw_to_accel_mm_s2(const chip_dev_t *dev, const int16_t raw[3],
                             chip_accel_mm_s2_t *accel)
{
    int32_t *out[3] = { &accel->x, &accel->y, &accel->z };
    for (int axis = 0; axis < 3; ++axis) {
        /* Множення на g₀ робиться всередині chip_raw_to_mm_s2 у 64 бітах;
         * підсилення осі накладаємо тим самим цілим коефіцієнтом ×1000. */
        int32_t mm_s2 = chip_raw_to_mm_s2(raw[axis], dev->range);
        *out[axis] = chip_div_round((int64_t)mm_s2 * dev->calib.gain_milli[axis], 1000);
    }
}

chip_status_t chip_read_raw(chip_dev_t *dev, int16_t raw[3])
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    if (raw == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    bool ready = false;
    chip_status_t st = chip_data_ready(dev, &ready, NULL);
    if (st != CHIP_OK) {
        return st;
    }
    if (!ready) {
        return CHIP_ERR_NO_DATA;
    }

    /* Шість байтів однією транзакцією: BDU тримає їх замороженими, поки
     * останній не піде на шину. Шість окремих читань дали б розрив даних. */
    uint8_t buf[CHIP_SAMPLE_BYTES];
    st = chip_reg_read_burst(dev, CHIP_REG_OUT_X_L, buf, CHIP_SAMPLE_BYTES);
    if (st != CHIP_OK) {
        return st;
    }

    chip_sample_to_raw(dev, buf, raw);
    return CHIP_OK;
}

chip_status_t chip_read_accel_si(chip_dev_t *dev, chip_accel_si_t *accel)
{
    if (accel == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    int16_t raw[3];
    chip_status_t st = chip_read_raw(dev, raw);
    if (st != CHIP_OK) {
        return st;
    }
    chip_raw_to_si(dev, raw, accel);
    return CHIP_OK;
}

chip_status_t chip_read_accel_mg(chip_dev_t *dev, chip_accel_mg_t *accel)
{
    if (accel == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    int16_t raw[3];
    chip_status_t st = chip_read_raw(dev, raw);
    if (st != CHIP_OK) {
        return st;
    }
    chip_raw_to_accel_mg(dev, raw, accel);
    return CHIP_OK;
}

chip_status_t chip_read_accel_mm_s2(chip_dev_t *dev, chip_accel_mm_s2_t *accel)
{
    if (accel == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    int16_t raw[3];
    chip_status_t st = chip_read_raw(dev, raw);
    if (st != CHIP_OK) {
        return st;
    }
    chip_raw_to_accel_mm_s2(dev, raw, accel);
    return CHIP_OK;
}

/* --- аварійне відновлення ------------------------------------------------ */

chip_status_t chip_recover_bus(chip_dev_t *dev)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (dev->gpio_ops == NULL) {
        return CHIP_ERR_INVALID_PARAM; /* платформа не дала ліній SCL/SDA */
    }

    chip_status_t st = chip_bus_recover(dev->gpio_ops, dev->gpio_ctx);
    if (st != CHIP_OK) {
        return st;
    }

    /* Чип пережив дотактовування, але міг втратити конфігурацію разом із
     * живленням — повертаємо її з тіні й перевіряємо, що це той самий чип. */
    uint8_t who = 0u;
    st = chip_io_read_byte(dev, CHIP_REG_WHO_AM_I, &who);
    if (st != CHIP_OK) {
        return st;
    }
    if (who != CHIP_WHO_AM_I_VALUE) {
        dev->is_initialized = false;
        return CHIP_ERR_NOT_FOUND;
    }

    return reapply_config(dev);
}
