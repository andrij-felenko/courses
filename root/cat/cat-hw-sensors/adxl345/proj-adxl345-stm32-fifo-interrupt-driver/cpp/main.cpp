#include "Adxl345DmaDriver.hpp"
#include "stm32f4xx_hal.h"
#include <cstdio>

// Зовнішня периферія STM32 HAL
extern SPI_HandleTypeDef hspi1;

namespace {
// Екземпляр драйвера акселерометра: SPI1, CS = GPIOA Pin 4, INT1 = GPIOA Pin 0
Sensors::Adxl345DmaDriver g_adxlDriver(&hspi1, GPIOA, GPIO_PIN_4, GPIO_PIN_0);

void Error_Handler() {
    while (true) {
        // Обробка критичної помилки системи
    }
}
}

/**
 * @brief Обробник зовнішнього переривання GPIO EXTI (викликається HAL).
 */
extern "C" void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    g_adxlDriver.onGpioExti(GPIO_Pin);
}

/**
 * @brief Обробник завершення транзакції SPI DMA (викликається HAL).
 */
extern "C" void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef* hspi) {
    if (hspi == &hspi1) {
        g_adxlDriver.onSpiTxRxCplt();
    }
}

/**
 * @brief Головна функція програми.
 */
int main() {
    // Ініціалізація апаратної периферії STM32 HAL
    HAL_Init();

    // Етап 1: Конфігурування ADXL345 (16g, 100Гц, поріг FIFO Watermark = 16 кадрів)
    if (!g_adxlDriver.configure(Sensors::Range::Range_16g, Sensors::DataRate::Rate_100Hz, 16)) {
        Error_Handler();
    }

    // Етап 2: Запуск режиму активного вимірювання
    if (!g_adxlDriver.start()) {
        Error_Handler();
    }

    // Головний цикл обробки даних
    while (true) {
        // Перевірка прапорця готовності нового порції вибірок від DMA
        if (g_adxlDriver.hasNewData()) {
            std::span<const Sensors::AccelSample> samples = g_adxlDriver.getSamples();

            // Обробка отриманих кадрів прискорення
            for (const auto& sample : samples) {
                float x_g = sample.xG();
                float y_g = sample.yG();
                float z_g = sample.zG();

                (void)x_g;
                (void)y_g;
                (void)z_g;
            }

            // Скидання прапорця після зчитування
            g_adxlDriver.clearDataReady();
        }

        // Перехід у режим сну Sleep Mode для зменшення енергоспоживання ЦП до наступного переривання
        HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    }
}
