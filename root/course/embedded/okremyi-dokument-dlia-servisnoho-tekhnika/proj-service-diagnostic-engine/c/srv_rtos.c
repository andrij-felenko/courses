/* srv_rtos.c — сервісний рушій як окрема низькопріоритетна задача FreeRTOS.
   Тут же живуть обидві реалізації захоплення шини: під RTOS це м'ютекс. */

#include "FreeRTOS.h"
#include "queue.h"
#include "semphr.h"
#include "task.h"

#include "hw_port.h"
#include "service_engine.h"

#define RX_QUEUE_LENGTH  256u
#define TASK_STACK_WORDS 1024u
#define POLL_PERIOD_MS   10u

static QueueHandle_t     s_rx_queue;
static SemaphoreHandle_t s_bus_mutex;
static volatile uint32_t s_dropped_bytes; /* байти, які не влізли в чергу */

static void srv_task(void *arg)
{
    (void)arg;
    srv_init(); /* BSP уже піднятий: задача стартує після ініціалізації плати */

    for (;;) {
        char c;
        /* Спершу вибираємо все, що встигло накопичитись, потім один крок
           автомата. Порожня черга блокує задачу на POLL_PERIOD_MS — саме
           стільки триває пауза між перевірками таймерів. */
        while (xQueueReceive(s_rx_queue, &c, pdMS_TO_TICKS(POLL_PERIOD_MS)) == pdTRUE) {
            srv_feed_byte(c);
        }
        srv_poll_step();
    }
}

bool srv_rtos_start(UBaseType_t priority)
{
    s_rx_queue  = xQueueCreate(RX_QUEUE_LENGTH, sizeof(char));
    s_bus_mutex = xSemaphoreCreateMutex();
    if (s_rx_queue == NULL || s_bus_mutex == NULL) {
        return false;
    }
    /* Пріоритет свідомо нижчий за задачі регулювання: діагностика ніколи
       не має права відсунути керування. */
    return xTaskCreate(srv_task, "srv", TASK_STACK_WORDS, NULL, priority, NULL) == pdPASS;
}

/* Викликається з ISR приймача UART: жодного розбору, лише передача байта. */
void srv_uart_rx_isr(char c)
{
    BaseType_t woken = pdFALSE;

    if (xQueueSendFromISR(s_rx_queue, &c, &woken) != pdTRUE) {
        s_dropped_bytes++; /* черга переповнена: рядок однаково піде в брак */
    }
    portYIELD_FROM_ISR(woken);
}

/* ISR апаратного захисту. Знеструмлення робимо прямо тут, без черги:
   чекати на планувальник, коли горить радіатор, ніхто не буде. */
void srv_fault_isr(uint32_t flags)
{
    srv_fault_trip(flags);
}

bool hw_bus_try_lock(uint32_t timeout_ms)
{
    /* Фіксований тайм-аут замість portMAX_DELAY: сервісний тест радше
       відмовиться від шини, ніж застрягне на ній разом із задачею збору. */
    return xSemaphoreTake(s_bus_mutex, pdMS_TO_TICKS(timeout_ms)) == pdTRUE;
}

void hw_bus_unlock(void)
{
    (void)xSemaphoreGive(s_bus_mutex);
}
