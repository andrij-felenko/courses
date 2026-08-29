// stm32_usart.hpp — периферія STM32G4 під напівдуплексну шину:
// USART1 (PA9/PA10), DE на PA12, DMA1_Channel4 на передавання, TIM7 на паузи.
//
// kHardwareDriverEnable перемикає керування DE на сам UART (CR3_DEM): ядро
// перестає смикати пін, а перед стартом і після стоп-біта витримуються
// апаратні інтервали DEAT/DEDT.
#pragma once

#include <chrono>
#include <cstdint>
#include <span>

#include "stm32g4xx.h"

namespace rs485 {

// Критична секція без ручного розблокування: PRIMASK відновлюється деструктором.
class IrqGuard {
public:
    IrqGuard() noexcept : primask_{__get_PRIMASK()} { __disable_irq(); }
    ~IrqGuard() {
        if (primask_ == 0) {
            __enable_irq();
        }
    }
    IrqGuard(const IrqGuard&) = delete;
    IrqGuard& operator=(const IrqGuard&) = delete;

private:
    std::uint32_t primask_;
};

namespace reg {
// USART_CR1
inline constexpr std::uint32_t kUe = 1u << 0;
inline constexpr std::uint32_t kRe = 1u << 2;
inline constexpr std::uint32_t kTe = 1u << 3;
inline constexpr std::uint32_t kRxneie = 1u << 5;
inline constexpr std::uint32_t kTcie = 1u << 6;
inline constexpr std::uint32_t kPeie = 1u << 8;
inline constexpr std::uint32_t kDedtPos = 16;   // затримка зняття DE після стоп-біта
inline constexpr std::uint32_t kDeatPos = 21;   // затримка старт-біта після підняття DE
// USART_CR3
inline constexpr std::uint32_t kEie = 1u << 0;
inline constexpr std::uint32_t kDmat = 1u << 7;
inline constexpr std::uint32_t kDem = 1u << 14;
// USART_ISR
inline constexpr std::uint32_t kPe = 1u << 0;
inline constexpr std::uint32_t kFe = 1u << 1;
inline constexpr std::uint32_t kNe = 1u << 2;
inline constexpr std::uint32_t kOre = 1u << 3;
inline constexpr std::uint32_t kRxne = 1u << 5;
inline constexpr std::uint32_t kTc = 1u << 6;
// USART_ICR
inline constexpr std::uint32_t kPecf = 1u << 0;
inline constexpr std::uint32_t kFecf = 1u << 1;
inline constexpr std::uint32_t kNcf = 1u << 2;
inline constexpr std::uint32_t kOrecf = 1u << 3;
inline constexpr std::uint32_t kTccf = 1u << 6;
// DMA_CCR
inline constexpr std::uint32_t kDmaEn = 1u << 0;
inline constexpr std::uint32_t kDmaTcie = 1u << 1;
inline constexpr std::uint32_t kDmaDirM2P = 1u << 4;
inline constexpr std::uint32_t kDmaMinc = 1u << 7;
inline constexpr std::uint32_t kDmaTcif4 = 1u << 13;
// TIM_CR1
inline constexpr std::uint32_t kTimCen = 1u << 0;
inline constexpr std::uint32_t kTimUrs = 1u << 2;
inline constexpr std::uint32_t kTimOpm = 1u << 3;

inline constexpr std::uint32_t kUsartClockHz = 170'000'000;
inline constexpr std::uint32_t kTimerClockHz = 170'000'000;
inline constexpr std::uint32_t kDmamuxUsart1Tx = 25;  // таблиця запитів DMAMUX (RM0440)
}  // namespace reg

struct RxFlags;   // оголошено в rs485_port.hpp

class Stm32Usart {
public:
    static constexpr bool kHardwareDriverEnable = false;

    // Знімок статусного регістра: читаємо ISR один раз і розбираємо тут.
    class Status {
    public:
        explicit Status(std::uint32_t isr) noexcept : isr_{isr} {}
        [[nodiscard]] bool hasError() const noexcept {
            return (isr_ & (reg::kOre | reg::kFe | reg::kNe | reg::kPe)) != 0;
        }
        [[nodiscard]] bool rxReady() const noexcept { return (isr_ & reg::kRxne) != 0; }
        [[nodiscard]] bool transmissionComplete() const noexcept {
            return (isr_ & reg::kTc) != 0 && (USART1->CR1 & reg::kTcie) != 0;
        }
        [[nodiscard]] RxFlags errors() const noexcept;

    private:
        std::uint32_t isr_;
    };

    void configure(std::uint32_t baud, bool hardwareDe) noexcept;

    void setDriverEnable(bool on) noexcept {
        if (hardwareDe_) {
            return;   // вивід веде периферія
        }
        GPIOA->BSRR = on ? (1u << 12) : (1u << (12 + 16));
    }

    void startTx(std::span<const std::uint8_t> frame) noexcept {
        DMA1_Channel4->CCR &= ~reg::kDmaEn;
        DMA1->IFCR = 0xFu << 12;
        DMA1_Channel4->CPAR = reinterpret_cast<std::uint32_t>(&USART1->TDR);
        DMA1_Channel4->CMAR = reinterpret_cast<std::uint32_t>(frame.data());
        DMA1_Channel4->CNDTR = static_cast<std::uint32_t>(frame.size());
        DMA1_Channel4->CCR = reg::kDmaMinc | reg::kDmaDirM2P | reg::kDmaTcie;

        USART1->ICR = reg::kTccf;   // прибрати TC від попереднього кадру
        DMA1_Channel4->CCR |= reg::kDmaEn;
    }

    void abortTx() noexcept {
        DMA1_Channel4->CCR &= ~(reg::kDmaEn | reg::kDmaTcie);
        DMA1->IFCR = 0xFu << 12;
    }

    void enableTcIrq(bool on) noexcept {
        if (on) {
            USART1->ICR = reg::kTccf;
            USART1->CR1 |= reg::kTcie;
        } else {
            USART1->CR1 &= ~reg::kTcie;
            USART1->ICR = reg::kTccf;
        }
    }

    // На класичному USART (F1/F4) ORE знімається читанням SR, потім DR;
    // тут для цього є окремий регістр ICR.
    void clearRxErrors() noexcept {
        USART1->ICR = reg::kPecf | reg::kFecf | reg::kNcf | reg::kOrecf;
        [[maybe_unused]] volatile std::uint32_t drop = USART1->RDR;
    }

    void armTimer(std::chrono::microseconds delay) noexcept {
        const auto ticks = static_cast<std::uint32_t>(delay.count());
        TIM7->CR1 = 0;
        TIM7->PSC = reg::kTimerClockHz / 1'000'000 - 1;   // тік — 1 мкс
        TIM7->ARR = ticks > 1 ? ticks - 1 : 1;
        TIM7->EGR = 1;    // UG: перезавантажити PSC/ARR
        TIM7->SR = 0;     // UG підняв UIF — прибираємо
        TIM7->DIER = 1;   // UIE
        TIM7->CR1 = reg::kTimOpm | reg::kTimUrs | reg::kTimCen;
    }

    void stopTimer() noexcept {
        TIM7->CR1 = 0;
        TIM7->DIER = 0;
        TIM7->SR = 0;
    }

    [[nodiscard]] static Status status() noexcept { return Status{USART1->ISR}; }
    [[nodiscard]] static std::uint8_t readByte() noexcept {
        return static_cast<std::uint8_t>(USART1->RDR);
    }
    static void clearTransmissionComplete() noexcept { USART1->ICR = reg::kTccf; }

    [[nodiscard]] static bool takeDmaComplete() noexcept {
        if ((DMA1->ISR & reg::kDmaTcif4) == 0) {
            return false;
        }
        DMA1->IFCR = reg::kDmaTcif4;
        DMA1_Channel4->CCR &= ~reg::kDmaEn;
        return true;
    }

    [[nodiscard]] static bool takeTimerEvent() noexcept {
        if ((TIM7->SR & 1u) == 0) {
            return false;
        }
        TIM7->SR = 0;
        return true;
    }

private:
    bool hardwareDe_{false};
};

inline void Stm32Usart::configure(std::uint32_t baud, bool hardwareDe) noexcept {
    hardwareDe_ = hardwareDe;

    RCC->AHB2ENR |= 1u << 0;                 // GPIOA
    RCC->AHB1ENR |= (1u << 0) | (1u << 2);   // DMA1, DMAMUX
    RCC->APB2ENR |= 1u << 14;                // USART1
    RCC->APB1ENR1 |= 1u << 5;                // TIM7

    GPIOA->MODER &= ~((3u << (9 * 2)) | (3u << (10 * 2)) | (3u << (12 * 2)));
    GPIOA->MODER |= (2u << (9 * 2)) | (2u << (10 * 2));   // PA9/PA10 — AF7
    GPIOA->AFR[1] &= ~((0xFu << 4) | (0xFu << 8) | (0xFu << 16));
    GPIOA->AFR[1] |= (7u << 4) | (7u << 8);

    if (hardwareDe_) {
        GPIOA->MODER |= 2u << (12 * 2);   // PA12 = USART1_DE
        GPIOA->AFR[1] |= 7u << 16;
    } else {
        GPIOA->MODER |= 1u << (12 * 2);   // PA12 — звичайний вихід
        GPIOA->OSPEEDR |= 3u << (12 * 2);
        setDriverEnable(false);
    }

    DMAMUX1_Channel3->CCR = reg::kDmamuxUsart1Tx;   // канал 4 DMA1 = канал 3 мультиплексора

    USART1->CR1 = 0;   // DEAT/DEDT пишуться лише при UE = 0
    USART1->BRR = (reg::kUsartClockHz + baud / 2) / baud;
    USART1->CR3 = reg::kDmat | reg::kEie;
    if (hardwareDe_) {
        USART1->CR3 |= reg::kDem;
        USART1->CR1 |= (8u << reg::kDeatPos) | (8u << reg::kDedtPos);   // по пів символу з боків
    }
    USART1->CR1 |= reg::kUe | reg::kTe | reg::kRe | reg::kRxneie | reg::kPeie;

    NVIC_SetPriority(USART1_IRQn, 1);
    NVIC_SetPriority(DMA1_Channel4_IRQn, 1);
    NVIC_SetPriority(TIM7_DAC_IRQn, 1);   // ім'я вектора — за startup-файлом сімейства
    NVIC_EnableIRQ(USART1_IRQn);
    NVIC_EnableIRQ(DMA1_Channel4_IRQn);
    NVIC_EnableIRQ(TIM7_DAC_IRQn);
}

}  // namespace rs485
