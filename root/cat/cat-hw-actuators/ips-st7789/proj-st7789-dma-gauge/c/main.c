/**
 * @file main.c
 * @brief Головний конвеєрний цикл оновлення кадру та апаратне профілювання завантаження CPU.
 *
 * Демонструє паралельну конвеєрну роботу: поки DMA транслює відрендерений рядок
 * у контролер ST7789, процесор формує наступний сканлайн у парний буфер.
 * Стробування тестового виводу GPIO дозволяє виміряти точний час роботи ядра за допомогою
 * осцилографа або логічного аналізатора.
 */

#include "st7789.h"
#include "gauge_renderer.h"

/* --- Апаратні дескриптори мікроконтролера та налаштування пінів --- */

/* Макроси для емуляції/керування апаратними регістрами тестового піна GPIO (профілювання) */
#define PROBE_PIN_PORT_BSRR        (*(volatile uint32_t *)(0x40020018U)) /* STM32 GPIOA BSRR регістр */
#define PROBE_PIN_MASK             (1U << 8U)                            /* Вивід PA8 як індикатор CPU Load */

/* Встановлення виводу PA8 у високий рівень (початок обчислень сканлайну) */
static inline void probe_pin_set_high(void) {
    PROBE_PIN_PORT_BSRR = PROBE_PIN_MASK;
}

/* Скидання виводу PA8 у низький рівень (завершення обчислень сканлайну) */
static inline void probe_pin_set_low(void) {
    PROBE_PIN_PORT_BSRR = (PROBE_PIN_MASK << 16U);
}

/* Екземпляри драйвера, подвійного буфера та стану вимірювального приладу */
static st7789_dev_t g_display;
static ping_pong_buffer_t g_ping_pong;
static gauge_state_t g_gauge;

/* --- Реалізація апаратних функцій зв'язку (HAL) для дисплея --- */

static void platform_cs_write(uint8_t state) {
    /* Керування лінією Chip Select (активний низький) */
    volatile uint32_t *bsrr = (volatile uint32_t *)0x40020018U; /* GPIOA BSRR */
    if (state != 0U) {
        *bsrr = (1U << 4U);        /* PA4 HIGH (деактивація) */
    } else {
        *bsrr = (1U << (4U + 16U)); /* PA4 LOW (активація) */
    }
}

static void platform_dc_write(uint8_t state) {
    /* Керування лінією Data/Command */
    volatile uint32_t *bsrr = (volatile uint32_t *)0x40020018U; /* GPIOA BSRR */
    if (state != 0U) {
        *bsrr = (1U << 1U);        /* PA1 HIGH (Data) */
    } else {
        *bsrr = (1U << (1U + 16U)); /* PA1 LOW (Command) */
    }
}

static void platform_rst_write(uint8_t state) {
    /* Керування апаратним скиданням RESET */
    volatile uint32_t *bsrr = (volatile uint32_t *)0x40020018U; /* GPIOA BSRR */
    if (state != 0U) {
        *bsrr = (1U << 2U);        /* PA2 HIGH */
    } else {
        *bsrr = (1U << (2U + 16U)); /* PA2 LOW (скидання) */
    }
}

static void platform_delay_ms(uint32_t ms) {
    /* Проста калібрована затримка (або виклик таймера/SysTick) */
    for (volatile uint32_t i = 0; i < ms * 16000U; i++) {
        __asm__ volatile ("nop");
    }
}

static void platform_spi_send_blocking(const uint8_t *data, uint16_t len) {
    volatile uint32_t *spi_sr = (volatile uint32_t *)0x40013008U; /* SPI1_SR */
    volatile uint32_t *spi_dr = (volatile uint32_t *)0x4001300CU; /* SPI1_DR */

    for (uint16_t i = 0; i < len; i++) {
        /* Очікуємо звільнення буфера передачі (TXE = 1) */
        while (!(*spi_sr & (1U << 1U))) {}
        *spi_dr = data[i];
    }
    /* Очікуємо закінчення передачі останнього байта (BSY = 0) */
    while (*spi_sr & (1U << 7U)) {}
}

static void platform_spi_send_dma(const uint8_t *data, uint16_t len) {
    /* Регістри контролера DMA2 (Stream 3 для SPI1_TX на Cortex-M) */
    volatile uint32_t *dma_cr   = (volatile uint32_t *)0x40026458U; /* DMA2_S3CR */
    volatile uint32_t *dma_ndtr = (volatile uint32_t *)0x4002645CU; /* DMA2_S3NDTR */
    volatile uint32_t *dma_m0ar = (volatile uint32_t *)0x40026464U; /* DMA2_S3M0AR */
    volatile uint32_t *dma_ifcr = (volatile uint32_t *)0x40026408U; /* DMA2_LIFCR */

    /* Вимикаємо потік DMA перед новим конфігуруванням */
    *dma_cr &= ~1U;
    while (*dma_cr & 1U) {}

    /* Очищаємо всі прапорці переривань для Stream 3 */
    *dma_ifcr = (0x3FU << 22U);

    /* Задаємо адресу джерела пам'яті та кількість байтів */
    *dma_m0ar = (uint32_t)data;
    *dma_ndtr = len;

    /* Вмикаємо переривання завершення передачі (TCIE) та активуємо потік DMA */
    *dma_cr |= (1U << 4U) | 1U;
}

/**
 * @brief Обробник апаратного переривання завершення прямого доступу до пам'яті (DMA ISR).
 * Викликається контролером переривань NVIC після передавання повного рядка на шину SPI.
 */
void DMA2_Stream3_IRQHandler(void) {
    volatile uint32_t *dma_lisr = (volatile uint32_t *)0x40026400U;
    volatile uint32_t *dma_lifcr = (volatile uint32_t *)0x40026408U;

    /* Перевіряємо прапорець завершення трансляції (Stream 3 Transfer Complete Flag) */
    if (*dma_lisr & (1U << 27U)) {
        *dma_lifcr = (1U << 27U); /* Скидаємо апаратний прапорець */

        /* Сповіщаємо драйвер про завершення передачі рядка */
        st7789_dma_transfer_complete_callback(&g_display);
    }
}

/**
 * @brief Емуляція динамічного вхідного сигналу від датчика (тиск, оберти двигуна).
 */
static int16_t simulate_sensor_input(void) {
    static int16_t simulated_val = 0;
    static int8_t direction = 15;

    simulated_val += direction;
    if (simulated_val >= 1000) {
        simulated_val = 1000;
        direction = -15;
    } else if (simulated_val <= 0) {
        simulated_val = 0;
        direction = 15;
    }

    return simulated_val;
}

/**
 * @brief Головна точка входу в програму.
 */
int main(void) {
    /* 1. Ініціалізація апаратної структури HAL */
    const st7789_hal_t hal = {
        .cs_write = platform_cs_write,
        .dc_write = platform_dc_write,
        .rst_write = platform_rst_write,
        .delay_ms = platform_delay_ms,
        .spi_send_blocking = platform_spi_send_blocking,
        .spi_send_dma = platform_spi_send_dma
    };

    /* 2. Ініціалізація контролера дисплея ST7789 */
    st7789_init(&g_display, &hal, ST7789_DEFAULT_X_OFFSET, ST7789_DEFAULT_Y_OFFSET);

    /* 3. Ініціалізація приладу: діапазон шкали 0..1000, фільтр експоненційного демпфування (shift=3) */
    gauge_renderer_init(&g_gauge, 0, 1000, 3U);
    g_ping_pong.write_index = 0U;

    probe_pin_set_low();

    /* 4. Нескінченний конвеєрний цикл виведення кадрів */
    while (1) {
        /* Опитування датчика та розрахунок нового положення стрілки з демпфуванням */
        const int16_t sensor_reading = simulate_sensor_input();
        gauge_update_needle(&g_gauge, sensor_reading);

        /* Налаштовуємо вікно оновлення дисплея на повний кадр 240x240 */
        st7789_set_window(&g_display, 0U, 0U, GAUGE_DISPLAY_WIDTH - 1U, GAUGE_DISPLAY_HEIGHT - 1U);

        /*
         * Конвеєрний сканлайн-рендеринг:
         * Рядок Y рендериться ядром у буфер write_index, у той час як попередній рядок
         * Y-1 асинхронно передається у контролер дисплея через DMA.
         */
        for (uint16_t y = 0; y < GAUGE_DISPLAY_HEIGHT; y++) {
            /* Отримуємо вказівник на активний буфер для малювання */
            uint16_t *current_line = g_ping_pong.buffer[g_ping_pong.write_index];

            /*
             * --- ПРОФІЛЮВАННЯ: ПОЧАТОК РОБОТИ ЯДРА ---
             * Виставляємо тестовий вивід GPIO в 1 перед генерацією пікселів рядка
             */
            probe_pin_set_high();

            /* Генерація рядка Y виключно цілочисельними операціями */
            gauge_render_scanline(&g_gauge, y, current_line);

            /*
             * --- ПРОФІЛЮВАННЯ: КІНЕЦЬ РОБОТИ ЯДРА ---
             * Скидаємо тестовий вивід GPIO в 0 одразу після завершення рендерингу.
             * Ширина імпульсу високого рівня на осцилографі показує точний час зайнятості CPU.
             */
            probe_pin_set_low();

            /*
             * Очікуємо закінчення передавання попереднього рядка через DMA,
             * якщо це не перший рядок кадру (y > 0)
             */
            if (y > 0U) {
                st7789_wait_dma_finish(&g_display);
            }

            /* Запускаємо асинхронне передавання щойно підготовленого рядка */
            st7789_send_line_dma(&g_display, current_line, GAUGE_DISPLAY_WIDTH);

            /* Перемикаємо індекс буфера на протилежний (ping-pong: 0 -> 1 -> 0) */
            g_ping_pong.write_index ^= 1U;
        }

        /* Очікуємо закінчення трансляції останнього (239-го) рядка кадру */
        st7789_wait_dma_finish(&g_display);

        /* Невелика пауза між кадрами для забезпечення стабільної частоти 60 FPS */
        platform_delay_ms(16U);
    }

    return 0;
}
