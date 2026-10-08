#include "ov3640.h"
#include <string.h>

/**
 * @file ov3640.c
 * @brief Реалізація C-драйвера сенсора OV3640: запис/читання по шині SCCB,
 *        таблиці регістрів гамма-корекції, матриці кольорів, PCLK та перемикання YUV422/JPEG.
 */

/* Масив базової ініціалізації матриці OV3640 */
static const ov3640_reg_val_t ov3640_default_init_regs[] = {
    {0x3012, 0x80}, /* Системне скидання регістрів */
    {0x300D, 0x02}, /* Дельник частоти PCLK */
    {0x3011, 0x00}, /* Внутрішнє тактування системи */
    /* Таблиця гамма-корекції (Gamma Curve Settings) */
    {0x5300, 0x08},
    {0x5301, 0x16},
    {0x5302, 0x2A},
    {0x5303, 0x4E},
    {0x5304, 0x65},
    {0x5305, 0x76},
    {0x5306, 0x85},
    {0x5307, 0x91},
    {0x5308, 0x9D},
    {0x5309, 0xA7},
    {0x530A, 0xB7},
    {0x530B, 0xC4},
    {0x530C, 0xD4},
    /* Матриця корекції кольорів (Color Matrix Coefficient Settings) */
    {0x5380, 0x38},
    {0x5381, 0x12},
    {0x5382, 0x06},
    {0x5383, 0x08},
    {0x5384, 0x34},
    {0x5385, 0x24},
    {0x5386, 0x02},
    {0x5387, 0x0A},
    {0x5388, 0x38},
    {0x5000, 0xFF}  /* Увімкнення блоку DSP обробки */
};

/* Налаштування для формату YUV422 */
static const ov3640_reg_val_t ov3640_fmt_yuv422_regs[] = {
    {0x3600, 0x00}, /* Режим YUV422 (YUYV порядок байтів) */
    {0x3601, 0x40}, /* Нормальний вихід даних без стиснення */
    {0x300D, 0x01}  /* Тактування PCLK під YUV потік */
};

/* Налаштування для стиснутого формату JPEG */
static const ov3640_reg_val_t ov3640_fmt_jpeg_regs[] = {
    {0x3600, 0x10}, /* Увімкнення апаратного JPEG-енкодера */
    {0x3601, 0x82}, /* Потоковий формат із вставкою маркерів SOI/EOI */
    {0x300D, 0x04}  /* Збільшення дільника PCLK для підлаштування під швидкість DMA */
};

/* Регістри вибору роздільної здатності VGA (640x480) */
static const ov3640_reg_val_t ov3640_res_vga_regs[] = {
    {0x3800, 0x02}, /* X-старт вікна */
    {0x3801, 0x80}, /* Y-старт вікна */
    {0x3804, 0x02}, /* X-ширина 640 */
    {0x3805, 0x80},
    {0x3806, 0x01}, /* Y-висота 480 */
    {0x3807, 0xE0}
};

/* Регістри вибору роздільної здатності 1080p (1920x1080) */
static const ov3640_reg_val_t ov3640_res_1080p_regs[] = {
    {0x3800, 0x00},
    {0x3801, 0x00},
    {0x3804, 0x07}, /* X-ширина 1920 */
    {0x3805, 0x80},
    {0x3806, 0x04}, /* Y-висота 1080 */
    {0x3807, 0x38}
};

/* Регістри вибору роздільної здатності QXGA (2048x1536) */
static const ov3640_reg_val_t ov3640_res_qxga_regs[] = {
    {0x3800, 0x00},
    {0x3801, 0x00},
    {0x3804, 0x08}, /* X-ширина 2048 */
    {0x3805, 0x00},
    {0x3806, 0x06}, /* Y-висота 1536 */
    {0x3807, 0x00}
};

ov3640_status_t ov3640_init(ov3640_handle_t *handle, const ov3640_io_t *io)
{
    if (!handle || !io || !io->sccb_write || !io->sccb_read || !io->delay_ms) {
        return OV3640_ERR_PARAM;
    }

    memset(handle, 0, sizeof(ov3640_handle_t));
    handle->io = *io;
    if (handle->io.sccb_addr == 0) {
        handle->io.sccb_addr = OV3640_SCCB_ADDR_WRITE;
    }

    /* Апаратне скидання та вихід із режиму сну */
    ov3640_set_power(handle, false);
    ov3640_reset(handle);

    /* Перевірка ідентифікатора сенсора */
    uint16_t chip_id = 0;
    ov3640_status_t status = ov3640_read_chip_id(handle, &chip_id);
    if (status != OV3640_OK) {
        return status;
    }

    /* Завантаження базових регістрів конфігурації */
    status = ov3640_write_reg_list(handle, ov3640_default_init_regs,
                                   sizeof(ov3640_default_init_regs) / sizeof(ov3640_reg_val_t));
    if (status != OV3640_OK) {
        return status;
    }

    /* Встановлення режимів за замовчуванням: VGA та YUV422 */
    status = ov3640_set_resolution(handle, OV3640_RES_VGA);
    if (status != OV3640_OK) {
        return status;
    }

    status = ov3640_set_format(handle, OV3640_FMT_YUV422);
    if (status != OV3640_OK) {
        return status;
    }

    handle->is_initialized = true;
    return OV3640_OK;
}

ov3640_status_t ov3640_reset(ov3640_handle_t *handle)
{
    if (!handle) {
        return OV3640_ERR_PARAM;
    }

    if (handle->io.set_reset) {
        handle->io.set_reset(true);
        handle->io.delay_ms(10);
        handle->io.set_reset(false);
        handle->io.delay_ms(20);
    }

    /* Програмне скидання через регістр OV3640_REG_SYS_RESET */
    return handle->io.sccb_write(handle->io.sccb_addr, OV3640_REG_SYS_RESET, 0x01);
}

ov3640_status_t ov3640_set_power(ov3640_handle_t *handle, bool enable)
{
    if (!handle) {
        return OV3640_ERR_PARAM;
    }

    if (handle->io.set_pwdn) {
        handle->io.set_pwdn(enable);
        handle->io.delay_ms(5);
    }

    return OV3640_OK;
}

ov3640_status_t ov3640_read_chip_id(ov3640_handle_t *handle, uint16_t *chip_id)
{
    if (!handle || !chip_id) {
        return OV3640_ERR_PARAM;
    }

    uint8_t id_high = 0;
    uint8_t id_low = 0;

    ov3640_status_t status = handle->io.sccb_read(handle->io.sccb_addr, OV3640_REG_CHIP_ID_HIGH, &id_high);
    if (status != OV3640_OK) {
        return status;
    }

    status = handle->io.sccb_read(handle->io.sccb_addr, OV3640_REG_CHIP_ID_LOW, &id_low);
    if (status != OV3640_OK) {
        return status;
    }

    *chip_id = (uint16_t)((id_high << 8) | id_low);
    if (*chip_id != OV3640_CHIP_ID) {
        return OV3640_ERR_ID_MISMATCH;
    }

    return OV3640_OK;
}

ov3640_status_t ov3640_set_resolution(ov3640_handle_t *handle, ov3640_res_t res)
{
    if (!handle) {
        return OV3640_ERR_PARAM;
    }

    const ov3640_reg_val_t *regs = NULL;
    size_t count = 0;

    switch (res) {
    case OV3640_RES_VGA:
        regs = ov3640_res_vga_regs;
        count = sizeof(ov3640_res_vga_regs) / sizeof(ov3640_reg_val_t);
        break;
    case OV3640_RES_1080P:
        regs = ov3640_res_1080p_regs;
        count = sizeof(ov3640_res_1080p_regs) / sizeof(ov3640_reg_val_t);
        break;
    case OV3640_RES_QXGA:
        regs = ov3640_res_qxga_regs;
        count = sizeof(ov3640_res_qxga_regs) / sizeof(ov3640_reg_val_t);
        break;
    default:
        return OV3640_ERR_PARAM;
    }

    ov3640_status_t status = ov3640_write_reg_list(handle, regs, count);
    if (status == OV3640_OK) {
        handle->resolution = res;
    }

    return status;
}

ov3640_status_t ov3640_set_format(ov3640_handle_t *handle, ov3640_format_t fmt)
{
    if (!handle) {
        return OV3640_ERR_PARAM;
    }

    const ov3640_reg_val_t *regs = NULL;
    size_t count = 0;

    if (fmt == OV3640_FMT_YUV422) {
        regs = ov3640_fmt_yuv422_regs;
        count = sizeof(ov3640_fmt_yuv422_regs) / sizeof(ov3640_reg_val_t);
    } else if (fmt == OV3640_FMT_JPEG) {
        regs = ov3640_fmt_jpeg_regs;
        count = sizeof(ov3640_fmt_jpeg_regs) / sizeof(ov3640_reg_val_t);
    } else {
        return OV3640_ERR_PARAM;
    }

    ov3640_status_t status = ov3640_write_reg_list(handle, regs, count);
    if (status == OV3640_OK) {
        handle->format = fmt;
    }

    return status;
}

ov3640_status_t ov3640_write_reg_list(ov3640_handle_t *handle, const ov3640_reg_val_t *list, size_t count)
{
    if (!handle || !list) {
        return OV3640_ERR_PARAM;
    }

    for (size_t i = 0; i < count; i++) {
        ov3640_status_t status = handle->io.sccb_write(handle->io.sccb_addr, list[i].reg, list[i].val);
        if (status != OV3640_OK) {
            return status;
        }
    }

    return OV3640_OK;
}
