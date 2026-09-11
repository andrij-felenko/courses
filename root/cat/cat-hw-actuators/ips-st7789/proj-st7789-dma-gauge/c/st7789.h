/**
 * @file st7789.h
 * @brief Драйвер кольорового IPS-дисплея 1.3" 240x240 на контролері ST7789 (SPI + DMA).
 *
 * Модуль містить список регістрів і команд контролера ST7789, опис бітів конфігурації,
 * структуру апаратних викликів (HAL), налаштування вікна виведення та інтерфейс
 * асинхронного передавання графічних рядків через прямий доступ до пам'яті (DMA).
 */

#ifndef ST7789_H
#define ST7789_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* --- Фізичні розміри панелі та зміщення контролера --- */
#define ST7789_WIDTH               240U
#define ST7789_HEIGHT              240U

/*
 * Більшість модулів 1.3" 240x240 використовують матрицю ST7789, де драйверне поле
 * має розмір 240x320. Залежно від трасування шлейфа зміщення за рядками може становити 0 або 80.
 */
#define ST7789_DEFAULT_X_OFFSET    0U
#define ST7789_DEFAULT_Y_OFFSET    0U

/* --- Команди контролера ST7789 --- */
#define ST7789_CMD_NOP             0x00U /* Немає операції */
#define ST7789_CMD_SWRESET         0x01U /* Програмне скидання логіки */
#define ST7789_CMD_SLPIN           0x10U /* Перехід у режим сну */
#define ST7789_CMD_SLPOUT          0x11U /* Вихід із режиму сну */
#define ST7789_CMD_NORON           0x13U /* Увімкнення нормального режиму відтворення */
#define ST7789_CMD_INVOFF          0x20U /* Вимкнення інверсії кольору */
#define ST7789_CMD_INVON           0x21U /* Увімкнення інверсії (необхідно для IPS) */
#define ST7789_CMD_DISPOFF         0x28U /* Вимкнення матриці дисплея */
#define ST7789_CMD_DISPON          0x29U /* Увімкнення матриці дисплея */
#define ST7789_CMD_CASET           0x2AU /* Встановлення діапазону стовпчиків (Column Address) */
#define ST7789_CMD_RASET           0x2BU /* Встановлення діапазону рядків (Row Address) */
#define ST7789_CMD_RAMWR           0x2CU /* Початок потокового запису у відеопам'ять (GRAM) */
#define ST7789_CMD_MADCTL          0x36U /* Керування порядком сканування осей (Memory Data Access) */
#define ST7789_CMD_COLMOD          0x3AU /* Вибір формату пікселя (Interface Pixel Format) */
#define ST7789_CMD_PORCTRL         0xB2U /* Налаштування гасіння рядків (Porch Setting) */
#define ST7789_CMD_GCTRL           0xB7U /* Керування напругою затворів (Gate Control) */
#define ST7789_CMD_VCOMS           0xBBU /* Встановлення рівня VCOM */
#define ST7789_CMD_LCMCTRL         0xC0U /* Налаштування керування живленням LCM */
#define ST7789_CMD_VDVVRHEN        0xC2U /* Дозвіл запису параметрів VDV і VRH */
#define ST7789_CMD_VRHS            0xC3U /* Регулювання напруги VRH */
#define ST7789_CMD_VDVS            0xC4U /* Регулювання напруги VDV */
#define ST7789_CMD_FRCTRL2         0xC6U /* Налаштування частоти кадру в нормальному режимі */
#define ST7789_CMD_PWCTRL1         0xD0U /* Керування живленням AVDD/AVCL/VDS */
#define ST7789_CMD_PVGAMCTRL       0xE0U /* Позитивна гамма-корекція (14 байтів) */
#define ST7789_CMD_NVGAMCTRL       0xE1U /* Негативна гамма-корекція (14 байтів) */

/* --- Біти регістру MADCTL (0x36) --- */
#define ST7789_MADCTL_MY           0x80U /* Дзеркальне відображення по осі Y */
#define ST7789_MADCTL_MX           0x40U /* Дзеркальне відображення по осі X */
#define ST7789_MADCTL_MV           0x20U /* Обмін осей X/Y (альбомна орієнтація) */
#define ST7789_MADCTL_ML           0x10U /* Вертикальне оновлення від низу до верху */
#define ST7789_MADCTL_BGR          0x08U /* Порядок кольорів BGR замість RGB */

/* --- Формат пікселів (COLMOD 0x3A) --- */
#define ST7789_COLOR_MODE_16BIT    0x55U /* 16 біт на піксель (RGB565) */
#define ST7789_COLOR_MODE_18BIT    0x66U /* 18 біт на піксель (RGB666) */

/*
 * Макрос упаковки RGB888 у 16-бітний RGB565.
 * Контролер ST7789 на шині SPI очікує дані пікселів у форматі Big-Endian (старший байт першим).
 * Оскільки мікроконтролери ARM Cortex-M зберігають uint16_t у форматі Little-Endian,
 * функція упаковки одразу міняє байти місцями, дозволяючи передавати буфер по DMA
 * без додаткової побайної конвертації у процесорі.
 */
#define COLOR_RGB565(r, g, b) \
    ((uint16_t)(((((uint16_t)(r) & 0xF8U) | (((uint16_t)(g) & 0xE0U) >> 5U))) | \
                (((((uint16_t)(g) & 0x1CU) << 11U) | (((uint16_t)(b) & 0xF8U) << 5U)))))

/* Базові попередньо упаковані кольори */
#define COLOR_BLACK                0x0000U
#define COLOR_WHITE                0xFFFFU
#define COLOR_RED                  COLOR_RGB565(255U, 0U, 0U)
#define COLOR_GREEN                COLOR_RGB565(0U, 255U, 0U)
#define COLOR_BLUE                 COLOR_RGB565(0U, 0U, 255U)
#define COLOR_YELLOW               COLOR_RGB565(255U, 255U, 0U)
#define COLOR_CYAN                 COLOR_RGB565(0U, 255U, 255U)
#define COLOR_DARKGRAY             COLOR_RGB565(35U, 35U, 40U)

/**
 * @brief Структура платформно-залежних функцій низького рівня (HAL).
 * Надається користувачем для прив'язки драйвера до конкретного мікроконтролера та периферії.
 */
typedef struct {
    void (*cs_write)(uint8_t state);                               /**< Керування лінією вибору кристала CS (активний 0) */
    void (*dc_write)(uint8_t state);                               /**< Керування лінією Data/Command (0 = команда, 1 = дані) */
    void (*rst_write)(uint8_t state);                              /**< Керування апаратним скиданням RESET (активний 0) */
    void (*delay_ms)(uint32_t ms);                                 /**< Системна затримка в мілісекундах */
    void (*spi_send_blocking)(const uint8_t *data, uint16_t len);  /**< Блокуюче надсилання байтів через SPI */
    void (*spi_send_dma)(const uint8_t *data, uint16_t len);       /**< Асинхронне надсилання блоку даних через SPI DMA */
} st7789_hal_t;

/**
 * @brief Екземпляр дескриптора дисплея ST7789.
 */
typedef struct {
    st7789_hal_t hal;              /**< Таблиця функціональних викликів апаратного рівня */
    uint16_t width;                /**< Робоча ширина видимої області */
    uint16_t height;               /**< Робоча висота видимої області */
    uint16_t x_offset;             /**< Апаратне зміщення по стовпчиках */
    uint16_t y_offset;             /**< Апаратне зміщення по рядках */
    volatile bool dma_busy;        /**< Прапорець активної трансляції каналу DMA */
} st7789_dev_t;

/**
 * @brief Ініціалізація дисплея, апаратне скидання та завантаження конфігураційних регістрів.
 * @param dev Вказівник на дескриптор дисплея.
 * @param hal Вказівник на заповнену структуру апаратних викликів.
 * @param x_offset Зміщення матриці по X (зазвичай 0).
 * @param y_offset Зміщення матриці по Y (0 або 80 залежно від модуля).
 */
void st7789_init(st7789_dev_t *dev, const st7789_hal_t *hal, uint16_t x_offset, uint16_t y_offset);

/**
 * @brief Встановлення прямокутної адресної області запису у відеопам'ять (CASET / RASET).
 * Після виклику контролер автоматично переводиться у режим прийому піксельних даних (RAMWR).
 * @param dev Вказівник на дескриптор дисплея.
 * @param x0 Початковий стовпчик (0..width-1).
 * @param y0 Початковий рядок (0..height-1).
 * @param x1 Кінцевий стовпчик (0..width-1).
 * @param y1 Кінцевий рядок (0..height-1).
 */
void st7789_set_window(st7789_dev_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);

/**
 * @brief Асинхронний запуск передавання рядка пікселів через SPI DMA.
 * Функція не блокує виконання процесора і повертає керування одразу після запуску каналу DMA.
 * @param dev Вказівник на дескриптор дисплея.
 * @param line_buffer Вказівник на масив пікселів uint16_t у форматі RGB565.
 * @param pixel_count Кількість пікселів для передавання (наприклад, 240).
 */
void st7789_send_line_dma(st7789_dev_t *dev, const uint16_t *line_buffer, uint16_t pixel_count);

/**
 * @brief Перевірка стану готовності каналу DMA.
 * @param dev Вказівник на дескриптор дисплея.
 * @return true — DMA зайнятий передаванням даних, false — канал вільний.
 */
bool st7789_is_busy(const st7789_dev_t *dev);

/**
 * @brief Блокуюче очікування завершення поточної асинхронної передачі DMA.
 * @param dev Вказівник на дескриптор дисплея.
 */
void st7789_wait_dma_finish(volatile st7789_dev_t *dev);

/**
 * @brief Обробник завершення передавання DMA (Transfer Complete).
 * Мусить викликатися всередині відповідного переривання мікроконтролера (DMA ISR).
 * @param dev Вказівник на дескриптор дисплея.
 */
void st7789_dma_transfer_complete_callback(st7789_dev_t *dev);

#ifdef __cplusplus
}
#endif

#endif /* ST7789_H */
