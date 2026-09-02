#define _POSIX_C_SOURCE 200809L

#include "rtos_port.h"

#if defined(SYS_PORT_FREERTOS)

#include "task.h"
#include "stm32f4xx.h"   /* CoreDebug, DWT, SystemCoreClock */

/* Лічильник тактів ядра Cortex-M: єдине джерело мікросекунд без переривань. */
static void dwt_enable(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0U;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

static void dwt_delay_us(uint32_t period_us)
{
    const uint32_t start = DWT->CYCCNT;
    const uint32_t ticks = period_us * (SystemCoreClock / 1000000U);
    /* Різниця беззнакових чисел коректна навіть на переповненні лічильника. */
    while ((DWT->CYCCNT - start) < ticks) {
        __NOP();
    }
}

bool sys_mutex_init(sys_mutex_t *m)
{
    *m = xSemaphoreCreateMutex();
    return *m != NULL;
}

void sys_mutex_destroy(sys_mutex_t *m)
{
    if (*m != NULL) {
        vSemaphoreDelete(*m);
        *m = NULL;
    }
}

bool sys_mutex_lock(sys_mutex_t *m)
{
    return xSemaphoreTake(*m, portMAX_DELAY) == pdTRUE;
}

void sys_mutex_unlock(sys_mutex_t *m)
{
    (void)xSemaphoreGive(*m);
}

void sys_delay_us(uint32_t period_us)
{
    if (period_us >= SYS_LONG_DELAY_US) {
        /* Мілісекунди й більше: віддаємо процесор іншим задачам.
           Округлення вгору — чип має право на паузу довшу, ніж просив. */
        vTaskDelay(pdMS_TO_TICKS((period_us + 999U) / 1000U));
    } else {
        /* Одиниці-сотні мікросекунд: перемикання контексту коштувало б
           більше за саму паузу, тому крутимося на лічильнику тактів. */
        if ((DWT->CTRL & DWT_CTRL_CYCCNTENA_Msk) == 0U) {
            dwt_enable();
        }
        dwt_delay_us(period_us);
    }
}

uint32_t sys_uptime_ms(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

#else /* хостова збірка для модульних тестів */

#include <errno.h>
#include <time.h>

static uint64_t mono_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

bool sys_mutex_init(sys_mutex_t *m)
{
    return pthread_mutex_init(m, NULL) == 0;
}

void sys_mutex_destroy(sys_mutex_t *m)
{
    (void)pthread_mutex_destroy(m);
}

bool sys_mutex_lock(sys_mutex_t *m)
{
    return pthread_mutex_lock(m) == 0;
}

void sys_mutex_unlock(sys_mutex_t *m)
{
    (void)pthread_mutex_unlock(m);
}

void sys_delay_us(uint32_t period_us)
{
    if (period_us >= SYS_LONG_DELAY_US) {
        struct timespec ts;
        ts.tv_sec = (time_t)(period_us / 1000000U);
        ts.tv_nsec = (long)(period_us % 1000000U) * 1000L;
        /* Сигнал може обірвати сон — добираємо залишок, а не мовчки коротшаємо. */
        while (nanosleep(&ts, &ts) == -1 && errno == EINTR) {
        }
    } else {
        /* Хостовий відповідник циклу DWT: активне очікування. */
        const uint64_t deadline = mono_ns() + (uint64_t)period_us * 1000ULL;
        while (mono_ns() < deadline) {
        }
    }
}

uint32_t sys_uptime_ms(void)
{
    return (uint32_t)(mono_ns() / 1000000ULL);
}

#endif
