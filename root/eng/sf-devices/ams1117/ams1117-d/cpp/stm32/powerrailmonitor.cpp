#include "stm32f4xx_hal.h"
#include "cmsis_os2.h"
#include <array>
#include <cstdint>

class PowerRailMonitor {
public:
    static constexpr size_t BufferLength = 16;
    static constexpr uint32_t EwmaShift = 3;
    static constexpr uint16_t ThresholdWarning = 3846; // ~3.1 В
    static constexpr uint16_t ThresholdCritical = 3598; // ~2.9 В

    static constexpr uint32_t FlagWarning = (1U << 0);
    static constexpr uint32_t FlagCritical = (1U << 1);

    enum class State : uint8_t {
        Normal = 0,
        Warning = 1,
        Critical = 2
    };

    explicit PowerRailMonitor(ADC_HandleTypeDef* hadc)
        : m_hadc(hadc), m_filteredVoltage(0), m_currentState(State::Normal) {}

    void init() {
        HAL_ADC_Start_DMA(m_hadc, reinterpret_cast<uint32_t*>(m_rawBuffer.data()), BufferLength);
    }

    void processBuffer(osEventFlagsId_t eventFlags) {
        uint32_t sum = 0;
        for (const auto sample : m_rawBuffer) {
            sum += sample;
        }
        const uint32_t average = sum / BufferLength;

        if (m_filteredVoltage == 0) {
            m_filteredVoltage = average;
        } else {
            m_filteredVoltage = ((m_filteredVoltage << EwmaShift) - m_filteredVoltage + average) >> EwmaShift;
        }

        if (m_filteredVoltage < ThresholdCritical) {
            m_currentState = State::Critical;
            osEventFlagsSet(eventFlags, FlagCritical);
        } else if (m_filteredVoltage < ThresholdWarning) {
            m_currentState = State::Warning;
            osEventFlagsSet(eventFlags, FlagWarning);
        } else {
            m_currentState = State::Normal;
        }
    }

    [[nodiscard]] State getCurrentState() const { return m_currentState; }
    [[nodiscard]] uint32_t getFilteredVoltage() const { return m_filteredVoltage; }

private:
    ADC_HandleTypeDef* m_hadc;
    alignas(4) std::array<uint16_t, BufferLength> m_rawBuffer{};
    uint32_t m_filteredVoltage;
    State m_currentState;
};
