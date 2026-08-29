// Вимір температури PT100 через ADS1220: 3-провідне підключення,
// логометрична опора на R_ref = 3.3 кОм, одиничні перетворення по 20 SPS
// і готовність результату за апаратним перериванням DRDY.
//
// Виводи (STM32G0): SPI1 на PA5/PA6/PA7, CS на PA4, DRDY на PB0.
// Тактування ядра лишається таким, як його налаштував стартовий код.

#include <array>
#include <cstdio>
#include <optional>
#include <string_view>

#include "stm32g0xx_hal.h"

#include "ads1220.hpp"
#include "pt100.hpp"
#include "spi_device.hpp"

namespace {

// Адреси периферії — це приведення числа до вказівника, тож constexpr
// вони бути не можуть; лишається звичайна незмінна змінна.
GPIO_TypeDef* const     kCsPort   = GPIOA;
constexpr std::uint16_t kCsPin    = GPIO_PIN_4;
GPIO_TypeDef* const     kDrdyPort = GPIOB;
constexpr std::uint16_t kDrdyPin  = GPIO_PIN_0;

SPI_HandleTypeDef  spi1{};
UART_HandleTypeDef uart2{};

// Драйвер живе стільки ж, скільки програма, але будується вже після
// того, як HAL підняв шину, — звідси optional замість глобального об'єкта.
std::optional<rtd::SpiDevice> bus;
std::optional<rtd::Ads1220>   sensor;

void report(std::string_view text) {
    HAL_UART_Transmit(&uart2,
                      reinterpret_cast<std::uint8_t*>(const_cast<char*>(text.data())),
                      static_cast<std::uint16_t>(text.size()),
                      100);
}

void gpioInit() {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    GPIO_InitTypeDef chipSelect{};
    chipSelect.Pin   = kCsPin;
    chipSelect.Mode  = GPIO_MODE_OUTPUT_PP;
    chipSelect.Pull  = GPIO_NOPULL;
    chipSelect.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_WritePin(kCsPort, kCsPin, GPIO_PIN_SET);
    HAL_GPIO_Init(kCsPort, &chipSelect);

    // DRDY — вихід із відкритим стоком, який АЦП притискає до нуля,
    // коли результат готовий. Звідси підтяжка вгору й спадний фронт.
    GPIO_InitTypeDef dataReady{};
    dataReady.Pin  = kDrdyPin;
    dataReady.Mode = GPIO_MODE_IT_FALLING;
    dataReady.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(kDrdyPort, &dataReady);

    HAL_NVIC_SetPriority(EXTI0_1_IRQn, 2, 0);
    HAL_NVIC_EnableIRQ(EXTI0_1_IRQn);
}

HAL_StatusTypeDef spiInit() {
    __HAL_RCC_SPI1_CLK_ENABLE();

    spi1.Instance               = SPI1;
    spi1.Init.Mode              = SPI_MODE_MASTER;
    spi1.Init.Direction         = SPI_DIRECTION_2LINES;
    spi1.Init.DataSize          = SPI_DATASIZE_8BIT;
    // Режим 1: тактовий сигнал у спокої низький, дані знімаються
    // по другому фронту — саме такий обмін чекає ADS1220.
    spi1.Init.CLKPolarity       = SPI_POLARITY_LOW;
    spi1.Init.CLKPhase          = SPI_PHASE_2EDGE;
    spi1.Init.NSS               = SPI_NSS_SOFT;
    spi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_32;  // ~2 МГц
    spi1.Init.FirstBit          = SPI_FIRSTBIT_MSB;
    spi1.Init.TIMode            = SPI_TIMODE_DISABLE;
    spi1.Init.CRCCalculation    = SPI_CRCCALCULATION_DISABLE;

    return HAL_SPI_Init(&spi1);
}

HAL_StatusTypeDef uartInit() {
    __HAL_RCC_USART2_CLK_ENABLE();

    uart2.Instance        = USART2;
    uart2.Init.BaudRate   = 115200;
    uart2.Init.WordLength = UART_WORDLENGTH_8B;
    uart2.Init.StopBits   = UART_STOPBITS_1;
    uart2.Init.Parity     = UART_PARITY_NONE;
    uart2.Init.Mode       = UART_MODE_TX_RX;
    uart2.Init.HwFlowCtl  = UART_HWCONTROL_NONE;

    return HAL_UART_Init(&uart2);
}

}  // namespace

// Обробник спаду DRDY. Тут не читають результат по SPI: обмін довгий,
// а переривання має лише позначити, що чекати вже нема чого.
extern "C" void HAL_GPIO_EXTI_Falling_Callback(std::uint16_t pin) {
    if (pin == kDrdyPin && sensor) {
        sensor->onDataReady();
    }
}

int main() {
    HAL_Init();
    gpioInit();

    if (uartInit() != HAL_OK || spiInit() != HAL_OK) {
        for (;;) {  // без шини говорити нема ні з ким і нема чим
        }
    }

    bus.emplace(spi1, kCsPort, kCsPin);
    sensor.emplace(*bus, 3300.0F, 16.0F);  // еталон 0.01 %, 5 ppm/°C; підсилення 16

    std::array<char, 96> line{};

    if (const auto ready = sensor->init(); !ready) {
        std::snprintf(line.data(), line.size(), "ADS1220 не піднявся: %.*s\r\n",
                      static_cast<int>(rtd::describe(ready.error()).size()),
                      rtd::describe(ready.error()).data());
        report(line.data());
        for (;;) {
        }
    }

    // Зміщення нуля міряємо один раз при старті, на прогрітій платі.
    // Воно дрібне, але при 1.9 мкВ на сотку градуса дрібне вже видно.
    if (const auto zeroed = sensor->calibrateOffset(); !zeroed) {
        std::snprintf(line.data(), line.size(), "калібрування нуля не вдалося: %.*s\r\n",
                      static_cast<int>(rtd::describe(zeroed.error()).size()),
                      rtd::describe(zeroed.error()).data());
        report(line.data());
    }

    for (;;) {
        const auto ohms = sensor->readResistance();
        if (!ohms) {
            std::snprintf(line.data(), line.size(), "вимір зірвано: %.*s\r\n",
                          static_cast<int>(rtd::describe(ohms.error()).size()),
                          rtd::describe(ohms.error()).data());
            report(line.data());
            HAL_Delay(1000);
            continue;
        }

        const auto celsius = pt100::celsiusAt(*ohms);
        if (!celsius) {
            std::snprintf(line.data(), line.size(), "опір %.3f Ом поза діапазоном PT100\r\n",
                          static_cast<double>(*ohms));
            report(line.data());
            HAL_Delay(1000);
            continue;
        }

        std::snprintf(line.data(), line.size(), "R = %.4f Ом   T = %.3f C\r\n",
                      static_cast<double>(*ohms), static_cast<double>(*celsius));
        report(line.data());

        // Пауза між вимірами — це ще й час, коли струми збудження вимкнені
        // й датчик остигає від власного розігріву.
        HAL_Delay(1000);
    }
}
