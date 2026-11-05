/* Подвійна буферизація аудіоданих ЦАП через DMA мовою C */
#include "stm32f4xx_hal.h"
#include <math.h>

#define AUDIO_HALF_BUF_SIZE 256
#define AUDIO_FULL_BUF_SIZE (AUDIO_HALF_BUF_SIZE * 2)
#define PI_VAL 3.14159265358979323846f

/* Вирівняний буфер у пам'яті SRAM за межою 32 байти */
uint16_t g_pingpong_buffer[AUDIO_FULL_BUF_SIZE] __attribute__((aligned(32)));

extern DAC_HandleTypeDef hdac;
extern TIM_HandleTypeDef htim6;

/* Синтез простого синусоїдального сигналу для заповнення буфера */
static void Fill_Audio_Buffer_Half(uint16_t *p_out, uint32_t len, float *phase)
{
    for (uint32_t i = 0; i < len; i++)
    {
        /* Генерація нормованої синусоїди від 0 до 4095 для 12-бітного ЦАП */
        float val = (sinf(*phase) + 1.0f) * 0.5f * 4095.0f;
        p_out[i] = (uint16_t)val;
        *phase += 0.05f;
        if (*phase >= (2.0f * PI_VAL))
        {
            *phase -= (2.0f * PI_VAL);
        }
    }
    
    /* Очищення D-Cache для примусового збереження даних в SRAM перед DMA трансфером */
    SCB_CleanDCache_by_Addr((uint32_t*)p_out, len * sizeof(uint16_t));
    __DSB();
}

/* Обробник події опрацювання першої половини буфера (Ping) */
void HAL_DAC_ConvHalfCpltCallbackCh1(DAC_HandleTypeDef *hdac_ptr)
{
    static float phase = 0.0f;
    /* Зворотний виклик під час відтворення буфера 1: перезаписуємо буфер 0 */
    Fill_Audio_Buffer_Half(&g_pingpong_buffer[0], AUDIO_HALF_BUF_SIZE, &phase);
}

/* Обробник події опрацювання другої половини буфера (Pong) */
void HAL_DAC_ConvCpltCallbackCh1(DAC_HandleTypeDef *hdac_ptr)
{
    static float phase = 0.0f;
    /* Зворотний виклик під час відтворення буфера 0: перезаписуємо буфер 1 */
    Fill_Audio_Buffer_Half(&g_pingpong_buffer[AUDIO_HALF_BUF_SIZE], AUDIO_HALF_BUF_SIZE, &phase);
}

/* Запуск потокової передачі в подвійному буфері */
void Audio_Start_Streaming(void)
{
    float init_phase = 0.0f;
    /* Початкове заповнення обох половин буфера перед стартом */
    Fill_Audio_Buffer_Half(&g_pingpong_buffer[0], AUDIO_HALF_BUF_SIZE, &init_phase);
    Fill_Audio_Buffer_Half(&g_pingpong_buffer[AUDIO_HALF_BUF_SIZE], AUDIO_HALF_BUF_SIZE, &init_phase);

    HAL_DAC_Start_DMA(&hdac, DAC_CHANNEL_1, (uint32_t*)g_pingpong_buffer, AUDIO_FULL_BUF_SIZE, DAC_ALIGN_12B_R);
    HAL_TIM_Base_Start(&htim6);
}
