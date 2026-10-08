// C++: Обгортка для локального обчислювального буфера в CCM SRAM із гарантованим детермінованим доступом
#include "stm32f4xx.h"
#include <arm_math.h>
#include <cstddef>

template <typename T, std::size_t Size>
class CcmBuffer {
private:
    // Атрибут ccmram гарантує розміщення масиву у зоні Core Coupled Memory (0x10000000)
    alignas(4) T m_data[Size] __attribute__((section(".ccmram")));

public:
    constexpr std::size_t size() const { return Size; }

    T& operator[](std::size_t index) { return m_data[index]; }
    const T& operator[](std::size_t index) const { return m_data[index]; }

    T* data() { return m_data; }
};

// Екземпляр обчислювального буфера у CCM SRAM
static CcmBuffer<float32_t, 256> g_dsp_pipeline_buffer;

void process_pipeline_step(const uint16_t* raw_input) {
    for (std::size_t i = 0; i < g_dsp_pipeline_buffer.size(); ++i) {
        g_dsp_pipeline_buffer[i] = static_cast<float32_t>(raw_input[i]) * 0.00024414f; // 1 / 4095
    }
}
