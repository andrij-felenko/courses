#pragma once

#include <stdint.h>
#include "esp_camera.h"

/**
 * @struct CameraPinConfig
 * @brief Структура розподілу апаратних виводів (GPIO) ESP32 для підключення камери OV2640.
 *
 * Описує розпіновку для паралельного відеоінтерфейсу DVP (D0–D7, PCLK, VSYNC, HREF, XCLK),
 * серійної шини управління SCCB (SIOD, SIOC) та додаткових ліній керування живленням і скиданням.
 */
struct CameraPinConfig {
    int pin_pwdn;       ///< GPIO живлення (Power Down), active high/low залежно від плати
    int pin_reset;      ///< GPIO скидання (Reset), -1 якщо не підключено
    int pin_xclk;       ///< GPIO тактового сигналу камери (XCLK)
    int pin_siod;       ///< GPIO шини SCCB SDA (Data)
    int pin_sioc;       ///< GPIO шини SCCB SCL (Clock)

    int pin_d7;         ///< GPIO старшого біту даних DVP D7
    int pin_d6;         ///< GPIO біту даних DVP D6
    int pin_d5;         ///< GPIO біту даних DVP D5
    int pin_d4;         ///< GPIO біту даних DVP D4
    int pin_d3;         ///< GPIO біту даних DVP D3
    int pin_d2;         ///< GPIO біту даних DVP D2
    int pin_d1;         ///< GPIO біту даних DVP D1
    int pin_d0;         ///< GPIO молодшого біту даних DVP D0

    int pin_vsync;      ///< GPIO кадрової синхронізації (VSYNC)
    int pin_href;       ///< GPIO рядкової синхронізації (HREF)
    int pin_pclk;       ///< GPIO піксельного тактування (PCLK)

    /**
     * @brief Отримання стандартної конфігурації пінів для популярного модуля AI-Thinker ESP32-CAM.
     * @return Заповнений об'єкт CameraPinConfig.
     */
    static CameraPinConfig getAiThinkerConfig() {
        CameraPinConfig cfg;
        cfg.pin_pwdn  = 32;
        cfg.pin_reset = -1;
        cfg.pin_xclk  = 0;
        cfg.pin_siod  = 26;
        cfg.pin_sioc  = 27;

        cfg.pin_d7    = 35;
        cfg.pin_d6    = 34;
        cfg.pin_d5    = 39;
        cfg.pin_d4    = 36;
        cfg.pin_d3    = 21;
        cfg.pin_d2    = 19;
        cfg.pin_d1    = 18;
        cfg.pin_d0    = 5;

        cfg.pin_vsync = 25;
        cfg.pin_href  = 23;
        cfg.pin_pclk  = 22;
        return cfg;
    }
};

/**
 * @struct CameraModeConfig
 * @brief Конфігурація режимів роботи камери та параметрів кадрового буфера.
 */
struct CameraModeConfig {
    framesize_t frame_size   = FRAMESIZE_VGA;      ///< Роздільна здатність за замовчуванням (VGA 640x480)
    pixformat_t pixel_format = PIXFORMAT_JPEG;     ///< Формат зображення (JPEG, RGB565, YUV422 тощо)
    int jpeg_quality         = 12;                 ///< Якість JPEG (10 - висока, 63 - низька)
    int fb_count             = 1;                  ///< Кількість кадрових буферів (1 або 2)
    int xclk_freq_hz         = 20000000;           ///< Частота генератора XCLK (20 МГц)
    camera_grab_mode_t grab_mode = CAMERA_GRAB_WHEN_EMPTY; ///< Режим захоплення кадрів
};
