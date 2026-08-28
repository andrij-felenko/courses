#include "driver/gptimer.h"
#include "driver/gpio.h"
#include "esp_timer.h"

#define ZCD_PIN    GPIO_NUM_4     // вхід від детектора переходу нуля (через оптопару)
#define GATE_PIN   GPIO_NUM_5     // вихід на оптодрайвер симістора (MOC3021 тощо)

#define GATE_PULSE_US   80        // тривалість імпульсу на затвор, мкс
#define HALF_PERIOD_US  10000     // півперіод для 50 Гц = 10 мс = 10000 мкс
#define DELAY_MIN_US    300       // мін. затримка: не смикати впритул до нуля
#define DELAY_MAX_US    9500      // макс. затримка: лишити час защіпнутися до кінця

static gptimer_handle_t g_timer = NULL;

// Затримка від нуля до імпульсу; читається в ISR, тому volatile.
// Стартове значення DELAY_MAX_US = навантаження ВИМКНЕНЕ (безпечний старт).
static volatile uint32_t g_fire_delay_us = DELAY_MAX_US;

// Прапорець "регулятор увімкнено"; поки false — жодних імпульсів на затвор.
static volatile bool g_output_enabled = false;
