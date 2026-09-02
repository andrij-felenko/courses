/*
 * Той самий обробник із єдиною точкою виходу. У C немає деструкторів, тож
 * дисципліну тримає goto cleanup: скільки б перевірок не додали далі, маска
 * відновлюється рівно в одному місці й на всіх шляхах.
 */
#include "cortexm.h"
#include "demos.h"

#define FRAME_MARK 0xA5U

/* Останній розібраний відлік: його пише фон, а читає обробник ШІМ. */
volatile uint16_t g_last_sample = 0U;

/* Кадр давача: 0xA5 | довжина | старший байт | молодший байт | XOR-сума. */
int sensor_frame_decode(const uint8_t *frame, size_t len, uint16_t *sample)
{
    if (frame == NULL || sample == NULL || len < 5U) {
        return SENSOR_ERR_ARG;
    }
    if (frame[0] != FRAME_MARK || frame[1] != 2U) {
        return SENSOR_ERR_ARG;
    }

    uint8_t checksum = 0U;
    for (size_t i = 0U; i < 4U; i++) {
        checksum ^= frame[i];
    }
    if (checksum != frame[4]) {
        return SENSOR_ERR_CRC;
    }

    *sample = (uint16_t)(((uint16_t)frame[2] << 8) | (uint16_t)frame[3]);
    return SENSOR_OK;
}

int sensor_frame_handle(const uint8_t *frame, size_t len)
{
    int status;
    uint16_t sample = 0U;

    const uint32_t saved_primask = __get_PRIMASK();
    __disable_irq();
    COMPILER_BARRIER();

    if (frame == NULL || len < 5U) {
        status = SENSOR_ERR_ARG;
        goto cleanup;
    }

    /* Розбір спільної памʼяті не чіпає, тож у зрілому драйвері його виносять
     * ПЕРЕД секцією — усередині лишається саме присвоєння. Тут він усередині
     * навмисне: показуємо шлях виходу, який легко забути. */
    status = sensor_frame_decode(frame, len, &sample);
    if (status != SENSOR_OK) {
        goto cleanup;
    }

    g_last_sample = sample;

cleanup:
    COMPILER_BARRIER();
    __set_PRIMASK(saved_primask); /* єдиний вихід: маска повертається завжди */
    return status;
}
