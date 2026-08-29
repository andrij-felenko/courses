/* Той самий поділ праці на ESP-IDF (ESP32).
 *
 * Тут верхніх половин дві, і вони показові саме своєю різницею:
 *  · UART обслуговує обробник самого драйвера IDF — він уже написаний
 *    дисципліновано й віддає нам події через чергу FreeRTOS;
 *  · аварійну лінію ми беремо на себе, і саме тут проявляються всі
 *    обмеження контексту переривання на ESP32 — включно з тим, що код
 *    обробника мусить лежати в IRAM.
 */
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_attr.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "soc/gpio_reg.h"

#define UART_PORT UART_NUM_1
#define UART_TX_PIN 17
#define UART_RX_PIN 16
#define UART_RX_BUF 1024
#define UART_EVENT_QUEUE_LEN 20

#define EMERGENCY_PIN 4  /* оптичний давач кінцевого положення */
#define POWER_GATE_PIN 5 /* дозвіл силового каскаду, активний рівень «1» */

static const char *TAG = "isr-discipline";

static QueueHandle_t s_uart_events;
static QueueHandle_t s_emergency_events;

typedef struct {
    int64_t timestamp_us; /* коли давач спрацював, за годинником esp_timer */
    uint32_t level;
} emergency_event_t;

/* ---------------------------------------------------------------------------
 * ВЕРХНЯ ПОЛОВИНА аварійної лінії.
 *
 * IRAM_ATTR обов'язковий: обробник зареєстровано з ESP_INTR_FLAG_IRAM, тобто
 * він мусить працювати навіть тоді, коли кеш зовнішньої флеш-пам'яті
 * вимкнено (а це стається щоразу під час запису в NVS чи OTA). Обробник поза
 * IRAM у такий момент дає миттєвий крах на читанні власного коду.
 *
 * З тієї ж причини тут немає ні ESP_LOGx, ні gpio_set_level: покладатись на
 * те, що чужа функція теж опинилась в IRAM, не можна. Ніжку гасимо прямим
 * записом у регістр — одна інструкція, жодних залежностей.
 * ------------------------------------------------------------------------ */
static void IRAM_ATTR emergency_isr(void *arg)
{
    (void)arg;

    /* 1. Дія, заради якої переривання й існує: знімаємо дозвіл силового
     *    каскаду. Це має статися ДО будь-якої бухгалтерії. */
    REG_WRITE(GPIO_OUT_W1TC_REG, (1u << POWER_GATE_PIN));

    /* 2. Фіксуємо факт і час — і віддаємо решту роботи фону. */
    const emergency_event_t event = {
        .timestamp_us = esp_timer_get_time(),
        .level = REG_READ(GPIO_IN_REG) & (1u << EMERGENCY_PIN),
    };

    BaseType_t higher_priority_woken = pdFALSE;
    /* Черга може бути повна — це не привід чекати. Втрачене повідомлення
     * гірше за втрачену систему: живлення вже знято. */
    (void)xQueueSendFromISR(s_emergency_events, &event, &higher_priority_woken);

    if (higher_priority_woken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}

/* --------------------------------------------------------------------------
 * НИЖНІ ПОЛОВИНИ: звичайні завдання FreeRTOS.
 * ------------------------------------------------------------------------ */
static void emergency_task(void *arg)
{
    (void)arg;
    emergency_event_t event;

    for (;;) {
        if (xQueueReceive(s_emergency_events, &event, portMAX_DELAY) == pdTRUE) {
            /* Тут уже можна все: журнал, запис у NVS, доповідь по мережі. */
            ESP_LOGW(TAG, "аварія на %lld мкс, рівень %u — живлення знято",
                     (long long)event.timestamp_us, (unsigned)event.level);
        }
    }
}

static void uart_event_task(void *arg)
{
    (void)arg;

    uint8_t chunk[128];
    uart_event_t event;

    for (;;) {
        if (xQueueReceive(s_uart_events, &event, portMAX_DELAY) != pdTRUE) {
            continue;
        }

        switch (event.type) {
        case UART_DATA:
            /* Дані вже лежать у буфері драйвера — забираємо їх у контексті
             * завдання, порціями не більшими за наш стек. */
            while (event.size > 0) {
                const size_t want = event.size > sizeof(chunk) ? sizeof(chunk) : event.size;
                const int got = uart_read_bytes(UART_PORT, chunk, want, pdMS_TO_TICKS(20));
                if (got <= 0) {
                    break;
                }
                /* Місце важкої роботи: розбір протоколу, CRC, запис у Flash. */
                event.size -= (size_t)got;
            }
            break;

        case UART_FIFO_OVF:
        case UART_BUFFER_FULL:
            /* Ми не встигли вичитати — рівно той сценарій, який в статті
             * зветься Overrun. Чесно визнаємо втрату й вирівнюємо потік. */
            ESP_LOGE(TAG, "переповнення приймача: потік розсинхронізовано");
            uart_flush_input(UART_PORT);
            xQueueReset(s_uart_events);
            break;

        case UART_PARITY_ERR:
        case UART_FRAME_ERR:
            ESP_LOGE(TAG, "помилка кадру на лінії");
            break;

        default:
            break;
        }
    }
}

static void uart_setup(void)
{
    const uart_config_t cfg = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &cfg));
    ESP_ERROR_CHECK(uart_set_pin(UART_PORT, UART_TX_PIN, UART_RX_PIN,
                                 UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    ESP_ERROR_CHECK(uart_driver_install(UART_PORT, UART_RX_BUF, 0,
                                        UART_EVENT_QUEUE_LEN, &s_uart_events, 0));

    /* Поріг FIFO: драйвер підніме переривання, назбиравши стільки байтів.
     * Менше значення — швидша реакція й більше входів у обробник;
     * більше — рідші входи й ближче до межі переповнення. */
    ESP_ERROR_CHECK(uart_set_rx_full_threshold(UART_PORT, 64));
}

static void emergency_setup(void)
{
    const gpio_config_t gate = {
        .pin_bit_mask = 1ULL << POWER_GATE_PIN,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&gate));
    ESP_ERROR_CHECK(gpio_set_level(POWER_GATE_PIN, 1));

    const gpio_config_t sensor = {
        .pin_bit_mask = 1ULL << EMERGENCY_PIN,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_NEGEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&sensor));

    s_emergency_events = xQueueCreate(8, sizeof(emergency_event_t));
    configASSERT(s_emergency_events != NULL);

    /* ESP_INTR_FLAG_LEVEL3 — високий апаратний рівень: аварію не має права
     * відкласти ні UART, ні Wi-Fi. IRAM — див. коментар до обробника. */
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM | ESP_INTR_FLAG_LEVEL3));
    ESP_ERROR_CHECK(gpio_isr_handler_add(EMERGENCY_PIN, emergency_isr, NULL));
}

void app_main(void)
{
    uart_setup();
    emergency_setup();

    xTaskCreate(uart_event_task, "uart-rx", 3072, NULL, 10, NULL);
    xTaskCreate(emergency_task, "emergency", 3072, NULL, 20, NULL);
}
