#include "stm32f4xx.h"
#include <stdint.h>

// Клас захищеного Bit-bang модуля з таймаутами та виводом профілювання
template <uintptr_t PortAddr, uint8_t SclPinIdx, uint8_t SdaPinIdx, uintptr_t ProfPortAddr, uint8_t ProfPinIdx>
class BitBangProtectedI2C {
public:
    static constexpr GPIO_TypeDef* port      = reinterpret_cast<GPIO_TypeDef*>(PortAddr);
    static constexpr GPIO_TypeDef* prof_port = reinterpret_cast<GPIO_TypeDef*>(ProfPortAddr);
    
    static constexpr uint16_t scl_mask  = static_cast<uint16_t>(1U << SclPinIdx);
    static constexpr uint16_t sda_mask  = static_cast<uint16_t>(1U << SdaPinIdx);
    static constexpr uint16_t prof_mask = static_cast<uint16_t>(1U << ProfPinIdx);

    // Очікування звільнення лінії SCL (clock stretching) із захисним таймаутом
    static inline bool wait_scl_high_timeout(uint32_t timeout_cycles) noexcept {
        // Установка виводу профілювання high для вимірювання затримки осцилографом
        prof_port->BSRR = prof_mask;

        uint32_t start_cycles = DWT->CYCCNT;
        bool success = true;

        while ((port->IDR & scl_mask) == 0) {
            if ((DWT->CYCCNT - start_cycles) > timeout_cycles) {
                success = false; // Таймаут вичерпано, ведений пристрій не відпустив SCL
                break;
            }
        }

        // Скидання виводу профілювання low
        prof_port->BSRR = static_cast<uint32_t>(prof_mask) << 16;
        return success;
    }

    // Автоматичне відновлення шини з поверненням коду стану
    static bool safe_bus_reset() noexcept {
        if ((port->IDR & sda_mask) != 0) {
            return true; // Шина вільна
        }

        for (uint8_t i = 0; i < 9; ++i) {
            port->BSRR = static_cast<uint32_t>(scl_mask) << 16; // SCL low
            delay_ticks(100);
            port->BSRR = scl_mask;                             // SCL high
            delay_ticks(100);

            if ((port->IDR & sda_mask) != 0) {
                break;
            }
        }

        // Формування генерації STOP
        port->BSRR = static_cast<uint32_t>(sda_mask) << 16;
        delay_ticks(100);
        port->BSRR = scl_mask;
        delay_ticks(100);
        port->BSRR = sda_mask;
        delay_ticks(100);

        return (port->IDR & sda_mask) != 0;
    }

private:
    static inline void delay_ticks(uint32_t ticks) noexcept {
        uint32_t start = DWT->CYCCNT;
        while ((DWT->CYCCNT - start) < ticks) {
            asm volatile("nop");
        }
    }
};
