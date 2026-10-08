/**
 * @file exti_handler.c
 * @brief Реалізація обробників зовнішніх апаратних переривань EXTI від давачів VL53L0X.
 *
 * Модуль забезпечує фіксацію подій готовності нових даних від виводів INT (GPIO1)
 * і формування неблокуючої черги (кольцового буфера) подій вимірювання для їх
 * безпечної обробки у головному циклі програми без затримок переривань.
 */

#include "vl53l0x_array.h"

#define EXTI_EVENT_QUEUE_SIZE 16U

/**
 * @brief Подія готовності даних від конкретного давача.
 */
typedef struct {
    uint8_t sensor_index;  /**< Індекс давача в масиві */
    uint32_t timestamp_ms; /**< Часова мітка надходження переривання */
} exti_event_t;

/**
 * @brief Кольцовий буфер (Ring Buffer) для асинхронних подій EXTI.
 */
typedef struct {
    exti_event_t queue[EXTI_EVENT_QUEUE_SIZE];
    volatile uint8_t head;
    volatile uint8_t tail;
} exti_ring_buffer_t;

static exti_ring_buffer_t g_exti_queue = { .head = 0, .tail = 0 };
static VL53L0X_Array_t *g_p_array_ctx = NULL;

/**
 * @brief Додавання події у кольцовий буфер з переривання (ISR-safe).
 */
static bool exti_queue_push(uint8_t sensor_idx, uint32_t timestamp)
{
    uint8_t next_head = (g_exti_queue.head + 1U) % EXTI_EVENT_QUEUE_SIZE;
    if (next_head == g_exti_queue.tail) {
        /* Черга переповнена — подія втрачається */
        return false;
    }

    g_exti_queue.queue[g_exti_queue.head].sensor_index = sensor_idx;
    g_exti_queue.queue[g_exti_queue.head].timestamp_ms = timestamp;
    g_exti_queue.head = next_head;
    return true;
}

/**
 * @brief Прив'язка глобального контексту масиву до модуля обробки EXTI.
 * @param arr Вказівник на ініціалізований масив давачів.
 */
void exti_handler_register_array(VL53L0X_Array_t *arr)
{
    g_p_array_ctx = arr;
    g_exti_queue.head = 0;
    g_exti_queue.tail = 0;
}

/**
 * @brief Головна процедура ISR, що викликається при низькорівневому апаратному перериванні EXTI.
 * @param pin_id Ідентифікатор виводу GPIO, який згенерував переривання.
 */
void HAL_GPIO_EXTI_Callback(uint16_t pin_id)
{
    if (g_p_array_ctx == NULL || !g_p_array_ctx->is_initialized) {
        return;
    }

    /* Пошук сенсора, якому належить даний вивід EXTI */
    for (uint8_t i = 0; i < g_p_array_ctx->count; i++) {
        vl53l0x_dev_t *dev = &g_p_array_ctx->dev[i];
        if (dev->exti_pin.pin_id == pin_id) {
            /* Встановлюємо атомарний прапорець готовності для конкретного пристрою */
            dev->data_ready_flag = true;

            /* Заносимо подію у кільцеву чергу */
            exti_queue_push(i, hal_get_tick_ms());
            break;
        }
    }
}

/**
 * @brief Вилучення чергової події із кольцового буфера в суперциклі (неблокуюче).
 * @param p_sensor_idx Вказівник на змінну для запису індексу сенсора.
 * @param p_timestamp Вказівник для збереження мітки часу.
 * @return true якщо подію вилучено, false якщо черга порожня.
 */
bool exti_pop_pending_sensor(uint8_t *p_sensor_idx, uint32_t *p_timestamp)
{
    if (g_exti_queue.head == g_exti_queue.tail) {
        return false; /* Черга порожня */
    }

    *p_sensor_idx = g_exti_queue.queue[g_exti_queue.tail].sensor_index;
    if (p_timestamp != NULL) {
        *p_timestamp = g_exti_queue.queue[g_exti_queue.tail].timestamp_ms;
    }

    g_exti_queue.tail = (g_exti_queue.tail + 1U) % EXTI_EVENT_QUEUE_SIZE;
    return true;
}
