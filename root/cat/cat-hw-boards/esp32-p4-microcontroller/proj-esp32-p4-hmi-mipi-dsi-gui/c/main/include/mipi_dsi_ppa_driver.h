#ifndef MIPI_DSI_PPA_DRIVER_H
#define MIPI_DSI_PPA_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Роздільна здатність дисплея за замовчуванням
 */
#define DISPLAY_HORIZONTAL_RESOLUTION  800
#define DISPLAY_VERTICAL_RESOLUTION    480
#define DISPLAY_COLOR_DEPTH_BYTES      2    /* RGB565 - 16 біт на піксель */

/**
 * @brief Вирівнювання кадрових буферів у PSRAM для сумісності з DMA та кешем
 */
#define PPA_PSRAM_ALIGNMENT_BYTES      64

/**
 * @brief Перелічувальний тип режимів пікселів для PPA
 */
typedef enum {
    PPA_COLOR_MODE_RGB565 = 0,
    PPA_COLOR_MODE_RGB888,
    PPA_COLOR_MODE_ARGB8888
} ppa_color_mode_t;

/**
 * @brief Конфігурація таймінгів шини MIPI-DSI (DPHY + DPI)
 */
typedef struct {
    uint32_t clock_lane_freq_mhz;   /*!< Частота тактової лінії MIPI-DSI DPHY в МГц */
    uint8_t  num_data_lanes;        /*!< Кількість ліній даних (1 або 2) */
    uint16_t hsync_pulse_width;     /*!< Ширина імпульсу строчного синхроімпульсу HSYNC */
    uint16_t hsync_back_porch;      /*!< Задній фронт HSYNC (HBP) */
    uint16_t hsync_front_porch;     /*!< Передній фронт HSYNC (HFP) */
    uint16_t vsync_pulse_width;     /*!< Ширина імпульсу кадрового синхроімпульсу VSYNC */
    uint16_t vsync_back_porch;      /*!< Задній фронт VSYNC (VBP) */
    uint16_t vsync_front_porch;     /*!< Передній фронт VSYNC (VFP) */
} mipi_dsi_timing_config_t;

/**
 * @brief Конфігурація параметрів апаратного прискорювача PPA
 */
typedef struct {
    ppa_color_mode_t input_color_mode;  /*!< Вхідний формат кольору пікселів */
    ppa_color_mode_t output_color_mode; /*!< Вихідний формат кольору пікселів */
    bool enable_scaling;                /*!< Прапор активації масштабування */
    bool enable_blending;               /*!< Прапор активації альфа-змішування */
    float scale_factor_x;               /*!< Коефіцієнт масштабування по осі X */
    float scale_factor_y;               /*!< Коефіцієнт масштабування по осі Y */
} ppa_config_t;

/**
 * @brief Дескриптор подвійного фреймбуфера в зовнішній пам'яті PSRAM
 */
typedef struct {
    uint8_t *buffer_1;            /*!< Указник на перший буфер кадру в PSRAM */
    uint8_t *buffer_2;            /*!< Указник на другий буфер кадру в PSRAM */
    size_t buffer_size_bytes;     /*!< Розмір одного буфера кадру в байтах */
    uint32_t width;               /*!< Ширина кадру у пікселях */
    uint32_t height;              /*!< Висота кадру у пікселях */
    volatile uint8_t active_index;/*!< Індекс активного буфера, що виводиться (0 або 1) */
    volatile bool is_busy;        /*!< Прапор зайнятості передачею даних */
} frame_buffer_descriptor_t;

/**
 * @brief Виділення пам'яті для двох кадрових буферів у PSRAM із кеш-вирівнюванням
 *
 * @param fb_desc Указник на дескриптор фреймбуфера
 * @param width Ширина дисплея в пікселях
 * @param height Висота дисплея в пікселях
 * @param bytes_per_pixel Кількість байт на один піксель
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t mipi_dsi_ppa_init_psram_buffers(frame_buffer_descriptor_t *fb_desc,
                                          uint32_t width,
                                          uint32_t height,
                                          uint8_t bytes_per_pixel);

/**
 * @brief Ініціалізація фізичного контролера шини MIPI-DSI та DPHY
 *
 * @param timing_cfg Конфігурація таймінгів MIPI-DSI
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t mipi_dsi_ppa_init_dsi(const mipi_dsi_timing_config_t *timing_cfg);

/**
 * @brief Ініціалізація апаратного прискорювача обробки пікселів PPA
 *
 * @param ppa_cfg Конфігурація PPA
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t mipi_dsi_ppa_init_ppa(const ppa_config_t *ppa_cfg);

/**
 * @brief Виконання апаратного блітингу та масштабування блоку пікселів через PPA
 *
 * @param src_buf Джерельний буфер пікселів
 * @param dst_buf Цільовий буфер кадру у PSRAM
 * @param src_width Ширина джерельної області
 * @param src_height Висота джерельної області
 * @param dst_width Ширина цільової області
 * @param dst_height Висота цільової області
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t mipi_dsi_ppa_blit(const void *src_buf,
                            void *dst_buf,
                            uint32_t src_width,
                            uint32_t src_height,
                            uint32_t dst_width,
                            uint32_t dst_height);

/**
 * @brief Перемикання активного кадрового буфера PSRAM для усунення артефактів Tearing
 *
 * @param fb_desc Указник на дескриптор фреймбуфера
 * @return esp_err_t ESP_OK у разі успіху
 */
esp_err_t mipi_dsi_ppa_swap_and_display(frame_buffer_descriptor_t *fb_desc);

/**
 * @brief Деініціалізація низькорівневого драйвера та звільнення пам'яті PSRAM
 *
 * @param fb_desc Указник на дескриптор фреймбуфера
 */
void mipi_dsi_ppa_deinit(frame_buffer_descriptor_t *fb_desc);

#ifdef __cplusplus
}
#endif

#endif /* MIPI_DSI_PPA_DRIVER_H */
