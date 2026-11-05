// Об'єктно-орієнтована обгортка аудіостримера мовою C++ (RAII паттерн)
#include "stm32f4xx_hal.h"
#include <cstdint>
#include <cstddef>

class AudioDacStreamer {
public:
    AudioDacStreamer(DAC_TypeDef* dac_inst, TIM_TypeDef* tim_inst, DMA_Stream_TypeDef* dma_stream)
        : m_dac(dac_inst), m_tim(tim_inst), m_dma_stream(dma_stream) {}

    bool Init(uint16_t* buffer_ptr, size_t buffer_size, uint32_t sample_rate_hz) {
        m_buffer = buffer_ptr;
        m_size = buffer_size;

        if (!ConfigureTimer(sample_rate_hz)) return false;
        if (!ConfigureDma()) return false;
        if (!ConfigureDac()) return false;

        return true;
    }

    void Start() {
        HAL_DAC_Start_DMA(&m_hdac, DAC_CHANNEL_1, reinterpret_cast<uint32_t*>(m_buffer), static_cast<uint32_t>(m_size), DAC_ALIGN_12B_R);
        HAL_TIM_Base_Start(&m_htim);
    }

    void Stop() {
        HAL_TIM_Base_Stop(&m_htim);
        HAL_DAC_Stop_DMA(&m_hdac, DAC_CHANNEL_1);
    }

private:
    DAC_TypeDef* m_dac;
    TIM_TypeDef* m_tim;
    DMA_Stream_TypeDef* m_dma_stream;

    DAC_HandleTypeDef m_hdac{};
    DMA_HandleTypeDef m_hdma{};
    TIM_HandleTypeDef m_htim{};

    uint16_t* m_buffer{nullptr};
    size_t m_size{0};

    bool ConfigureTimer(uint32_t sample_rate) {
        __HAL_RCC_TIM6_CLK_ENABLE();
        uint32_t pclk1 = HAL_RCC_GetPCLK1Freq();
        uint32_t prescaler = (pclk1 / 1000000) - 1;
        uint32_t period = (1000000 / sample_rate) - 1;

        m_htim.Instance = m_tim;
        m_htim.Init.Prescaler = prescaler;
        m_htim.Init.CounterMode = TIM_COUNTERMODE_UP;
        m_htim.Init.Period = period;
        m_htim.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;

        if (HAL_TIM_Base_Init(&m_htim) != HAL_OK) return false;

        TIM_MasterConfigTypeDef sMasterConfig{0};
        sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
        sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
        return HAL_TIMEx_MasterConfigSynchronization(&m_htim, &sMasterConfig) == HAL_OK;
    }

    bool ConfigureDma() {
        __HAL_RCC_DMA1_CLK_ENABLE();
        m_hdma.Instance = m_dma_stream;
        m_hdma.Init.Channel = DMA_CHANNEL_7;
        m_hdma.Init.Direction = DMA_MEMORY_TO_PERIPH;
        m_hdma.Init.PeriphInc = DMA_PINC_DISABLE;
        m_hdma.Init.MemInc = DMA_MINC_ENABLE;
        m_hdma.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
        m_hdma.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
        m_hdma.Init.Mode = DMA_CIRCULAR;
        m_hdma.Init.Priority = DMA_PRIORITY_HIGH;
        m_hdma.Init.FIFOMode = DMA_FIFOMODE_DISABLE;

        if (HAL_DMA_Init(&m_hdma) != HAL_OK) return false;
        __HAL_LINKDMA(&m_hdac, DMA_Handle1, m_hdma);
        return true;
    }

    bool ConfigureDac() {
        __HAL_RCC_DAC_CLK_ENABLE();
        m_hdac.Instance = m_dac;
        if (HAL_DAC_Init(&m_hdac) != HAL_OK) return false;

        DAC_ChannelConfTypeDef sConfig{0};
        sConfig.DAC_Trigger = DAC_TRIGGER_T6_TRGO;
        sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
        return HAL_DAC_ConfigChannel(&m_hdac, &sConfig, DAC_CHANNEL_1) == HAL_OK;
    }
};
