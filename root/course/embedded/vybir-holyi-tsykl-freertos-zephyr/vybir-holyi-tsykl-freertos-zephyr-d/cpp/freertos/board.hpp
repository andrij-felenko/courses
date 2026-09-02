#pragma once

// Плата під RTOS. Відмінність від голого циклу одна, але принципова: там,
// де апаратура змушує чекати мілісекунди, ми віддаємо процесор ядру.
#include "FreeRTOS.h"
#include "task.h"
#include "stm32g0xx.h"

#include <cstdint>
#include <expected>
#include <span>

namespace board {

enum class BusError { Timeout, Nack };

inline constexpr std::uint32_t kBusGuard = 100000U;

inline void init_pins() noexcept
{
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN | RCC_IOPENR_GPIOBEN;
    RCC->APBENR1 |= RCC_APBENR1_I2C1EN;
    RCC->APBENR2 |= RCC_APBENR2_SPI1EN;

    GPIOB->MODER = (GPIOB->MODER & ~(GPIO_MODER_MODE6 | GPIO_MODER_MODE7)) |
                   (2U << GPIO_MODER_MODE6_Pos) | (2U << GPIO_MODER_MODE7_Pos);
    GPIOB->OTYPER |= GPIO_OTYPER_OT6 | GPIO_OTYPER_OT7;
    GPIOB->PUPDR = (GPIOB->PUPDR & ~(GPIO_PUPDR_PUPD6 | GPIO_PUPDR_PUPD7)) |
                   (1U << GPIO_PUPDR_PUPD6_Pos) | (1U << GPIO_PUPDR_PUPD7_Pos);
    GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(GPIO_AFRL_AFSEL6 | GPIO_AFRL_AFSEL7)) |
                    (6U << GPIO_AFRL_AFSEL6_Pos) | (6U << GPIO_AFRL_AFSEL7_Pos);

    I2C1->CR1 = 0U;
    I2C1->TIMINGR = 0x00303D5BU; // 100 кГц при PCLK = 16 МГц
    I2C1->CR1 = I2C_CR1_PE;

    GPIOA->MODER = (GPIOA->MODER & ~(GPIO_MODER_MODE5 | GPIO_MODER_MODE7)) |
                   (2U << GPIO_MODER_MODE5_Pos) | (2U << GPIO_MODER_MODE7_Pos);
    GPIOA->MODER = (GPIOA->MODER & ~(GPIO_MODER_MODE1 | GPIO_MODER_MODE2 | GPIO_MODER_MODE4)) |
                   (1U << GPIO_MODER_MODE1_Pos) | (1U << GPIO_MODER_MODE2_Pos) |
                   (1U << GPIO_MODER_MODE4_Pos);
    GPIOA->OSPEEDR |= (2U << GPIO_OSPEEDR_OSPEED5_Pos) | (2U << GPIO_OSPEEDR_OSPEED7_Pos);
    GPIOA->BSRR = GPIO_BSRR_BS4;

    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (5U << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_DS_0 | SPI_CR2_DS_1 | SPI_CR2_DS_2 | SPI_CR2_FRXTH;
    SPI1->CR1 |= SPI_CR1_SPE;
}

inline void start_watchdog() noexcept
{
    RCC->CSR |= RCC_CSR_LSION;
    while ((RCC->CSR & RCC_CSR_LSIRDY) == 0U) { }

    IWDG->KR = 0x0000CCCCU;
    IWDG->KR = 0x00005555U;
    IWDG->PR = 4U;
    IWDG->RLR = 500U; // ≈ 1 с
    while (IWDG->SR != 0U) { }
    IWDG->KR = 0x0000AAAAU;
}

inline void kick_watchdog() noexcept { IWDG->KR = 0x0000AAAAU; }

class I2cBus {
public:
    explicit constexpr I2cBus(std::uint8_t address7) noexcept : address_{address7} {}

    std::expected<void, BusError> write_reg(std::uint8_t reg, std::uint8_t value) noexcept
    {
        I2C1->CR2 = (std::uint32_t{address_} << 1) | (2U << I2C_CR2_NBYTES_Pos) |
                    I2C_CR2_AUTOEND | I2C_CR2_START;
        if (auto r = wait(I2C_ISR_TXIS); !r) { return r; }
        I2C1->TXDR = reg;
        if (auto r = wait(I2C_ISR_TXIS); !r) { return r; }
        I2C1->TXDR = value;
        finish();
        return {};
    }

    std::expected<void, BusError> read_regs(std::uint8_t reg, std::span<std::uint8_t> out) noexcept
    {
        I2C1->CR2 = (std::uint32_t{address_} << 1) | (1U << I2C_CR2_NBYTES_Pos) | I2C_CR2_START;
        if (auto r = wait(I2C_ISR_TXIS); !r) { return r; }
        I2C1->TXDR = reg;
        if (auto r = wait(I2C_ISR_TC); !r) { return r; }

        I2C1->CR2 = (std::uint32_t{address_} << 1) |
                    (static_cast<std::uint32_t>(out.size()) << I2C_CR2_NBYTES_Pos) |
                    I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;
        for (auto &byte : out) {
            if (auto r = wait(I2C_ISR_RXNE); !r) { return r; }
            byte = static_cast<std::uint8_t>(I2C1->RXDR);
        }
        finish();
        return {};
    }

private:
    static void reset() noexcept
    {
        I2C1->CR1 &= ~I2C_CR1_PE;
        vTaskDelay(1); // такт ядра ми можемо собі дозволити — на відміну від циклу
        I2C1->CR1 |= I2C_CR1_PE;
    }

    static std::expected<void, BusError> wait(std::uint32_t flag) noexcept
    {
        for (std::uint32_t guard = kBusGuard; guard != 0U; --guard) {
            if ((I2C1->ISR & flag) != 0U) { return {}; }
            if ((I2C1->ISR & I2C_ISR_NACKF) != 0U) {
                I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
                reset();
                return std::unexpected{BusError::Nack};
            }
        }
        reset();
        return std::unexpected{BusError::Timeout};
    }

    static void finish() noexcept
    {
        for (std::uint32_t guard = kBusGuard;
             ((I2C1->ISR & I2C_ISR_STOPF) == 0U) && (guard != 0U); --guard) { }
        I2C1->ICR = I2C_ICR_STOPCF | I2C_ICR_NACKCF;
    }

    std::uint8_t address_;
};

class SpiBus {
public:
    static void select(bool on) noexcept { GPIOA->BSRR = on ? GPIO_BSRR_BR4 : GPIO_BSRR_BS4; }
    static void data_mode(bool data) noexcept { GPIOA->BSRR = data ? GPIO_BSRR_BS1 : GPIO_BSRR_BR1; }
    static void reset_pin(bool high) noexcept { GPIOA->BSRR = high ? GPIO_BSRR_BS2 : GPIO_BSRR_BR2; }

    static std::expected<void, BusError> write(std::span<const std::uint8_t> bytes) noexcept
    {
        for (std::uint8_t byte : bytes) {
            std::uint32_t guard = kBusGuard;
            while ((SPI1->SR & SPI_SR_TXE) == 0U) {
                if (guard-- == 0U) { return std::unexpected{BusError::Timeout}; }
            }
            *reinterpret_cast<volatile std::uint8_t *>(&SPI1->DR) = byte;
        }
        while ((SPI1->SR & SPI_SR_BSY) != 0U) { }
        while ((SPI1->SR & SPI_SR_RXNE) != 0U) {
            (void)*reinterpret_cast<volatile std::uint8_t *>(&SPI1->DR);
        }
        return {};
    }
};

} // namespace board
