#include <stdint.h>
#include <stdbool.h>

/* Апаратні регістри контролера переривань (псевдокод структури MCU) */
typedef struct {
    volatile uint32_t PR;   /* Pending Register (прапорці очікування) */
    volatile uint32_t IMR;  /* Interrupt Mask Register */
} EXTI_TypeDef;

#define EXTI_BASE_ADDR   ((EXTI_TypeDef *)0x40010400)
#define DRDY_PIN_LINE    (1 << 4)  /* Лінія переривання GPIO_PIN_4 */

/* Атомарний прапорець наявності нових даних для обробки у фоновому потоці */
volatile bool g_sensor_data_ready = false;
volatile uint32_t g_drdy_event_counter = 0;

void EXTI4_IRQHandler(void)
{
    EXTI_TypeDef *exti = EXTI_BASE_ADDR;

    /* Перевіряємо, чи переривання викликане саме лінією давача */
    if (exti->PR & DRDY_PIN_LINE) {
        /* Очищаємо апаратний прапорець переривання в контролері EXTI */
        exti->PR = DRDY_PIN_LINE;

        /* Фіксуємо подію для фонового завдання або вивільняємо семафор RTOS */
        g_sensor_data_ready = true;
        g_drdy_event_counter++;
    }
}
