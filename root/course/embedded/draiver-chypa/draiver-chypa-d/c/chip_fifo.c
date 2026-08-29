#include "chip_accel.h"
#include "chip_fifo.h"
#include "chip_io.h"
#include "chip_regops.h"

/* Скільки вибірок забираємо однією транзакцією. 8 × 6 = 48 байтів — пачка,
 * яку не соромно віддати DMA й яка не з'їдає стек задачі збору. */
#define CHIP_FIFO_CHUNK_SAMPLES 8u

static chip_status_t write_fifo_ctrl(chip_dev_t *dev, chip_fifo_mode_t mode, uint8_t watermark)
{
    uint8_t value = (uint8_t)(((uint8_t)mode << FIFO_CTRL_MODE_SHIFT) & FIFO_CTRL_MODE_MASK);
    value |= (uint8_t)(watermark & FIFO_CTRL_WTM_MASK);
    return chip_reg_write(dev, CHIP_REG_FIFO_CTRL, value);
}

chip_status_t chip_fifo_configure(chip_dev_t *dev, const chip_fifo_config_t *cfg)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    if (cfg == NULL || cfg->mode > CHIP_FIFO_STREAM_TO_FIFO ||
        cfg->watermark >= CHIP_FIFO_DEPTH) {
        return CHIP_ERR_INVALID_PARAM;
    }

    if (cfg->mode == CHIP_FIFO_BYPASS) {
        chip_status_t st = write_fifo_ctrl(dev, CHIP_FIFO_BYPASS, 0u);
        if (st != CHIP_OK) {
            return st;
        }
        return chip_reg_clear_bits(dev, CHIP_REG_CTRL_REG5, CTRL5_FIFO_EN);
    }

    /* Прохід через Bypass очищає вміст буфера: інакше перші вибірки нового
     * режиму приїхали б упереміш зі старими. */
    chip_status_t st = write_fifo_ctrl(dev, CHIP_FIFO_BYPASS, 0u);
    if (st != CHIP_OK) {
        return st;
    }

    st = chip_reg_set_bits(dev, CHIP_REG_CTRL_REG5, CTRL5_FIFO_EN);
    if (st != CHIP_OK) {
        return st;
    }

    return write_fifo_ctrl(dev, cfg->mode, cfg->watermark);
}

chip_status_t chip_fifo_restart(chip_dev_t *dev)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }

    uint8_t saved = dev->shadow_fifo_ctrl;
    chip_fifo_mode_t mode = (chip_fifo_mode_t)((saved & FIFO_CTRL_MODE_MASK) >> FIFO_CTRL_MODE_SHIFT);
    uint8_t watermark = (uint8_t)(saved & FIFO_CTRL_WTM_MASK);

    if (mode == CHIP_FIFO_BYPASS) {
        return CHIP_OK; /* нічого не накопичується — нічого й скидати */
    }

    chip_status_t st = write_fifo_ctrl(dev, CHIP_FIFO_BYPASS, 0u);
    if (st != CHIP_OK) {
        return st;
    }
    return write_fifo_ctrl(dev, mode, watermark);
}

chip_status_t chip_fifo_enable_watermark_interrupt(chip_dev_t *dev, bool enable)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    uint8_t bits = (uint8_t)(CTRL3_I1_WTM | CTRL3_I1_OVERRUN);
    return enable ? chip_reg_set_bits(dev, CHIP_REG_CTRL_REG3, bits)
                  : chip_reg_clear_bits(dev, CHIP_REG_CTRL_REG3, bits);
}

chip_status_t chip_fifo_level(chip_dev_t *dev, uint8_t *samples,
                              bool *watermark_hit, bool *overrun)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }

    uint8_t src = 0u;
    chip_status_t st = chip_io_read_byte(dev, CHIP_REG_FIFO_SRC, &src);
    if (st != CHIP_OK) {
        return st;
    }

    if (samples != NULL) {
        /* EMPTY і рівень FSS живуть в одному байті: порожній буфер віддає
         * FSS = 0 разом із виставленим EMPTY. */
        *samples = (src & FIFO_SRC_EMPTY) ? 0u : (uint8_t)(src & FIFO_SRC_FSS_MASK);
    }
    if (watermark_hit != NULL) {
        *watermark_hit = (src & FIFO_SRC_WTM) != 0u;
    }
    if (overrun != NULL) {
        *overrun = (src & FIFO_SRC_OVRN) != 0u;
    }
    return CHIP_OK;
}

chip_status_t chip_fifo_read(chip_dev_t *dev, chip_accel_si_t *out,
                             size_t max_samples, size_t *read_samples)
{
    if (dev == NULL || !dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }
    if (out == NULL || max_samples == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }

    if (read_samples != NULL) {
        *read_samples = 0u;
    }

    uint8_t available = 0u;
    chip_status_t st = chip_fifo_level(dev, &available, NULL, NULL);
    if (st != CHIP_OK) {
        return st;
    }
    if (available == 0u) {
        return CHIP_ERR_NO_DATA;
    }

    size_t remaining = (available < max_samples) ? (size_t)available : max_samples;
    size_t done = 0u;

    while (remaining > 0u) {
        size_t chunk = (remaining < CHIP_FIFO_CHUNK_SAMPLES) ? remaining : CHIP_FIFO_CHUNK_SAMPLES;
        uint8_t buf[CHIP_FIFO_CHUNK_SAMPLES * CHIP_SAMPLE_BYTES];

        /* Адреса всередині блоку OUT_* закільцьовується, тож одна транзакція
         * з автоінкрементом віддає підряд кілька повних вибірок. */
        st = chip_reg_read_burst(dev, CHIP_REG_OUT_X_L, buf,
                                 (uint16_t)(chunk * CHIP_SAMPLE_BYTES));
        if (st != CHIP_OK) {
            if (read_samples != NULL) {
                *read_samples = done; /* що встигли забрати — те дійсне */
            }
            return st;
        }

        for (size_t i = 0; i < chunk; ++i) {
            int16_t raw[3];
            chip_sample_to_raw(dev, &buf[i * CHIP_SAMPLE_BYTES], raw);
            chip_raw_to_si(dev, raw, &out[done + i]);
        }

        done += chunk;
        remaining -= chunk;
    }

    if (read_samples != NULL) {
        *read_samples = done;
    }
    return CHIP_OK;
}
