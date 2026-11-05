/* Ідіоматичний клас потокового аудіоплеєра мовою C++ (C++17) */
#include "stm32f4xx_hal.h"
#include <array>
#include <functional>
#include <cmath>

template <size_t HalfBufferSize>
class AudioStreamEngine {
public:
    static constexpr size_t FullBufferSize = HalfBufferSize * 2;

    AudioStreamEngine(DAC_HandleTypeDef& hdac, TIM_HandleTypeDef& htim, uint32_t channel)
        : m_hdac(hdac), m_htim(htim), m_channel(channel) {}

    using FillCallback = std::function<void(uint16_t* buffer, size_t size)>;

    void SetAudioGenerator(FillCallback callback) {
        m_generator = std::move(callback);
    }

    bool Start() {
        if (!m_generator) return false;

        /* Початкова ініціалізація обох половин */
        m_generator(&m_buffer[0], HalfBufferSize);
        m_generator(&m_buffer[HalfBufferSize], HalfBufferSize);

        FlushCache(&m_buffer[0], FullBufferSize);

        s_instance = this;

        HAL_DAC_Start_DMA(&m_hdac, m_channel, reinterpret_cast<uint32_t*>(m_buffer.data()), FullBufferSize, DAC_ALIGN_12B_R);
        HAL_TIM_Base_Start(&m_htim);
        return true;
    }

    void Stop() {
        HAL_TIM_Base_Stop(&m_htim);
        HAL_DAC_Stop_DMA(&m_hdac, m_channel);
        s_instance = nullptr;
    }

    void OnHalfComplete() {
        if (m_generator) {
            m_generator(&m_buffer[0], HalfBufferSize);
            FlushCache(&m_buffer[0], HalfBufferSize);
        }
    }

    void OnFullComplete() {
        if (m_generator) {
            m_generator(&m_buffer[HalfBufferSize], HalfBufferSize);
            FlushCache(&m_buffer[HalfBufferSize], HalfBufferSize);
        }
    }

    static AudioStreamEngine* GetInstance() { return s_instance; }

private:
    DAC_HandleTypeDef& m_hdac;
    TIM_HandleTypeDef& m_htim;
    uint32_t m_channel;
    FillCallback m_generator;

    alignas(32) std::array<uint16_t, FullBufferSize> m_buffer{};
    static inline AudioStreamEngine* s_instance{nullptr};

    void FlushCache(uint16_t* ptr, size_t count) {
        SCB_CleanDCache_by_Addr(reinterpret_cast<uint32_t*>(ptr), count * sizeof(uint16_t));
        __DSB();
    }
};

/* Глобальні системні перехоплювачі подій HAL C++ */
extern "C" void HAL_DAC_ConvHalfCpltCallbackCh1(DAC_HandleTypeDef* hdac) {
    if (auto* engine = AudioStreamEngine<256>::GetInstance()) {
        engine->OnHalfComplete();
    }
}

extern "C" void HAL_DAC_ConvCpltCallbackCh1(DAC_HandleTypeDef* hdac) {
    if (auto* engine = AudioStreamEngine<256>::GetInstance()) {
        engine->OnFullComplete();
    }
}
