// ports/stm32f4/stm32_i2c_bus.cpp — контролер I2C1 мікроконтролера STM32F401.
// Це ЄДИНЕ місце у всьому проєкті, де згадано регістри контролера шини.
// Драйвери BME280 і ADXL345 знають лише hal::II2cBus.
#include "hal/clock.hpp"
#include "ports/stm32f4/stm32_peripherals.hpp"

namespace port {
namespace {

constexpr hal::Millis  kTimeout{10};
constexpr std::uint32_t kApb1ClockMhz = 42;
constexpr std::uint32_t kCcr100kHz    = 210;  // 42 МГц / (2 × 100 кГц)
constexpr std::uint32_t kTrise100kHz  = 43;   // 1000 нс × 42 МГц + 1

} // namespace

void Stm32I2cBus::init()
{
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    // PB6 = SCL, PB7 = SDA: альтернативна функція 4, відкритий стік,
    // підтяжки на платі зовнішні (4.7 кОм).
    GPIOB->MODER   &= ~((3U << 12) | (3U << 14));
    GPIOB->MODER   |=  ((2U << 12) | (2U << 14));
    GPIOB->OTYPER  |=  ((1U << 6) | (1U << 7));
    GPIOB->OSPEEDR |=  ((3U << 12) | (3U << 14));
    GPIOB->PUPDR   &= ~((3U << 12) | (3U << 14));
    GPIOB->AFR[0]  &= ~((0xFU << 24) | (0xFU << 28));
    GPIOB->AFR[0]  |=  ((4U << 24) | (4U << 28));

    // Після скидання шини контролер часто лишається у стані «зайнято»:
    // скидаємо його явно, інакше перша ж транзакція впаде за часом.
    regs_->CR1 = I2C_CR1_SWRST;
    regs_->CR1 = 0;
    regs_->CR2   = kApb1ClockMhz;
    regs_->CCR   = kCcr100kHz;
    regs_->TRISE = kTrise100kHz;
    regs_->CR1  |= I2C_CR1_PE;
}

// Нескінченне очікування прапорця перетворює пристрій на цеглину: досить
// одного розряду статики, щоб лінія SDA залипла в нулі назавжди.
std::expected<void, hal::I2cError> Stm32I2cBus::wait_flag(std::uint32_t mask)
{
    const auto started = hal::now();
    while ((regs_->SR1 & mask) == 0) {
        if ((regs_->SR1 & I2C_SR1_AF) != 0) {
            regs_->SR1 &= ~I2C_SR1_AF;
            regs_->CR1 |= I2C_CR1_STOP;
            return std::unexpected{hal::I2cError::Nack};
        }
        if ((regs_->SR1 & (I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR)) != 0) {
            regs_->SR1 &= ~(I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR);
            regs_->CR1 |= I2C_CR1_STOP;
            return std::unexpected{hal::I2cError::BusError};
        }
        if (hal::elapsed_since(started) > kTimeout) {
            regs_->CR1 |= I2C_CR1_STOP;
            return std::unexpected{hal::I2cError::Timeout};
        }
    }
    return {};
}

std::expected<void, hal::I2cError> Stm32I2cBus::wait_not_busy()
{
    const auto started = hal::now();
    while ((regs_->SR2 & I2C_SR2_BUSY) != 0) {
        if (hal::elapsed_since(started) > kTimeout) {
            return std::unexpected{hal::I2cError::BusError};
        }
    }
    return {};
}

void Stm32I2cBus::clear_addr()
{
    // Прапорець ADDR скидається читанням SR1, а потім SR2 — саме в такому
    // порядку. Пропущене читання лишає контролер у розтягнутому такті.
    volatile std::uint32_t tmp = regs_->SR1;
    tmp = regs_->SR2;
    static_cast<void>(tmp);
}

std::expected<void, hal::I2cError> Stm32I2cBus::start(std::uint8_t address, bool reading)
{
    regs_->CR1 |= I2C_CR1_START;
    if (auto res = wait_flag(I2C_SR1_SB); !res) {
        return res;
    }
    regs_->DR = static_cast<std::uint32_t>(address << 1) | (reading ? 1U : 0U);
    return wait_flag(I2C_SR1_ADDR);
}

std::expected<void, hal::I2cError>
Stm32I2cBus::write(std::uint8_t address, std::span<const std::uint8_t> data)
{
    if (auto res = wait_not_busy(); !res) {
        return res;
    }
    if (auto res = start(address, false); !res) {
        return res;
    }
    clear_addr();

    // Порожня посилка — це опитування присутності: адресу мікросхема вже
    // підтвердила, тож просто відпускаємо шину.
    for (const std::uint8_t byte : data) {
        if (auto res = wait_flag(I2C_SR1_TXE); !res) {
            return res;
        }
        regs_->DR = byte;
    }

    if (!data.empty()) {
        if (auto res = wait_flag(I2C_SR1_BTF); !res) {
            return res;
        }
    }
    regs_->CR1 |= I2C_CR1_STOP;
    return {};
}

std::expected<void, hal::I2cError>
Stm32I2cBus::read(std::uint8_t address, std::span<std::uint8_t> data)
{
    if (data.empty()) {
        return std::unexpected{hal::I2cError::BadArgs};
    }
    if (auto res = wait_not_busy(); !res) {
        return res;
    }
    return receive(address, data);
}

std::expected<void, hal::I2cError>
Stm32I2cBus::receive(std::uint8_t address, std::span<std::uint8_t> data)
{
    regs_->CR1 |= I2C_CR1_ACK;
    if (auto res = start(address, true); !res) {
        return res;
    }

    // Три різні послідовності завершення — не примха, а припис довідника
    // RM0090: контролер має дізнатися про кінець посилки на байт раніше,
    // ніж той доїде.
    if (data.size() == 1) {
        regs_->CR1 &= ~I2C_CR1_ACK;
        clear_addr();
        regs_->CR1 |= I2C_CR1_STOP;
        if (auto res = wait_flag(I2C_SR1_RXNE); !res) {
            return res;
        }
        data[0] = static_cast<std::uint8_t>(regs_->DR);
        return {};
    }

    if (data.size() == 2) {
        regs_->CR1 &= ~I2C_CR1_ACK;
        regs_->CR1 |= I2C_CR1_POS;   // NACK поїде на другий байт
        clear_addr();
        auto res = wait_flag(I2C_SR1_BTF);
        if (!res) {
            regs_->CR1 &= ~I2C_CR1_POS;
            return res;
        }
        regs_->CR1 |= I2C_CR1_STOP;
        data[0] = static_cast<std::uint8_t>(regs_->DR);
        data[1] = static_cast<std::uint8_t>(regs_->DR);
        regs_->CR1 &= ~I2C_CR1_POS;
        return {};
    }

    clear_addr();

    std::size_t index = 0;
    while ((data.size() - index) > 3) {
        if (auto res = wait_flag(I2C_SR1_RXNE); !res) {
            return res;
        }
        data[index++] = static_cast<std::uint8_t>(regs_->DR);
    }

    // Лишилося три байти: чекаємо BTF, знімаємо ACK і забираємо N-3.
    if (auto res = wait_flag(I2C_SR1_BTF); !res) {
        return res;
    }
    regs_->CR1 &= ~I2C_CR1_ACK;
    data[index++] = static_cast<std::uint8_t>(regs_->DR);

    if (auto res = wait_flag(I2C_SR1_BTF); !res) {
        return res;
    }
    regs_->CR1 |= I2C_CR1_STOP;
    data[index++] = static_cast<std::uint8_t>(regs_->DR);
    data[index]   = static_cast<std::uint8_t>(regs_->DR);
    return {};
}

std::expected<void, hal::I2cError>
Stm32I2cBus::write_read(std::uint8_t address,
                        std::span<const std::uint8_t> tx,
                        std::span<std::uint8_t> rx)
{
    if (tx.empty() || rx.empty()) {
        return std::unexpected{hal::I2cError::BadArgs};
    }
    if (auto res = wait_not_busy(); !res) {
        return res;
    }
    if (auto res = start(address, false); !res) {
        return res;
    }
    clear_addr();

    for (const std::uint8_t byte : tx) {
        if (auto res = wait_flag(I2C_SR1_TXE); !res) {
            return res;
        }
        regs_->DR = byte;
    }
    if (auto res = wait_flag(I2C_SR1_BTF); !res) {
        return res;
    }

    // Повторний START без STOP: шина не відпускається, тож інший майстер
    // не встромиться між адресою регістра й читанням даних.
    return receive(address, rx);
}

} // namespace port
