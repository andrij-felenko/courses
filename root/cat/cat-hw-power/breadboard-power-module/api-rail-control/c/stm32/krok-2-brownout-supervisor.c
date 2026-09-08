/* ============================================================================
   krok-2-brownout-supervisor.c — STM32 HAL: супервізор напруги шини
   ========================================================================== */

#include "main.h"

#define V_WARN_TRIP_MV   4650
#define V_WARN_CLEAR_MV  4800

extern uint32_t STM32_Read_Rail_mV(void);

typedef enum {
    STM32_RAIL_OK,
    STM32_RAIL_WARN
} STM32_Rail_Status_t;

static STM32_Rail_Status_t s_status = STM32_RAIL_OK;

void MB102_Supervisor_Process(void) {
    uint32_t mv = STM32_Read_Rail_mV();

    if (s_status == STM32_RAIL_OK) {
        if (mv < V_WARN_TRIP_MV) {
            s_status = STM32_RAIL_WARN;
            // Екстрене вимкнення силового P-MOSFET (GPIO_PIN_SET = HIGH = OFF)
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET); // Alarm LED ON
        }
    } else {
        if (mv >= V_WARN_CLEAR_MV) {
            s_status = STM32_RAIL_OK;
            // Відновлення навантаження (GPIO_PIN_RESET = LOW = ON)
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); // Alarm LED OFF
        }
    }
}
