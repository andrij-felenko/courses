/*
 * Як критична секція витікає в C: у функції зʼявилися перевірки, і кожен
 * достроковий return виносить нас із неї з вимкненими перериваннями.
 * Наслідок — не «трохи повільніше», а мертвий контролер: SysTick не тікає,
 * UART не приймає, сторожовий таймер перезавантажує плату.
 */
#include "cortexm.h"
#include "demos.h"

int sensor_frame_handle_leaky(const uint8_t *frame, size_t len)
{
    uint16_t sample = 0U;

    const uint32_t saved_primask = __get_PRIMASK();
    __disable_irq();
    COMPILER_BARRIER();

    if (frame == NULL || len < 5U) {
        /* Витік №1: PRIMASK лишився одиницею назавжди. */
        return SENSOR_ERR_ARG;
    }

    const int rc = sensor_frame_decode(frame, len, &sample);
    if (rc != SENSOR_OK) {
        /* Витік №2, найпідступніший: спрацьовує раз на тисячу кадрів, коли
         * завада зіпсувала контрольну суму, і виглядає як «зависання без причини». */
        return rc;
    }

    g_last_sample = sample;

    COMPILER_BARRIER();
    __set_PRIMASK(saved_primask); /* сюди доходить лише щасливий шлях */
    return SENSOR_OK;
}
