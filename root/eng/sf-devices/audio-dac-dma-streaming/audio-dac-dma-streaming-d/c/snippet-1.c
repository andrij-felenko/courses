/* Конфігурація потокової передачі аудіо через ЦАП, DMA та Таймер мовою C */
#include "stm32f4xx_hal.h"

#define AUDIO_BUF_SIZE 512

/* Буфер аудіовибірок у пам'яті SRAM */
uint16_t g_audio_buffer[AUDIO_BUF_SIZE];

DAC_HandleTypeDef hdac;
DMA_HandleTypeDef hdma_dac1;
TIM_HandleTypeDef htim6;

void Audio_Init_Hardware(uint32_t sample_rate)
{
    /* 1. Ініціалізація апаратного таймера TIM6 для генерації тригера TRGO */
    __HAL_RCC_TIM6_CLK_ENABLE();
    
    uint32_t pclk1 = HAL_RCC_GetPCLK1Freq();
    uint32_t prescaler = (uint32_t)(pclk1 / 1000000) - 1; /* Тактування 1 МГц */
    uint32_t period = (1000000 / sample_rate) - 1;        /* Період для частоти sample_rate */

    htim6.Instance = TIM6;
    htim6.Init.Prescaler = prescaler;
    htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim6.Init.Period = period;
    htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_Base_Init(&htim6);

    /* Налаштування виходу тригера TRGO за подією оновлення лічильника */
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    HAL_TIMEx_MasterConfigSynchronization(&htim6, &sMasterConfig);

    /* 2. Налаштування контролера DMA у циклічному режимі (Circular Mode) */
    __HAL_RCC_DMA1_CLK_ENABLE();
    
    hdma_dac1.Instance = DMA1_Stream5;
    hdma_dac1.Init.Channel = DMA_CHANNEL_7;
    hdma_dac1.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_dac1.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_dac1.Init.MemInc = DMA_MINC_ENABLE;
    hdma_dac1.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    hdma_dac1.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    hdma_dac1.Init.Mode = DMA_CIRCULAR; /* Циклічна автоматична перезагрузка */
    hdma_dac1.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_dac1.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_dac1);

    /* Прив'язка DMA до каналу ЦАП */
    __HAL_LINKDMA(&hdac, DMA_Handle1, hdma_dac1);

    /* 3. Конфігурація ЦАП зі спрацьовуванням від тригера TIM6 */
    __HAL_RCC_DAC_CLK_ENABLE();
    
    hdac.Instance = DAC;
    HAL_DAC_Init(&hdac);

    DAC_ChannelConfTypeDef sConfig = {0};
    sConfig.DAC_Trigger = DAC_TRIGGER_T6_TRGO; /* Апаратна прив'язка до TRGO */
    sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
    HAL_DAC_ConfigChannel(&hdac, &sConfig, DAC_CHANNEL_1);
}

void Audio_Start_Streaming(void)
{
    /* Запуск заповнення ЦАП через DMA та ввімкнення таймера */
    HAL_DAC_Start_DMA(&hdac, DAC_CHANNEL_1, (uint32_t*)g_audio_buffer, AUDIO_BUF_SIZE, DAC_ALIGN_12B_R);
    HAL_TIM_Base_Start(&htim6);
}
