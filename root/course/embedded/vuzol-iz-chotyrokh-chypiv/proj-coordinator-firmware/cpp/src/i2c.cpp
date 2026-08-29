#include <array>

#include "i2c.hpp"

namespace node {

void I2cMaster::pinsToPeripheral() noexcept {
    scl_.openDrain(true);
    sda_.openDrain(true);
    scl_.pull(mcu::Pin::Pull::Up);
    sda_.pull(mcu::Pin::Pull::Up);
    scl_.alternate(4);   // AF4 = I2C1
    sda_.alternate(4);
}

void I2cMaster::pinsToManual() noexcept {
    // Ті самі виводи, але вихід загального призначення: такти жене прошивка.
    scl_.write(true);
    sda_.write(true);
    scl_.mode(mcu::Pin::Mode::Output);
    sda_.mode(mcu::Pin::Mode::Output);
}

void I2cMaster::peripheralSetup() noexcept {
    I2C1->CR1 = 0;                  // PE=0 скидає внутрішній автомат
    I2C1->TIMINGR = 0x0030'3D5Bu;   // 100 кГц від ядра HSI16
    I2C1->CR1 = I2C_CR1_PE;
}

void I2cMaster::begin() noexcept {
    RCC->AHB2ENR  |= RCC_AHB2ENR_GPIOBEN;
    RCC->APB1ENR1 |= RCC_APB1ENR1_I2C1EN;

    // Ядро I2C тактуємо від HSI16: тайминги не залежать від того, на чому
    // саме зараз крутиться SYSCLK після виходу зі Stop 2.
    RCC->CCIPR = (RCC->CCIPR & ~RCC_CCIPR_I2C1SEL) | (2u << RCC_CCIPR_I2C1SEL_Pos);
    RCC->CR |= RCC_CR_HSION;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0u) { }

    pinsToPeripheral();
    peripheralSetup();

    if ((I2C1->ISR & I2C_ISR_BUSY) != 0u) {
        recoverBus();   // ведений міг лишитися завислим після скидання ядра
    }
}

bool I2cMaster::recoverBus() noexcept {
    ++recoveries_;

    I2C1->CR1 &= ~I2C_CR1_PE;   // периферія інакше тримає лінії
    pinsToManual();

    bool released = sda_.read();

    // До дев'яти тактів: рівно стільки треба, щоб ведений домовив байт,
    // якого від нього вже ніхто не чекає, і відпустив SDA.
    for (int i = 0; i < 9 && !released; ++i) {
        scl_.write(false);
        mcu::time::delayUs(5);
        scl_.write(true);
        mcu::time::delayUs(5);
        released = sda_.read();
    }

    // Коректний STOP: SDA іде з нуля в одиницю при високому SCL.
    sda_.write(false);
    mcu::time::delayUs(5);
    scl_.write(true);
    mcu::time::delayUs(5);
    sda_.write(true);
    mcu::time::delayUs(5);

    pinsToPeripheral();
    peripheralSetup();

    return released && ((I2C1->ISR & I2C_ISR_BUSY) == 0u);
}

I2cResult<void> I2cMaster::waitFor(std::uint32_t isrMask) noexcept {
    const std::uint32_t started = mcu::time::millis();

    for (;;) {
        const std::uint32_t isr = I2C1->ISR;

        if ((isr & isrMask) != 0u) return {};
        if ((isr & I2C_ISR_NACKF) != 0u) {
            I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
            return std::unexpected{I2cError::Nack};
        }
        if (mcu::time::elapsed(started, kTimeoutMs)) {
            return std::unexpected{I2cError::Timeout};
        }
    }
}

I2cResult<void> I2cMaster::waitIdle() noexcept {
    const std::uint32_t started = mcu::time::millis();

    while ((I2C1->ISR & I2C_ISR_BUSY) != 0u) {
        if (mcu::time::elapsed(started, kTimeoutMs)) {
            // Класичний випадок: ведений тримає SDA і шина «зайнята» вічно.
            if (recoverBus()) break;
            return std::unexpected{I2cError::BusStuck};
        }
    }
    return {};
}

// Аварійне завершення: гасимо периферію, щоб наступна транзакція почалася
// з чистого автомата, а не доїдала недороблену.
std::unexpected<I2cError> I2cMaster::abort(I2cError why) noexcept {
    I2C1->CR1 &= ~I2C_CR1_PE;
    for (volatile int i = 0; i < 8; ++i) { }
    I2C1->CR1 |= I2C_CR1_PE;

    if (why == I2cError::Timeout) recoverBus();
    return std::unexpected{why};
}

I2cResult<void> I2cMaster::write(std::uint8_t addr7, std::span<const std::byte> data) noexcept {
    if (auto idle = waitIdle(); !idle) return idle;

    I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
    I2C1->CR2 = (static_cast<std::uint32_t>(addr7) << 1) |
                (static_cast<std::uint32_t>(data.size()) << I2C_CR2_NBYTES_Pos) |
                I2C_CR2_AUTOEND | I2C_CR2_START;

    for (std::byte b : data) {
        if (auto st = waitFor(I2C_ISR_TXIS); !st) return abort(st.error());
        I2C1->TXDR = static_cast<std::uint32_t>(b);
    }

    if (auto st = waitFor(I2C_ISR_STOPF); !st) return abort(st.error());
    I2C1->ICR = I2C_ICR_STOPCF;
    return {};
}

I2cResult<void> I2cMaster::writeRegister(std::uint8_t addr7, std::uint8_t reg,
                                         std::uint8_t value) noexcept {
    const std::array<std::byte, 2> frame{std::byte{reg}, std::byte{value}};
    return write(addr7, frame);
}

I2cResult<void> I2cMaster::readRegisters(std::uint8_t addr7, std::uint8_t reg,
                                         std::span<std::byte> dst) noexcept {
    if (auto idle = waitIdle(); !idle) return idle;

    I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;

    // Перша фаза — адреса регістра, без AUTOEND: далі потрібен повторний
    // старт, а не STOP, інакше DS3231 скине внутрішній вказівник.
    I2C1->CR2 = (static_cast<std::uint32_t>(addr7) << 1) |
                (1u << I2C_CR2_NBYTES_Pos) | I2C_CR2_START;

    if (auto st = waitFor(I2C_ISR_TXIS); !st) return abort(st.error());
    I2C1->TXDR = reg;

    if (auto st = waitFor(I2C_ISR_TC); !st) return abort(st.error());

    I2C1->CR2 = (static_cast<std::uint32_t>(addr7) << 1) |
                (static_cast<std::uint32_t>(dst.size()) << I2C_CR2_NBYTES_Pos) |
                I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;

    for (std::byte& b : dst) {
        if (auto st = waitFor(I2C_ISR_RXNE); !st) return abort(st.error());
        b = static_cast<std::byte>(I2C1->RXDR);
    }

    if (auto st = waitFor(I2C_ISR_STOPF); !st) return abort(st.error());
    I2C1->ICR = I2C_ICR_STOPCF;
    return {};
}

}  // namespace node
