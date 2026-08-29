/*
 * Реалізація контракту. Жодного статичного стану, жодного malloc,
 * жодного __disable_irq() — усе, що виходить назовні, іде через bus_ops.
 */
#include "chip_driver.h"
#include "chip_regs.h"

#include <string.h>

#define CHIP_G_MS2              9.80665f

#define CHIP_BOOT_TIMEOUT_MS    20u
#define CHIP_DRDY_TIMEOUT_MS    250u
#define CHIP_POLL_STEP_MS       1u

/* Паспортне вікно самотесту для ±2 g, у мg. */
#define CHIP_ST_MIN_MG          17
#define CHIP_ST_MAX_MG          360
#define CHIP_ST_AVG_SAMPLES     5u
#define CHIP_ST_SETTLE_MS       90u

/* ------------------------------------------------------------------ */
/* Транспортні обгортки                                                */
/* ------------------------------------------------------------------ */

static chip_status_t map_bus(int32_t rc)
{
    if (rc == CHIP_BUS_OK) {
        return CHIP_STATUS_OK;
    }
    if (rc == CHIP_BUS_ERR_TIMEOUT) {
        return CHIP_ERR_TIMEOUT;
    }
    return CHIP_ERR_COMM_FAIL;
}

static void chip_delay(const chip_dev_t *dev, uint32_t ms)
{
    dev->bus_ops->delay_ms(ms, dev->user_ctx);
}

/* Пакетне читання: для len > 1 обовʼязково піднімаємо біт автоінкремента. */
static chip_status_t reg_read(const chip_dev_t *dev, uint8_t reg, uint8_t *buf, uint16_t len)
{
    uint8_t addr = (len > 1u) ? CHIP_REG_AUTO_INC(reg) : reg;
    return map_bus(dev->bus_ops->read(dev->dev_addr, addr, buf, len, dev->user_ctx));
}

static chip_status_t reg_read8(const chip_dev_t *dev, uint8_t reg, uint8_t *value)
{
    return reg_read(dev, reg, value, 1u);
}

static chip_status_t reg_write8(const chip_dev_t *dev, uint8_t reg, uint8_t value)
{
    return map_bus(dev->bus_ops->write(dev->dev_addr, reg, &value, 1u, dev->user_ctx));
}

/*
 * Запис керувального регістру через тінь: нове значення рахуємо з копії в
 * дескрипторі, а не з читання шини. Read-modify-write по I2C коштує зайвої
 * транзакції й ламається, щойно між читанням і записом втрутиться інша
 * задача чи апаратне скидання прапорця.
 */
static chip_status_t ctrl_write(chip_dev_t *dev, uint8_t reg, uint8_t value)
{
    chip_status_t st = reg_write8(dev, reg, value);
    if (st != CHIP_STATUS_OK) {
        return st;
    }
    switch (reg) {
    case CHIP_REG_CTRL1: dev->shadow_ctrl1 = value; break;
    case CHIP_REG_CTRL4: dev->shadow_ctrl4 = value; break;
    case CHIP_REG_CTRL5: dev->shadow_ctrl5 = value; break;
    default: break;
    }
    return CHIP_STATUS_OK;
}

/* ------------------------------------------------------------------ */
/* Дрібні перетворення                                                 */
/* ------------------------------------------------------------------ */

/* Ціна розряду у високому роздільному режимі (12 біт), мg на розряд. */
static float lsb_mg_for_range(uint8_t range_g)
{
    switch (range_g) {
    case 2u:  return 1.0f;
    case 4u:  return 2.0f;
    case 8u:  return 4.0f;
    case 16u: return 12.0f;
    default:  return 0.0f;
    }
}

static bool fs_bits_for_range(uint8_t range_g, uint8_t *bits)
{
    switch (range_g) {
    case 2u:  *bits = 0u; return true;
    case 4u:  *bits = 1u; return true;
    case 8u:  *bits = 2u; return true;
    case 16u: *bits = 3u; return true;
    default:  return false;
    }
}

static bool odr_bits_for_hz(uint16_t hz, uint8_t *bits)
{
    switch (hz) {
    case 1u:   *bits = 0x1u; return true;
    case 10u:  *bits = 0x2u; return true;
    case 25u:  *bits = 0x3u; return true;
    case 50u:  *bits = 0x4u; return true;
    case 100u: *bits = 0x5u; return true;
    case 200u: *bits = 0x6u; return true;
    case 400u: *bits = 0x7u; return true;
    default:   return false;
    }
}

/*
 * Відлік лежить у двох байтах little-endian, вирівняний уліво: значущі
 * дванадцять біт сидять у старших розрядах. Знак треба зберегти, тому
 * спершу збираємо int16_t, і лише потім зсуваємо арифметично.
 */
static int16_t raw_axis(const uint8_t *p)
{
    uint16_t u = (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
    int16_t  s = (int16_t)u;
    return (int16_t)(s / 16);   /* /16 замість >>4: ділення визначене й для відʼємних */
}

static void decode_sample(const uint8_t *raw, float lsb_to_ms2, chip_axes_data_si_t *out)
{
    out->x = (float)raw_axis(&raw[0]) * lsb_to_ms2;
    out->y = (float)raw_axis(&raw[2]) * lsb_to_ms2;
    out->z = (float)raw_axis(&raw[4]) * lsb_to_ms2;
}

/* ------------------------------------------------------------------ */
/* Скидання й підняття NVM                                             */
/* ------------------------------------------------------------------ */

/*
 * BOOT самоскидний: піднімає з NVM коефіцієнти підстроювання й сам падає в
 * нуль, коли закінчив. Чекаємо квантовано — нескінченного циклу опитування
 * тут бути не може.
 */
static chip_status_t boot_and_wait(chip_dev_t *dev)
{
    chip_status_t st = reg_write8(dev, CHIP_REG_CTRL5, CHIP_CTRL5_BOOT);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    for (uint32_t waited = 0u; waited < CHIP_BOOT_TIMEOUT_MS; waited += CHIP_POLL_STEP_MS) {
        uint8_t ctrl5 = 0u;
        chip_delay(dev, CHIP_POLL_STEP_MS);
        st = reg_read8(dev, CHIP_REG_CTRL5, &ctrl5);
        if (st != CHIP_STATUS_OK) {
            return st;
        }
        if ((ctrl5 & CHIP_CTRL5_BOOT) == 0u) {
            dev->shadow_ctrl5 = ctrl5;
            return CHIP_STATUS_OK;
        }
    }
    return CHIP_ERR_TIMEOUT;
}

chip_status_t chip_reload_trim(chip_dev_t *dev)
{
    if (dev == NULL || dev->bus_ops == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    chip_status_t st = boot_and_wait(dev);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    /* Якщо NVM піднялася справно, керувальні регістри стоять у заводських
     * значеннях. Розбіжність означає пошкоджений вміст пам'яті підстроювання. */
    uint8_t ctrl[6] = {0};
    st = reg_read(dev, CHIP_REG_CTRL1, ctrl, sizeof ctrl);
    if (st != CHIP_STATUS_OK) {
        return st;
    }
    if (ctrl[0] != CHIP_CTRL1_RESET_VALUE) {
        return CHIP_ERR_CALIBRATION_INVALID;
    }
    for (unsigned i = 1u; i < sizeof ctrl; ++i) {
        if (ctrl[i] != 0u) {
            return CHIP_ERR_CALIBRATION_INVALID;
        }
    }

    dev->shadow_ctrl1 = ctrl[0];
    dev->shadow_ctrl4 = ctrl[3];
    dev->shadow_ctrl5 = ctrl[4];
    return CHIP_STATUS_OK;
}

chip_status_t chip_soft_reset(chip_dev_t *dev)
{
    if (dev == NULL || dev->bus_ops == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    chip_status_t st = chip_reload_trim(dev);
    dev->is_initialized = false;
    dev->sample_pending = false;
    return st;
}

/* ------------------------------------------------------------------ */
/* Життєвий цикл                                                       */
/* ------------------------------------------------------------------ */

chip_status_t chip_init(chip_dev_t *dev,
                        const chip_bus_ops_t *bus_ops,
                        void *user_ctx,
                        uint8_t dev_addr)
{
    if (dev == NULL || bus_ops == NULL ||
        bus_ops->read == NULL || bus_ops->write == NULL || bus_ops->delay_ms == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (dev_addr > 0x7Fu) {
        return CHIP_ERR_INVALID_PARAM;
    }

    memset(dev, 0, sizeof *dev);
    dev->bus_ops  = bus_ops;
    dev->user_ctx = user_ctx;
    dev->dev_addr = dev_addr;

    uint8_t who = 0u;
    chip_status_t st = reg_read8(dev, CHIP_REG_WHO_AM_I, &who);
    if (st != CHIP_STATUS_OK) {
        return st;
    }
    if (who != CHIP_WHO_AM_I_VALUE) {
        /* Відповідь є, але це не наша мікросхема: переплутана адреса,
         * інший датчик на тій самій шині або підробка в партії. */
        return CHIP_ERR_DEVICE_NOT_FOUND;
    }

    st = chip_reload_trim(dev);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    /* Відомий стан: високий роздільний, BDU, ±2 g, три осі, 100 Гц. */
    st = ctrl_write(dev, CHIP_REG_CTRL4, CHIP_CTRL4_BDU | CHIP_CTRL4_HR);
    if (st != CHIP_STATUS_OK) {
        return st;
    }
    st = ctrl_write(dev, CHIP_REG_CTRL1, CHIP_CTRL1_XYZ_EN | (0x5u << CHIP_CTRL1_ODR_SHIFT));
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    dev->range_g        = 2u;
    dev->lsb_to_ms2     = lsb_mg_for_range(2u) * 0.001f * CHIP_G_MS2;
    dev->is_initialized = true;
    return CHIP_STATUS_OK;
}

chip_status_t chip_set_range(chip_dev_t *dev, uint8_t range_g)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    uint8_t fs = 0u;
    if (!fs_bits_for_range(range_g, &fs)) {
        return CHIP_ERR_INVALID_PARAM;
    }

    uint8_t ctrl4 = (uint8_t)((dev->shadow_ctrl4 & (uint8_t)~CHIP_CTRL4_FS_MASK) |
                              (uint8_t)(fs << CHIP_CTRL4_FS_SHIFT));
    chip_status_t st = ctrl_write(dev, CHIP_REG_CTRL4, ctrl4);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    dev->range_g    = range_g;
    dev->lsb_to_ms2 = lsb_mg_for_range(range_g) * 0.001f * CHIP_G_MS2;
    return CHIP_STATUS_OK;
}

chip_status_t chip_set_odr_hz(chip_dev_t *dev, uint16_t odr_hz)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    uint8_t odr = 0u;
    if (!odr_bits_for_hz(odr_hz, &odr)) {
        return CHIP_ERR_INVALID_PARAM;
    }

    uint8_t ctrl1 = (uint8_t)((dev->shadow_ctrl1 & (uint8_t)~CHIP_CTRL1_ODR_MASK) |
                              (uint8_t)(odr << CHIP_CTRL1_ODR_SHIFT));
    return ctrl_write(dev, CHIP_REG_CTRL1, ctrl1);
}

chip_status_t chip_shutdown(chip_dev_t *dev)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    uint8_t ctrl1 = (uint8_t)(dev->shadow_ctrl1 & (uint8_t)~CHIP_CTRL1_ODR_MASK);
    chip_status_t st = ctrl_write(dev, CHIP_REG_CTRL1, ctrl1);
    if (st == CHIP_STATUS_OK) {
        dev->is_initialized = false;
        dev->sample_pending = false;
    }
    return st;
}

/* ------------------------------------------------------------------ */
/* Читання відліків                                                    */
/* ------------------------------------------------------------------ */

chip_status_t chip_read_sample_si(chip_dev_t *dev, chip_axes_data_si_t *data_si)
{
    if (dev == NULL || data_si == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    uint8_t status = 0u;
    chip_status_t st = reg_read8(dev, CHIP_REG_STATUS, &status);
    if (st != CHIP_STATUS_OK) {
        return st;
    }
    if ((status & CHIP_STATUS_ZYXDA) == 0u) {
        return CHIP_ERR_DATA_NOT_READY;
    }

    /* Шість байтів однією транзакцією: під BDU вихідні регістри заморожені,
     * поки не прочитано старший байт, тож три осі належать одному відлікові. */
    uint8_t raw[CHIP_SAMPLE_BYTES];
    st = reg_read(dev, CHIP_REG_OUT_X_L, raw, (uint16_t)sizeof raw);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    decode_sample(raw, dev->lsb_to_ms2, data_si);
    dev->sample_pending = false;
    return CHIP_STATUS_OK;
}

void chip_drdy_from_isr(chip_dev_t *dev)
{
    if (dev != NULL) {
        dev->sample_pending = true;
    }
}

bool chip_sample_pending(const chip_dev_t *dev)
{
    return (dev != NULL) && dev->sample_pending;
}

/* ------------------------------------------------------------------ */
/* Апаратна черга                                                      */
/* ------------------------------------------------------------------ */

chip_status_t chip_fifo_enable(chip_dev_t *dev, bool enable)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    uint8_t ctrl5 = enable
        ? (uint8_t)(dev->shadow_ctrl5 | CHIP_CTRL5_FIFO_EN)
        : (uint8_t)(dev->shadow_ctrl5 & (uint8_t)~CHIP_CTRL5_FIFO_EN);

    chip_status_t st = ctrl_write(dev, CHIP_REG_CTRL5, ctrl5);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    /* Черга перезапускається лише через Bypass: без цього кроку після
     * переповнення вона так і лишиться закритою. */
    st = reg_write8(dev, CHIP_REG_FIFO_CTRL, CHIP_FIFO_MODE_BYPASS);
    if (st != CHIP_STATUS_OK || !enable) {
        return st;
    }
    return reg_write8(dev, CHIP_REG_FIFO_CTRL, CHIP_FIFO_MODE_STREAM);
}

chip_status_t chip_fifo_read(chip_dev_t *dev,
                             chip_fifo_buf_t *scratch,
                             chip_axes_data_si_t *out,
                             uint8_t max_samples,
                             chip_fifo_status_t *fifo_status)
{
    if (dev == NULL || scratch == NULL || out == NULL || fifo_status == NULL || max_samples == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    uint8_t src = 0u;
    chip_status_t st = reg_read8(dev, CHIP_REG_FIFO_SRC, &src);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    fifo_status->overrun   = (src & CHIP_FIFO_SRC_OVRN) != 0u;
    fifo_status->watermark = (src & CHIP_FIFO_SRC_WTM) != 0u;
    fifo_status->count     = 0u;

    uint8_t available = (uint8_t)(src & CHIP_FIFO_SRC_FSS);
    if (available > CHIP_FIFO_DEPTH) {
        available = CHIP_FIFO_DEPTH;
    }
    if (available > max_samples) {
        available = max_samples;
    }
    if (available == 0u) {
        return CHIP_ERR_DATA_NOT_READY;
    }

    /* Одна пакетна транзакція на всю черга-порцію: читання OUT_X_L з
     * автоінкрементом просуває чергу на відлік за кожні шість байтів. */
    uint16_t bytes = (uint16_t)(available * CHIP_SAMPLE_BYTES);
    st = reg_read(dev, CHIP_REG_OUT_X_L, scratch->raw, bytes);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    for (uint8_t i = 0u; i < available; ++i) {
        decode_sample(&scratch->raw[i * CHIP_SAMPLE_BYTES], dev->lsb_to_ms2, &out[i]);
    }
    fifo_status->count = available;
    dev->sample_pending = false;

    if (fifo_status->overrun) {
        /* Дані віддали, але попередили: частину відліків утрачено, і черга
         * потребує перезапуску через Bypass. */
        return chip_fifo_enable(dev, true);
    }
    return CHIP_STATUS_OK;
}

/* ------------------------------------------------------------------ */
/* Самотест                                                            */
/* ------------------------------------------------------------------ */

static chip_status_t wait_drdy(chip_dev_t *dev)
{
    for (uint32_t waited = 0u; waited < CHIP_DRDY_TIMEOUT_MS; waited += CHIP_POLL_STEP_MS) {
        uint8_t status = 0u;
        chip_status_t st = reg_read8(dev, CHIP_REG_STATUS, &status);
        if (st != CHIP_STATUS_OK) {
            return st;
        }
        if ((status & CHIP_STATUS_ZYXDA) != 0u) {
            return CHIP_STATUS_OK;
        }
        chip_delay(dev, CHIP_POLL_STEP_MS);
    }
    return CHIP_ERR_TIMEOUT;
}

/* Середнє по n відліках у сирих розрядах — перший відлік після зміни
 * режиму відкидаємо, він іще від старих налаштувань. */
static chip_status_t average_raw(chip_dev_t *dev, int32_t avg[3], uint8_t n)
{
    uint8_t raw[CHIP_SAMPLE_BYTES];
    int32_t sum[3] = {0, 0, 0};

    chip_status_t st = wait_drdy(dev);
    if (st != CHIP_STATUS_OK) {
        return st;
    }
    st = reg_read(dev, CHIP_REG_OUT_X_L, raw, (uint16_t)sizeof raw);
    if (st != CHIP_STATUS_OK) {
        return st;
    }

    for (uint8_t i = 0u; i < n; ++i) {
        st = wait_drdy(dev);
        if (st != CHIP_STATUS_OK) {
            return st;
        }
        st = reg_read(dev, CHIP_REG_OUT_X_L, raw, (uint16_t)sizeof raw);
        if (st != CHIP_STATUS_OK) {
            return st;
        }
        sum[0] += raw_axis(&raw[0]);
        sum[1] += raw_axis(&raw[2]);
        sum[2] += raw_axis(&raw[4]);
    }

    for (unsigned axis = 0u; axis < 3u; ++axis) {
        avg[axis] = sum[axis] / (int32_t)n;
    }
    return CHIP_STATUS_OK;
}

chip_status_t chip_self_test(chip_dev_t *dev)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INITIALIZED;
    }

    const uint8_t saved_ctrl1 = dev->shadow_ctrl1;
    const uint8_t saved_ctrl4 = dev->shadow_ctrl4;
    const uint8_t range_saved = dev->range_g;

    /* Паспортне вікно задано для ±2 g, високого роздільного, 50 Гц. */
    chip_status_t st = ctrl_write(dev, CHIP_REG_CTRL4, CHIP_CTRL4_BDU | CHIP_CTRL4_HR);
    if (st != CHIP_STATUS_OK) {
        goto restore;
    }
    st = ctrl_write(dev, CHIP_REG_CTRL1, CHIP_CTRL1_XYZ_EN | (0x4u << CHIP_CTRL1_ODR_SHIFT));
    if (st != CHIP_STATUS_OK) {
        goto restore;
    }
    chip_delay(dev, CHIP_ST_SETTLE_MS);

    int32_t base[3];
    st = average_raw(dev, base, CHIP_ST_AVG_SAMPLES);
    if (st != CHIP_STATUS_OK) {
        goto restore;
    }

    /* Умикаємо електростатичне збудження маси. */
    st = ctrl_write(dev, CHIP_REG_CTRL4,
                    (uint8_t)(CHIP_CTRL4_BDU | CHIP_CTRL4_HR | CHIP_CTRL4_ST_0));
    if (st != CHIP_STATUS_OK) {
        goto restore;
    }
    chip_delay(dev, CHIP_ST_SETTLE_MS);

    int32_t excited[3];
    st = average_raw(dev, excited, CHIP_ST_AVG_SAMPLES);
    if (st != CHIP_STATUS_OK) {
        goto restore;
    }

    /* У режимі ±2 g один розряд — рівно 1 мg, тож різниця в розрядах і є
     * різниця в мg: порівнюємо просто з вікном 17…360. */
    for (unsigned axis = 0u; axis < 3u; ++axis) {
        int32_t delta = excited[axis] - base[axis];
        if (delta < 0) {
            delta = -delta;
        }
        if (delta < CHIP_ST_MIN_MG || delta > CHIP_ST_MAX_MG) {
            st = CHIP_ERR_SELF_TEST_FAILED;
            break;
        }
    }

restore:
    /* Збудження треба зняти навіть тоді, коли тест провалився чи шина впала:
     * інакше датчик лишиться назавжди зміщеним. */
    (void)ctrl_write(dev, CHIP_REG_CTRL4, saved_ctrl4);
    (void)ctrl_write(dev, CHIP_REG_CTRL1, saved_ctrl1);
    dev->range_g    = range_saved;
    dev->lsb_to_ms2 = lsb_mg_for_range(range_saved) * 0.001f * CHIP_G_MS2;
    return st;
}
