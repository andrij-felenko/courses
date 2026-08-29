// platform_stm32f4.cpp — порт під STM32F407. Єдиний файл, що знає регістри.
//
// Розводка стенда:
//   PA0 — дільник 10 кОм + NTC 10 кОм · PA1 — дільник 100к/100к від акумулятора
//   PB0 — ключ передавача · PB1 — підігрів плати · PB2 — дозвіл заряду
//   PB6 — I2C1_SCL, PB7 — I2C1_SDA (зовнішні підтяжки 4.7 кОм)
//
// Жодне очікування апаратної події не робиться вічним циклом: у полі зависла
// шина або мертвий АЦП — це буденність, і кожен такий цикл перетворився б на
// скидання від сторожового таймера замість помилки, яку видно у журналі.

#include "field/platform.hpp"

#include "stm32f4xx.h"

namespace field::plat {
namespace {

// Не constexpr: адреси периферії в CMSIS — це reinterpret_cast, і сталою
// виразу він не буває навіть тоді, коли число за ним відоме на етапі збірки.
GPIO_TypeDef* const kLoadPort = GPIOB;
GPIO_TypeDef* const kI2cPort = GPIOB;
constexpr std::uint8_t kSclPin = 6;
constexpr std::uint8_t kSdaPin = 7;

// Скільки обертів порожнього циклу терпимо, чекаючи прапорця периферії.
// Число з запасом: при 168 МГц це ≈1 мс, довша за будь-яку штатну подію.
constexpr std::uint32_t kSpinLimit = 40'000;

constexpr std::uint8_t loadPin(Load load) noexcept {
    switch (load) {
        case Load::Radio: return 0;
        case Load::Heater: return 1;
        case Load::Charger: return 2;
    }
    return 0;
}

volatile std::uint32_t g_ticks = 0;
std::uint32_t g_coreHz = kHclkBaseHz;
std::uint32_t g_resetFlags = 0;
bool g_loadState[3]{};

void gpioMode(GPIO_TypeDef* port, std::uint8_t pin, std::uint32_t mode) noexcept {
    port->MODER = (port->MODER & ~(3u << (pin * 2))) | (mode << (pin * 2));
}

void gpioAf(GPIO_TypeDef* port, std::uint8_t pin, std::uint32_t af) noexcept {
    const std::uint8_t idx = pin >> 3;
    const std::uint8_t shift = (pin & 7u) * 4;
    port->AFR[idx] = (port->AFR[idx] & ~(0xFu << shift)) | (af << shift);
}

void backupDomainInit() noexcept {
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    PWR->CR |= PWR_CR_DBP;  // без цього BKPxR лишаються тільки для читання

    RCC->CSR |= RCC_CSR_LSION;
    for (std::uint32_t spin = 0; spin < kSpinLimit; ++spin) {
        if ((RCC->CSR & RCC_CSR_LSIRDY) != 0) {
            break;
        }
    }

    // RTCSEL пишеться лише раз на життя батарейки резервного домену: повторний
    // вибір джерела вимагав би скидання домену, а разом із ним стерлася б уся
    // історія аварій — саме те, заради чого домен і взято.
    if ((RCC->BDCR & RCC_BDCR_RTCEN) == 0) {
        RCC->BDCR |= RCC_BDCR_RTCSEL_1;  // 0b10 — LSI
        RCC->BDCR |= RCC_BDCR_RTCEN;
    }
}

void adcInit() noexcept {
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;
    ADC->CCR = (ADC->CCR & ~ADC_CCR_ADCPRE) | ADC_CCR_ADCPRE_0;  // APB2/4

    // 480 тактів на вибірку. Дільник із NTC на 10 кОм має високий вихідний
    // опір; коротка вибірка не встигає зарядити конденсатор пристрою
    // вибірки-зберігання, і замір «пливе» слідом за сусіднім каналом.
    ADC1->SMPR2 |= (7u << (static_cast<unsigned>(Channel::Ntc) * 3)) |
                   (7u << (static_cast<unsigned>(Channel::Vbat) * 3));
    ADC1->SQR1 = 0;  // одна перетворка в послідовності
    ADC1->CR2 |= ADC_CR2_ADON;
}

// BKP0R..BKP19R лежать у пам'яті підряд, тож індексуються як масив.
volatile std::uint32_t* bkpWord(std::uint8_t index) noexcept {
    return &(&RTC->BKP0R)[index];
}

std::expected<void, HwError> i2cWait(volatile std::uint32_t& reg, std::uint32_t mask) noexcept {
    for (std::uint32_t spin = 0; spin < kSpinLimit; ++spin) {
        if ((reg & mask) != 0) {
            return {};
        }
        if ((I2C1->SR1 & I2C_SR1_AF) != 0) {
            I2C1->SR1 &= ~I2C_SR1_AF;
            I2C1->CR1 |= I2C_CR1_STOP;
            return std::unexpected{HwError::Nack};  // раба немає, але лінії живі
        }
    }
    return std::unexpected{HwError::Timeout};
}

std::expected<void, HwError> i2cStart(std::uint8_t addr7, bool read) noexcept {
    if ((I2C1->SR2 & I2C_SR2_BUSY) != 0) {
        return std::unexpected{HwError::Busy};  // лінію тримають ще до нашого старту
    }

    I2C1->CR1 |= I2C_CR1_START;
    if (auto ok = i2cWait(I2C1->SR1, I2C_SR1_SB); !ok) {
        return ok;
    }

    I2C1->DR = static_cast<std::uint8_t>((addr7 << 1) | (read ? 1u : 0u));
    if (auto ok = i2cWait(I2C1->SR1, I2C_SR1_ADDR); !ok) {
        return ok;
    }

    static_cast<void>(I2C1->SR1);  // читання SR1+SR2 знімає ADDR
    static_cast<void>(I2C1->SR2);
    return {};
}

}  // namespace

void init() {
    // Прапори скидання знімаємо ОДИН раз і зберігаємо: RMVF стирає їх
    // назавжди, і другий охочий дізнатися причину старту нічого не побачить.
    g_resetFlags = RCC->CSR;
    RCC->CSR |= RCC_CSR_RMVF;

    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;

    gpioMode(GPIOA, 0, 3);  // аналоговий режим
    gpioMode(GPIOA, 1, 3);

    for (const Load load : {Load::Radio, Load::Heater, Load::Charger}) {
        const std::uint8_t pin = loadPin(load);
        kLoadPort->BSRR = 1u << (pin + 16);  // спершу нуль
        gpioMode(kLoadPort, pin, 1);         // потім вихід
        g_loadState[static_cast<unsigned>(load)] = false;
    }

    backupDomainInit();
    adcInit();

    SystemCoreClock = g_coreHz;
    static_cast<void>(SysTick_Config(g_coreHz / 1000));
}

std::uint32_t resetFlagsRaw() noexcept { return g_resetFlags; }

std::chrono::milliseconds now() noexcept { return std::chrono::milliseconds{g_ticks}; }

void delayFor(std::chrono::microseconds span) noexcept {
    // Тіло циклу — чотири такти ядра. Точність тут не потрібна: найкоротша
    // затримка у проєкті — півперіод ручного тактування шини, 5 мкс.
    volatile std::uint32_t loops =
        (g_coreHz / 4'000'000) * static_cast<std::uint32_t>(span.count());
    while (loops != 0) {
        --loops;
    }
}

void setCoreDivider(unsigned log2) noexcept {
    static constexpr std::uint32_t kHpre[5] = {0, 8, 9, 10, 11};  // /1 /2 /4 /8 /16
    if (log2 > 4) {
        log2 = 4;
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_HPRE) | (kHpre[log2] << RCC_CFGR_HPRE_Pos);
    g_coreHz = kHclkBaseHz >> log2;
    SystemCoreClock = g_coreHz;

    // SysTick рахує від HCLK, тож без перезарядки мілісекунда стала б удвічі
    // довшою, а разом із нею — усі періоди в головному циклі.
    static_cast<void>(SysTick_Config(g_coreHz / 1000));
}

std::uint32_t coreHz() noexcept { return g_coreHz; }

void setLoad(Load load, bool on) noexcept {
    const std::uint8_t pin = loadPin(load);
    kLoadPort->BSRR = on ? (1u << pin) : (1u << (pin + 16));
    g_loadState[static_cast<unsigned>(load)] = on;
}

bool loadOn(Load load) noexcept { return g_loadState[static_cast<unsigned>(load)]; }

std::expected<std::uint16_t, HwError> readAdc(Channel channel) noexcept {
    ADC1->SR &= ~ADC_SR_EOC;
    ADC1->SQR3 = static_cast<std::uint32_t>(channel);
    ADC1->CR2 |= ADC_CR2_SWSTART;

    for (std::uint32_t spin = 0; spin < kSpinLimit; ++spin) {
        if ((ADC1->SR & ADC_SR_EOC) != 0) {
            return static_cast<std::uint16_t>(ADC1->DR);
        }
    }
    return std::unexpected{HwError::Timeout};
}

std::expected<std::uint32_t, HwError> bkpRead(std::uint8_t index) noexcept {
    if (index >= kBkpWords) {
        return std::unexpected{HwError::BadIndex};
    }
    return *bkpWord(index);
}

std::expected<void, HwError> bkpWrite(std::uint8_t index, std::uint32_t value) noexcept {
    if (index >= kBkpWords) {
        return std::unexpected{HwError::BadIndex};
    }
    *bkpWord(index) = value;
    return {};
}

void i2cInit() noexcept {
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    // Повне скидання блока. Після ручного тактування периферія лишається
    // у стані посеред транзакції, і без SWRST перший же START зависає.
    I2C1->CR1 = I2C_CR1_SWRST;
    I2C1->CR1 = 0;

    gpioMode(kI2cPort, kSclPin, 2);  // альтернативна функція
    gpioMode(kI2cPort, kSdaPin, 2);
    gpioAf(kI2cPort, kSclPin, 4);  // AF4 — I2C1
    gpioAf(kI2cPort, kSdaPin, 4);
    kI2cPort->OTYPER |= (1u << kSclPin) | (1u << kSdaPin);  // відкритий стік

    I2C1->CR2 = 42;    // APB1 = 42 МГц
    I2C1->CCR = 210;   // 42 МГц / (2 · 100 кГц) — стандартний режим
    I2C1->TRISE = 43;  // 1 мкс фронту при 42 МГц
    I2C1->CR1 |= I2C_CR1_PE;
}

std::expected<void, HwError> i2cProbe(std::uint8_t addr7) noexcept {
    const auto result = i2cStart(addr7, false);
    I2C1->CR1 |= I2C_CR1_STOP;
    return result;
}

std::expected<void, HwError> i2cReadReg(std::uint8_t addr7, std::uint8_t reg,
                                        std::span<std::uint8_t> buf) noexcept {
    if (buf.empty()) {
        return std::unexpected{HwError::BadIndex};
    }

    if (auto ok = i2cStart(addr7, false); !ok) {
        return ok;
    }

    I2C1->DR = reg;
    if (auto ok = i2cWait(I2C1->SR1, I2C_SR1_BTF); !ok) {
        return ok;
    }

    I2C1->CR1 |= I2C_CR1_ACK;
    if (auto ok = i2cStart(addr7, true); !ok) {  // повторний START, тепер на читання
        I2C1->CR1 |= I2C_CR1_STOP;
        return ok;
    }

    for (std::size_t i = 0; i < buf.size(); ++i) {
        if (i + 1 == buf.size()) {
            // Останній байт квитуємо запереченням і одразу ставимо STOP:
            // інакше раб почне віддавати наступний і затримає SDA внизу.
            I2C1->CR1 &= ~I2C_CR1_ACK;
            I2C1->CR1 |= I2C_CR1_STOP;
        }
        if (auto ok = i2cWait(I2C1->SR1, I2C_SR1_RXNE); !ok) {
            I2C1->CR1 |= I2C_CR1_STOP;
            return ok;
        }
        buf[i] = static_cast<std::uint8_t>(I2C1->DR);
    }
    return {};
}

PinControl::PinControl() noexcept {
    I2C1->CR1 &= ~I2C_CR1_PE;  // периферія відпускає ніжки
    gpioMode(kI2cPort, kSclPin, 1);
    gpioMode(kI2cPort, kSdaPin, 1);
    kI2cPort->OTYPER |= (1u << kSclPin) | (1u << kSdaPin);
    kI2cPort->BSRR = (1u << kSclPin) | (1u << kSdaPin);  // обидві відпущені
}

PinControl::~PinControl() {
    i2cInit();  // SWRST плюс повернення ніжок під AF4
}

void PinControl::writeScl(bool high) noexcept {
    kI2cPort->BSRR = high ? (1u << kSclPin) : (1u << (kSclPin + 16));
}

void PinControl::writeSda(bool high) noexcept {
    kI2cPort->BSRR = high ? (1u << kSdaPin) : (1u << (kSdaPin + 16));
}

bool PinControl::readScl() const noexcept { return (kI2cPort->IDR & (1u << kSclPin)) != 0; }

bool PinControl::readSda() const noexcept { return (kI2cPort->IDR & (1u << kSdaPin)) != 0; }

void watchdogStart(std::chrono::milliseconds timeout) noexcept {
    // IWDG живиться від власного LSI ≈32 кГц і не спиняється разом
    // із зірваним основним тактуванням — саме тому він, а не таймер ядра.
    const auto ticks = static_cast<std::uint32_t>(timeout.count());
    IWDG->KR = 0x5555;  // дозвіл запису PR/RLR
    IWDG->PR = 3;       // /32 → приблизно 1 кГц
    IWDG->RLR = (ticks > 4095) ? 4095 : ticks;
    IWDG->KR = 0xAAAA;  // перезавантажити лічильник
    IWDG->KR = 0xCCCC;  // пуск; зупинити вже не можна
}

void watchdogKick() noexcept { IWDG->KR = 0xAAAA; }

void systemReset() noexcept {
    NVIC_SystemReset();
    for (;;) {
    }
}

}  // namespace field::plat

extern "C" void SysTick_Handler() { ++field::plat::g_ticks; }
