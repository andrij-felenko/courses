#include "busy_wait_trap.h"

#include "FreeRTOS.h"
#include "task.h"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_i2c.h"
#include "stm32f4xx_ll_usart.h"

#include "../spsc_ring.h"

#define SENSOR_ADDR_7BIT 0x48u
#define I2C_TIMEOUT_MS 20u
#define RELAY_TASK_STACK_WORDS 256u

static spsc_ring_buffer_t s_relay_ring;
static TaskHandle_t s_relay_task = NULL;
static StaticTask_t s_relay_tcb;
static StackType_t s_relay_stack[RELAY_TASK_STACK_WORDS];

static volatile uint32_t s_relay_dropped;
static volatile uint32_t s_relay_bus_errors;
static volatile uint32_t s_relay_timeouts;

/* ===========================================================================
 * ТАК РОБИТИ НЕ МОЖНА.
 *
 * Функція навмисно не називається USART2_IRQHandler і нікуди не підключена:
 * вона тут як експонат. Якби вона стояла у векторі, один затиснутий до землі
 * SDA — і ядро назавжди залишилось би всередині while, з погашеними
 * перериваннями свого й нижчих рівнів. Аварійна лінія в такій системі
 * не спрацює вже ніколи.
 * ======================================================================== */
void usart2_isr_trap_never_link(void)
{
    if (LL_USART_IsActiveFlag_RXNE(USART2)) {
        const uint8_t data = LL_USART_ReceiveData8(USART2);

        /* Умова виходу залежить від ЗОВНІШНЬОЇ мікросхеми. Обробник
         * переривання не має права ставити свою тривалість у залежність
         * від чужого дроту. */
        while (!LL_I2C_IsActiveFlag_TXE(I2C1)) {
            /* тут система і залишається назавжди */
        }
        LL_I2C_TransmitData8(I2C1, data);
    }
}

/* ===========================================================================
 * ТАК ТРЕБА. Обробник лише забирає байт і кладе його в кільце; чекати
 * на шину буде фонове завдання, якому чекати дозволено.
 * ======================================================================== */
void usart2_relay_isr(void)
{
    BaseType_t higher_priority_woken = pdFALSE;

    if (LL_USART_IsActiveFlag_ORE(USART2)) {
        LL_USART_ClearFlag_ORE(USART2);
    }

    while (LL_USART_IsActiveFlag_RXNE(USART2)) {
        const uint8_t data = LL_USART_ReceiveData8(USART2);
        if (!ring_buffer_push_isr(&s_relay_ring, data)) {
            s_relay_dropped++;
        }
    }

    if (s_relay_task != NULL) {
        vTaskNotifyGiveFromISR(s_relay_task, &higher_priority_woken);
    }
    portYIELD_FROM_ISR(higher_priority_woken);
}

/* Те саме очікування прапорця — але в контексті завдання, з кінцевим
 * терміном і з поверненням керування планувальнику на кожній ітерації.
 * Тут воно законне: поки ми чекаємо, система живе далі. */
#define WAIT_FLAG(cond, deadline)                                    \
    do {                                                             \
        while (!(cond)) {                                            \
            if (LL_I2C_IsActiveFlag_BERR(I2C1)) {                    \
                LL_I2C_ClearFlag_BERR(I2C1);                         \
                LL_I2C_GenerateStopCondition(I2C1);                  \
                s_relay_bus_errors++;                                \
                return I2C_BUS_ERROR;                                \
            }                                                        \
            if (LL_I2C_IsActiveFlag_AF(I2C1)) {                      \
                LL_I2C_ClearFlag_AF(I2C1);                           \
                LL_I2C_GenerateStopCondition(I2C1);                  \
                s_relay_bus_errors++;                                \
                return I2C_BUS_ERROR;                                \
            }                                                        \
            if (xTaskGetTickCount() > (deadline)) {                  \
                LL_I2C_GenerateStopCondition(I2C1);                  \
                s_relay_timeouts++;                                  \
                return I2C_TIMEOUT;                                  \
            }                                                        \
            taskYIELD();                                             \
        }                                                            \
    } while (0)

static i2c_status_t i2c_write_byte(uint8_t addr7, uint8_t data)
{
    const TickType_t deadline = xTaskGetTickCount() + pdMS_TO_TICKS(I2C_TIMEOUT_MS);

    WAIT_FLAG(!LL_I2C_IsActiveFlag_BUSY(I2C1), deadline);

    LL_I2C_GenerateStartCondition(I2C1);
    WAIT_FLAG(LL_I2C_IsActiveFlag_SB(I2C1), deadline);

    LL_I2C_TransmitData8(I2C1, (uint8_t)(addr7 << 1)); /* біт 0 = 0: запис */
    WAIT_FLAG(LL_I2C_IsActiveFlag_ADDR(I2C1), deadline);
    LL_I2C_ClearFlag_ADDR(I2C1);

    WAIT_FLAG(LL_I2C_IsActiveFlag_TXE(I2C1), deadline);
    LL_I2C_TransmitData8(I2C1, data);

    WAIT_FLAG(LL_I2C_IsActiveFlag_BTF(I2C1), deadline);
    LL_I2C_GenerateStopCondition(I2C1);

    return I2C_OK;
}

static void i2c_relay_task(void *arg)
{
    (void)arg;

    for (;;) {
        (void)ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        uint8_t byte;
        while (ring_buffer_pop_main(&s_relay_ring, &byte)) {
            const i2c_status_t st = i2c_write_byte(SENSOR_ADDR_7BIT, byte);
            if (st != I2C_OK) {
                /* Шину заклинило. У контексті завдання це просто помилка:
                 * скидаємо решту черги й даємо периферії видихнути.
                 * Всередині ISR та сама ситуація була б зупинкою пристрою. */
                uint8_t drop;
                while (ring_buffer_pop_main(&s_relay_ring, &drop)) {
                    s_relay_dropped++;
                }
                vTaskDelay(pdMS_TO_TICKS(50));
                break;
            }
        }
    }
}

void i2c_relay_start(void)
{
    ring_buffer_init(&s_relay_ring);

    s_relay_task = xTaskCreateStatic(i2c_relay_task,
                                     "i2c-relay",
                                     RELAY_TASK_STACK_WORDS,
                                     NULL,
                                     configMAX_PRIORITIES - 3u,
                                     s_relay_stack,
                                     &s_relay_tcb);
    configASSERT(s_relay_task != NULL);
}

uint32_t i2c_relay_dropped(void)
{
    return s_relay_dropped;
}

uint32_t i2c_relay_failures(void)
{
    return s_relay_bus_errors + s_relay_timeouts;
}

/* Вектор USART2 віддано правильній версії. */
void USART2_IRQHandler(void)
{
    usart2_relay_isr();
}
