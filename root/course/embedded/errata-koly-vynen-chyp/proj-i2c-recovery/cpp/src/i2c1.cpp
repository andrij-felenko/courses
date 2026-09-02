#include "i2c1.hpp"

#include "timing.hpp"

#include "stm32f10x.h"

namespace hw {
namespace {

using namespace std::chrono_literals;

/* Стеля очікування однієї події. Байт на 100 кГц їде 90 мкс, тож 2 мс — це вже
   не «повільно», а «ніхто не відповідає». */
constexpr auto kEventTimeout = 2000us;

/* Чекаємо на прапорець у SR1, попутно ловлячи дві біди, які теж проявляються
   як «подія не настала»: неотримане підтвердження й помилку шини. */
std::expected<void, I2cError> wait_flag(std::uint16_t flag) noexcept {
    I2cError fault = I2cError::Timeout;
    bool failed = false;

    const bool settled = bsp::wait_until([&]() noexcept {
        const std::uint16_t sr1 = I2C1->SR1;

        if ((sr1 & I2C_SR1_AF) != 0U) {
            I2C1->SR1 = static_cast<std::uint16_t>(sr1 & ~I2C_SR1_AF);  /* знімається записом нуля */
            fault = I2cError::Nack;
            failed = true;
            return true;
        }
        if ((sr1 & I2C_SR1_BERR) != 0U) {
            I2C1->SR1 = static_cast<std::uint16_t>(sr1 & ~I2C_SR1_BERR);
            fault = I2cError::BusError;
            failed = true;
            return true;
        }
        return (sr1 & flag) != 0U;
    }, kEventTimeout);

    if (!settled) {
        I2C1->CR1 |= I2C_CR1_STOP;   /* спроба звільнити шину по-доброму */
        return std::unexpected{I2cError::Timeout};
    }
    if (failed) {
        I2C1->CR1 |= I2C_CR1_STOP;
        return std::unexpected{fault};
    }
    return {};
}

void clear_addr_flag() noexcept {
    (void)I2C1->SR1;
    (void)I2C1->SR2;   /* ADDR знімається читанням саме цієї пари регістрів */
}

} // namespace

I2c1::I2c1(std::uint32_t bus_hz) noexcept {
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    I2C1->CR1 = I2C_CR1_SWRST;   /* скидання всередині блоку: регістри в нулі */
    bsp::delay(2us);
    I2C1->CR1 = 0U;

    SystemCoreClockUpdate();
    const std::uint32_t pclk1 = SystemCoreClock / 2U;   /* APB1 = 36 МГц при ядрі 72 МГц */
    const std::uint32_t pclk1_mhz = pclk1 / 1'000'000U;

    I2C1->CR2 = static_cast<std::uint16_t>(pclk1_mhz);  /* модулю треба знати частоту входу */

    std::uint32_t ccr = pclk1 / (2U * bus_hz);          /* стандартний режим: T_low = T_high */
    if (ccr < 4U) {
        ccr = 4U;                                       /* нижня межа за RM0008 */
    }
    I2C1->CCR = static_cast<std::uint16_t>(ccr);
    I2C1->TRISE = static_cast<std::uint16_t>(pclk1_mhz + 1U);   /* 1000 нс фронту */

    I2C1->CR1 = I2C_CR1_PE;
}

I2c1::~I2c1() {
    /* Модуль гасимо самі: інакше після знищення об'єкта передавач лишиться на
       шині, і наступне відновлення тактуватиме лінії проти живого контролера. */
    I2C1->CR1 &= ~I2C_CR1_PE;
}

std::expected<std::uint8_t, I2cError>
I2c1::read_register(std::uint8_t addr7, std::uint8_t reg) noexcept {
    /* Той самий BUSY, що о другій ночі стоїть при чистих 3.3 В на обох лініях.
       У нормі він знімається за такт-два, тож довге очікування означає не
       зайнятість, а заклинену шину — і кличе процедуру відновлення. */
    if (!bsp::wait_until([]() noexcept { return (I2C1->SR2 & I2C_SR2_BUSY) == 0U; }, kEventTimeout)) {
        return std::unexpected{I2cError::BusBusy};
    }

    I2C1->CR1 |= I2C_CR1_ACK | I2C_CR1_START;
    if (auto ok = wait_flag(I2C_SR1_SB); !ok) {
        return std::unexpected{ok.error()};
    }

    I2C1->DR = static_cast<std::uint16_t>(addr7 << 1);   /* адреса + біт запису */
    if (auto ok = wait_flag(I2C_SR1_ADDR); !ok) {
        return std::unexpected{ok.error()};
    }
    clear_addr_flag();

    I2C1->DR = reg;                                      /* номер регістра в чипі */
    if (auto ok = wait_flag(I2C_SR1_BTF); !ok) {
        return std::unexpected{ok.error()};
    }

    /* Повторний START: віддавати шину між записом номера й читанням не можна,
       інакше чужий мастер зіб'є вказівник регістра всередині веденого. */
    I2C1->CR1 |= I2C_CR1_START;
    if (auto ok = wait_flag(I2C_SR1_SB); !ok) {
        return std::unexpected{ok.error()};
    }

    I2C1->DR = static_cast<std::uint16_t>((addr7 << 1) | 1U);   /* адреса + біт читання */
    if (auto ok = wait_flag(I2C_SR1_ADDR); !ok) {
        return std::unexpected{ok.error()};
    }

    /* Один байт: ACK знімаємо ДО зняття ADDR і ставимо STOP одразу після, і все
       це без переривань. Спізнимося на кілька тактів — чип отримає зайве
       підтвердження й почне віддавати другий байт (RM0008, випадок N = 1). */
    I2C1->CR1 &= ~I2C_CR1_ACK;
    __disable_irq();
    clear_addr_flag();
    I2C1->CR1 |= I2C_CR1_STOP;
    __enable_irq();

    if (auto ok = wait_flag(I2C_SR1_RXNE); !ok) {
        return std::unexpected{ok.error()};
    }
    const auto value = static_cast<std::uint8_t>(I2C1->DR);

    /* Чекаємо, доки апаратура догенерує STOP: START поверх недоробленого STOP —
       класичний спосіб власноруч загнати модуль у вічний BUSY. */
    if (!bsp::wait_until([]() noexcept { return (I2C1->CR1 & I2C_CR1_STOP) == 0U; }, kEventTimeout)) {
        return std::unexpected{I2cError::Timeout};
    }

    I2C1->CR1 |= I2C_CR1_ACK;
    return value;
}

} // namespace hw
