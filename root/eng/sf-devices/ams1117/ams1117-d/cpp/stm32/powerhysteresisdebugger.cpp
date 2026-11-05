#include "stm32f4xx.h"
#include <cstdint>
#include <string_view>

class PowerHysteresisDebugger {
public:
    static constexpr uint16_t ThresholdOnRaw  = 3908U; // ~3.15 В
    static constexpr uint16_t ThresholdOffRaw = 3660U; // ~2.95 В

    enum class Mode : uint8_t {
        LowPowerMode = 0,
        NormalMode   = 1
    };

    PowerHysteresisDebugger() noexcept : m_currentMode(Mode::NormalMode) {}

    void process(uint32_t filteredRaw) noexcept {
        if (m_currentMode == Mode::NormalMode && filteredRaw < ThresholdOffRaw) {
            m_currentMode = Mode::LowPowerMode;
            setDebugPin(true);
            logItm("[PWR_CPP]: Transition to LOW POWER state\n");
            disableHighPowerPeripherals();
        } else if (m_currentMode == Mode::LowPowerMode && filteredRaw > ThresholdOnRaw) {
            m_currentMode = Mode::NormalMode;
            setDebugPin(false);
            logItm("[PWR_CPP]: Voltage recovered -> NORMAL state\n");
            enableHighPowerPeripherals();
        }
    }

    [[nodiscard]] Mode getMode() const noexcept { return m_currentMode; }

private:
    static void setDebugPin(bool active) noexcept {
        if (active) {
            GPIOA->BSRR = GPIO_BSRR_BS5;
        } else {
            GPIOA->BSRR = GPIO_BSRR_BR5;
        }
    }

    static void logItm(std::string_view message) noexcept {
        for (const char ch : message) {
            if (((ITM->TCR & ITM_TCR_ITMENA_Msk) != 0U) &&
                ((ITM->TER & (1U << 0)) != 0U)) {
                while (ITM->PORT[0].u32 == 0U);
                ITM->PORT[0].u8 = static_cast<uint8_t>(ch);
            }
        }
    }

    static void disableHighPowerPeripherals() noexcept {
        RCC->APB2ENR &= ~RCC_APB2ENR_SPI1EN;
    }

    static void enableHighPowerPeripherals() noexcept {
        RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    }

    Mode m_currentMode;
};
