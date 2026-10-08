#include "dcmi_dma.h"
#include <string.h>

/**
 * @file dcmi_dma.c
 * @brief Реалізація подвійного буферизування DMA, обробників переривань DCMI
 *        та неблокуючого виявлення маркерів SOI/EOI для JPEG.
 */

/* Симуляція регістрів апаратної периферії DCMI та DMA для автономності */
typedef struct {
    volatile uint32_t CR;   /* Control Register */
    volatile uint32_t SR;   /* Status Register */
    volatile uint32_t RIS;  /* Raw Interrupt Status */
    volatile uint32_t IER;  /* Interrupt Enable Register */
    volatile uint32_t ICR;  /* Interrupt Clear Register */
} DCMI_TypeDef;

typedef struct {
    volatile uint32_t CR;   /* DMA Stream Control Register */
    volatile uint32_t NDTR; /* Number of Data Items Register */
    volatile uint32_t M0AR; /* Memory 0 Address Register */
    volatile uint32_t M1AR; /* Memory 1 Address Register */
} DMA_Stream_TypeDef;

static DCMI_TypeDef DCMI_Peripheral;
static DMA_Stream_TypeDef DMA_Stream_Peripheral;

dcmi_dma_status_t dcmi_dma_init(dcmi_dma_handle_t *handle, uint32_t *buf0, uint32_t *buf1, size_t buf_size_words)
{
    if (!handle || !buf0 || !buf1 || buf_size_words == 0) {
        return DCMI_DMA_ERR_PARAM;
    }

    memset(handle, 0, sizeof(dcmi_dma_handle_t));

    /* Налаштування подвійного буфера */
    handle->double_buf.buf0 = buf0;
    handle->double_buf.buf1 = buf1;
    handle->double_buf.buf_size_words = buf_size_words;
    handle->double_buf.active_buf = DCMI_DMA_BUF_0;

    /* Початкові параметри сигналів DCMI (активні низькі/високі) */
    handle->hw_config.pclk_polarity = 1;  /* Наростаючий фронт PCLK */
    handle->hw_config.hsync_polarity = 0; /* Активний низький HSYNC */
    handle->hw_config.vsync_polarity = 0; /* Активний низький VSYNC */
    handle->hw_config.byte_swap = false;

    handle->state = FRAME_STATE_IDLE;
    handle->is_jpeg_mode = false;

    /* Конфігурація симульованих регістрів периферії */
    DCMI_Peripheral.CR = (1 << 14); /* DCMI Enable */
    DCMI_Peripheral.IER = (1 << 0) | (1 << 1) | (1 << 2); /* FRAME, OVR, LINE interrupts */

    DMA_Stream_Peripheral.CR = (1 << 18) | (1 << 8); /* Double Buffer Mode + Circular Mode */
    DMA_Stream_Peripheral.M0AR = (uintptr_t)buf0;
    DMA_Stream_Peripheral.M1AR = (uintptr_t)buf1;
    DMA_Stream_Peripheral.NDTR = (uint32_t)buf_size_words;

    return DCMI_DMA_OK;
}

dcmi_dma_status_t dcmi_dma_start(dcmi_dma_handle_t *handle)
{
    if (!handle || !handle->double_buf.buf0 || !handle->double_buf.buf1) {
        return DCMI_DMA_ERR_PARAM;
    }

    handle->state = FRAME_STATE_CAPTURING;
    handle->double_buf.active_buf = DCMI_DMA_BUF_0;

    /* Запуск DMA та підхоплення захоплення кадрів DCMI */
    DMA_Stream_Peripheral.CR |= (1 << 0); /* Enable DMA Stream */
    DCMI_Peripheral.CR |= (1 << 0);       /* Capture Enable */

    return DCMI_DMA_OK;
}

dcmi_dma_status_t dcmi_dma_stop(dcmi_dma_handle_t *handle)
{
    if (!handle) {
        return DCMI_DMA_ERR_PARAM;
    }

    DCMI_Peripheral.CR &= ~(1 << 0);       /* Disable Capture */
    DMA_Stream_Peripheral.CR &= ~(1 << 0); /* Disable DMA Stream */

    handle->state = FRAME_STATE_IDLE;
    return DCMI_DMA_OK;
}

void dcmi_dma_set_jpeg_buffer(dcmi_dma_handle_t *handle, uint8_t *out_buf, size_t max_size)
{
    if (!handle) {
        return;
    }

    handle->jpeg_parser.jpeg_out_buf = out_buf;
    handle->jpeg_parser.jpeg_max_size = max_size;
    handle->is_jpeg_mode = true;
    dcmi_dma_reset_jpeg_parser(handle);
}

void dcmi_dma_reset_jpeg_parser(dcmi_dma_handle_t *handle)
{
    if (!handle) {
        return;
    }

    handle->jpeg_parser.jpeg_actual_size = 0;
    handle->jpeg_parser.is_soi_found = false;
    handle->jpeg_parser.is_eoi_found = false;
    handle->jpeg_parser.last_byte = 0x00;
}

void dcmi_dma_irq_handler_dcmi(dcmi_dma_handle_t *handle)
{
    if (!handle) {
        return;
    }

    uint32_t flags = DCMI_Peripheral.RIS;

    /* Обробка події переповнення буфера (Overrun Error) */
    if (flags & (1 << 1)) {
        DCMI_Peripheral.ICR = (1 << 1); /* Очищення прапорця OVR */
        handle->overrun_count++;
        handle->state = FRAME_STATE_OVERRUN;
        if (handle->error_cb) {
            handle->error_cb(DCMI_DMA_ERR_OVERRUN);
        }
    }

    /* Обробка завершення рядка (Line Event) */
    if (flags & (1 << 2)) {
        DCMI_Peripheral.ICR = (1 << 2); /* Очищення прапорця LINE */
        handle->line_count++;
    }

    /* Обробка завершення кадру (Frame Event) */
    if (flags & (1 << 0)) {
        DCMI_Peripheral.ICR = (1 << 0); /* Очищення прапорця FRAME */
        handle->frame_count++;

        if (!handle->is_jpeg_mode) {
            handle->state = FRAME_STATE_READY;
            if (handle->frame_complete_cb) {
                size_t frame_bytes = handle->double_buf.buf_size_words * sizeof(uint32_t);
                uint8_t *active_data = (handle->double_buf.active_buf == DCMI_DMA_BUF_0) ?
                                        (uint8_t *)handle->double_buf.buf0 : (uint8_t *)handle->double_buf.buf1;
                handle->frame_complete_cb(active_data, frame_bytes, false);
            }
        }
    }
}

void dcmi_dma_irq_handler_dma(dcmi_dma_handle_t *handle)
{
    if (!handle) {
        return;
    }

    /* Перевірка активного буфера в режимі Double Buffer Mode (CT-біт у CR) */
    uint32_t filled_buf_index = handle->double_buf.active_buf;

    /* Перемикання індексу активного буфера hardware DMA */
    if (filled_buf_index == DCMI_DMA_BUF_0) {
        handle->double_buf.active_buf = DCMI_DMA_BUF_1;
    } else {
        handle->double_buf.active_buf = DCMI_DMA_BUF_0;
    }

    /* Вказівник на дані в буфері, заповненому DMA */
    const uint8_t *filled_data = (filled_buf_index == DCMI_DMA_BUF_0) ?
                                 (const uint8_t *)handle->double_buf.buf0 :
                                 (const uint8_t *)handle->double_buf.buf1;
    size_t chunk_bytes = handle->double_buf.buf_size_words * sizeof(uint32_t);

    /* Якщо активний режим JPEG, аналізуємо наявність маркерів SOI та EOI */
    if (handle->is_jpeg_mode) {
        bool frame_done = dcmi_dma_process_jpeg_chunk(handle, filled_data, chunk_bytes);
        if (frame_done && handle->frame_complete_cb) {
            handle->state = FRAME_STATE_READY;
            handle->frame_complete_cb(handle->jpeg_parser.jpeg_out_buf,
                                     handle->jpeg_parser.jpeg_actual_size,
                                     true);
            dcmi_dma_reset_jpeg_parser(handle);
        }
    }
}

bool dcmi_dma_process_jpeg_chunk(dcmi_dma_handle_t *handle, const uint8_t *chunk, size_t chunk_size)
{
    if (!handle || !chunk || chunk_size == 0) {
        return false;
    }

    jpeg_parser_ctx_t *parser = &handle->jpeg_parser;
    if (!parser->jpeg_out_buf || parser->jpeg_max_size == 0) {
        return false;
    }

    for (size_t i = 0; i < chunk_size; i++) {
        uint8_t current_byte = chunk[i];

        /* Перевірка на маркер SOI (0xFFD8) */
        if (!parser->is_soi_found) {
            if (parser->last_byte == JPEG_MARKER_PREFIX && current_byte == JPEG_MARKER_SOI) {
                parser->is_soi_found = true;
                parser->jpeg_actual_size = 0;
                /* Запис перших двох байтів SOI у буфер кадру */
                parser->jpeg_out_buf[parser->jpeg_actual_size++] = JPEG_MARKER_PREFIX;
                parser->jpeg_out_buf[parser->jpeg_actual_size++] = JPEG_MARKER_SOI;
            }
        } else {
            /* Запис байта в вихідний буфер з перевіркою на переповнення */
            if (parser->jpeg_actual_size < parser->jpeg_max_size) {
                parser->jpeg_out_buf[parser->jpeg_actual_size++] = current_byte;
            } else {
                /* Переповнення вихідного буфера JPEG */
                dcmi_dma_reset_jpeg_parser(handle);
                return false;
            }

            /* Перевірка на маркер EOI (0xFFD9) */
            if (parser->last_byte == JPEG_MARKER_PREFIX && current_byte == JPEG_MARKER_EOI) {
                parser->is_eoi_found = true;
                parser->last_byte = current_byte;
                return true; /* Кадр повністю виділено */
            }
        }

        parser->last_byte = current_byte;
    }

    return false;
}
