#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "ov3640.h"
#include "dcmi_dma.h"

/**
 * @file main.c
 * @brief Демонстраційна точка входу: послідовна ініціалізація шини SCCB,
 *        налаштування OV3640, конфігурація DCMI/DMA у режимі подвійного буфера
 *        та асинхронне фонове захоплення відеопотоку без блокування ядра.
 */

#define DMA_BUF_SIZE_WORDS   4096   /* 16 кілобайт на один буфер DMA */
#define JPEG_MAX_FRAME_SIZE  65536  /* 64 кілобайти для цілісного JPEG-кадру */

/* Апаратні кільцеві буфери у RAM */
static uint32_t g_dma_buf0[DMA_BUF_SIZE_WORDS];
static uint32_t g_dma_buf1[DMA_BUF_SIZE_WORDS];
static uint8_t  g_jpeg_frame_buf[JPEG_MAX_FRAME_SIZE];

/* Глобальні дескриптори периферії */
static ov3640_handle_t g_ov3640;
static dcmi_dma_handle_t g_dcmi_dma;

/* Симуляція регістрів SCCB та керування GPIO */
static ov3640_status_t mock_sccb_write(uint8_t dev_addr, uint16_t reg, uint8_t data)
{
    (void)dev_addr;
    (void)reg;
    (void)data;
    return OV3640_OK;
}

static ov3640_status_t mock_sccb_read(uint8_t dev_addr, uint16_t reg, uint8_t *data)
{
    (void)dev_addr;
    if (!data) return OV3640_ERR_PARAM;

    if (reg == OV3640_REG_CHIP_ID_HIGH) {
        *data = 0x36;
    } else if (reg == OV3640_REG_CHIP_ID_LOW) {
        *data = 0x40;
    } else {
        *data = 0x00;
    }
    return OV3640_OK;
}

static void mock_set_pwdn(bool active)
{
    (void)active;
}

static void mock_set_reset(bool active)
{
    (void)active;
}

static void mock_delay_ms(uint32_t ms)
{
    (void)ms;
}

/* Зворотні виклики обробки кадрів та помилок */
static void on_frame_complete(const uint8_t *data, size_t length, bool is_jpeg)
{
    (void)data;
    if (is_jpeg) {
        printf("[СИСТЕМА] Успішно захоплено JPEG-кадр. Розмір: %zu байтів.\n", length);
    } else {
        printf("[СИСТЕМА] Успішно захоплено YUV422-кадр. Розмір: %zu байтів.\n", length);
    }
}

static void on_dcmi_error(dcmi_dma_status_t status)
{
    printf("[ПОМИЛКА] Апаратний збій DCMI/DMA, код: %d\n", (int)status);
}

int main(void)
{
    printf("=== Старт ініціалізації відеосистеми OV3640 + DCMI/DMA ===\n");

    /* 1. Налаштування апаратного шар I/O для сенсора OV3640 */
    ov3640_io_t io_config = {
        .sccb_addr = OV3640_SCCB_ADDR_WRITE,
        .sccb_write = mock_sccb_write,
        .sccb_read = mock_sccb_read,
        .set_pwdn = mock_set_pwdn,
        .set_reset = mock_set_reset,
        .delay_ms = mock_delay_ms
    };

    /* 2. Ініціалізація сенсора OV3640 */
    ov3640_status_t ov_status = ov3640_init(&g_ov3640, &io_config);
    if (ov_status != OV3640_OK) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати OV3640, код: %d\n", ov_status);
        return -1;
    }
    printf("[ОК] Сенсор OV3640 успішно ініціалізовано.\n");

    /* 3. Перевірка Chip ID */
    uint16_t chip_id = 0;
    if (ov3640_read_chip_id(&g_ov3640, &chip_id) == OV3640_OK) {
        printf("[ОК] Виявлено сенсор з Chip ID: 0x%04X\n", chip_id);
    }

    /* 4. Конфігурування роздільної здатності VGA та формату JPEG */
    ov3640_set_resolution(&g_ov3640, OV3640_RES_VGA);
    ov3640_set_format(&g_ov3640, OV3640_FMT_JPEG);
    printf("[ОК] Встановлено режим: VGA (640x480), формат: JPEG.\n");

    /* 5. Налаштування периферії DCMI та DMA у режимі Double Buffer Mode */
    dcmi_dma_status_t dcmi_status = dcmi_dma_init(&g_dcmi_dma, g_dma_buf0, g_dma_buf1, DMA_BUF_SIZE_WORDS);
    if (dcmi_status != DCMI_DMA_OK) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати DCMI/DMA, код: %d\n", dcmi_status);
        return -1;
    }

    g_dcmi_dma.frame_complete_cb = on_frame_complete;
    g_dcmi_dma.error_cb = on_dcmi_error;

    /* Прив'язка буфера для виділення JPEG-зображень */
    dcmi_dma_set_jpeg_buffer(&g_dcmi_dma, g_jpeg_frame_buf, JPEG_MAX_FRAME_SIZE);

    /* 6. Запуск потокового захоплення */
    dcmi_dma_start(&g_dcmi_dma);
    printf("[ОК] Потокове апаратне захоплення DCMI/DMA запущено.\n");

    /* 7. Демонстраційний головний цикл виконання */
    uint32_t iteration = 0;
    while (iteration < 5) {
        /* Симуляція надходження переривань DMA та DCMI у фоновому режимі */
        /* У реальній системі це виконується апаратно перериваннями NVIC */
        dcmi_dma_irq_handler_dcmi(&g_dcmi_dma);
        dcmi_dma_irq_handler_dma(&g_dcmi_dma);

        /* Основне ядро процесора повністю вільне для інших обчислювальних задач */
        iteration++;
    }

    /* Зупинка захоплення */
    dcmi_dma_stop(&g_dcmi_dma);
    printf("=== Роботу відеосистеми завершено успішно ===\n");

    return 0;
}
