#include "lvgl.h"
#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "semphr.h"

#define LCD_HOR_RES     320
#define LCD_VER_RES     240
#define LCD_BUF_LINES   24    /* 1/10 висоти екрана */
#define LCD_BUF_SIZE    (LCD_HOR_RES * LCD_BUF_LINES)

/* Апаратні дескриптори периферії */
extern SPI_HandleTypeDef hspi1;
extern DMA_HandleTypeDef hdma_spi1_tx;

/* Буфери рендерингу: обов'язкове вирівнювання за 32-байтною лінією кешу */
static lv_color_t __attribute__((aligned(32))) buf1[LCD_BUF_SIZE];
static lv_color_t __attribute__((aligned(32))) buf2[LCD_BUF_SIZE];

static lv_disp_draw_buf_t draw_buf;
static lv_disp_drv_t      disp_drv;

/* Семафор блокування доступу до апаратної шини SPI */
static SemaphoreHandle_t spi_mutex = NULL;

/* Допоміжні функції атомарного керування лініями дисплея */
static inline void lcd_cs_low(void)   { GPIOB->BSRR = (1 << (6 + 16)); }
static inline void lcd_cs_high(void)  { GPIOB->BSRR = (1 << 6); }
static inline void lcd_dc_cmd(void)   { GPIOB->BSRR = (1 << (7 + 16)); }
static inline void lcd_dc_data(void)  { GPIOB->BSRR = (1 << 7); }

static void lcd_send_cmd(uint8_t cmd)
{
    lcd_dc_cmd();
    lcd_cs_low();
    HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
    lcd_cs_high();
}

static void lcd_send_data(const uint8_t *data, uint16_t len)
{
    lcd_dc_data();
    lcd_cs_low();
    HAL_SPI_Transmit(&hspi1, (uint8_t*)data, len, HAL_MAX_DELAY);
    lcd_cs_high();
}

static void lcd_set_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    uint8_t caset[4] = { (uint8_t)(x1 >> 8), (uint8_t)(x1 & 0xFF),
                         (uint8_t)(x2 >> 8), (uint8_t)(x2 & 0xFF) };
    uint8_t raset[4] = { (uint8_t)(y1 >> 8), (uint8_t)(y1 & 0xFF),
                         (uint8_t)(y2 >> 8), (uint8_t)(y2 & 0xFF) };

    lcd_send_cmd(0x2A); /* Column Address Set: встановлення меж X */
    lcd_send_data(caset, 4);

    lcd_send_cmd(0x2B); /* Row Address Set: встановлення меж Y */
    lcd_send_data(raset, 4);

    lcd_send_cmd(0x2C); /* Memory Write: перехід у режим запису пікселів */
}

/* Зворотний виклик скидання растрового буфера в дисплей через DMA */
static void disp_flush_cb(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p)
{
    uint32_t pixel_count = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);
    uint32_t byte_count  = pixel_count * sizeof(lv_color_t);

    /* Захоплюємо апаратну шину SPI перед конфігурацією вікна */
    xSemaphoreTake(spi_mutex, portMAX_DELAY);

    /* 1. Задаємо координати прямокутного вікна оновлення */
    lcd_set_window(area->x1, area->y1, area->x2, area->y2);

    /* 2. Переводимо лінію DC у режим даних і активуємо лінію CS */
    lcd_dc_data();
    lcd_cs_low();

    /* 3. Очищення кешу даних Cortex-M7 (скидання брудних рядків у фізичну SRAM) */
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    SCB_CleanDCache_by_Addr((uint32_t*)color_p, (int32_t)byte_count);
#endif

    /* 4. Запуск неблокуючої транзакції DMA */
    HAL_SPI_Transmit_DMA(&hspi1, (uint8_t*)color_p, (uint16_t)byte_count);
}

/* Обробник переривання завершення передачі DMA */
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
    if (hspi->Instance == SPI1) {
        /* Деактивуємо вибір чипа після закінчення транзакції */
        lcd_cs_high();

        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(spi_mutex, &xHigherPriorityTaskWoken);

        /* Інформуємо графічне ядро: поточний буфер вільний для наступного рендерингу */
        lv_disp_flush_ready(&disp_drv);

        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

void gui_init(void)
{
    spi_mutex = xSemaphoreCreateMutex();

    lv_init();

    /* Реєстрація двох буферів у дескрипторі малювання */
    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, LCD_BUF_SIZE);

    /* Конфігурація та реєстрація HAL-драйвера дисплея */
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res  = LCD_HOR_RES;
    disp_drv.ver_res  = LCD_VER_RES;
    disp_drv.flush_cb = disp_flush_cb;
    disp_drv.draw_buf = &draw_buf;

    lv_disp_drv_register(&disp_drv);
}

/* Фонова графічна задача FreeRTOS */
void gui_task(void *pvParameters)
{
    (void)pvParameters;
    gui_init();

    TickType_t last_wake = xTaskGetTickCount();
    while (1) {
        /* Обробка черги таймерів, анімацій та виклик рендерингу */
        lv_timer_handler();
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(5));
    }
}
