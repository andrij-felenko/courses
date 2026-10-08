#include "ina219_driver.hpp"
#include "uart_telemetry.hpp"

#if __has_include("stm32f4xx_hal.h")
#include "stm32f4xx_hal.h"
#endif

// Екземпляри апаратних хендлів STM32 HAL
static I2C_HandleTypeDef hi2c1;
static UART_HandleTypeDef huart2;

// Прототипи системних функцій ініціалізації
static void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_I2C1_Init(void);
static void MX_USART2_UART_Init(void);

int main(void) {
    // 1. Ініціалізація низькорівневої периферії STM32
#if defined(HAL_I2C_MODULE_ENABLED) || defined(STM32F4xx_HAL_H)
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_USART2_UART_Init();
#endif

    // 2. Створення об'єкта телеметрії UART2
    telemetry::UartTelemetry telemetry(&huart2);
    telemetry.sendString("=== STM32 INA219 Power Monitor Initializing ===\r\n");

    // 3. Створення драйвера INA219 для I2C1
    ina219::Ina219Driver ina219(&hi2c1, ina219::kDefaultI2cAddress);

    // Калібрувальні параметри: опір шунта 0.1 Ом, max струм 3.2 А
    constexpr float kShuntResistorOhms = 0.1f;
    constexpr float kMaxCurrentAmperes = 3.2f;

    if (ina219.init(kShuntResistorOhms, kMaxCurrentAmperes) != HAL_OK) {
        telemetry.sendString("[ERROR] INA219 initialization failed on I2C bus!\r\n");
    } else {
        telemetry.sendString("[OK] INA219 successfully initialized and calibrated.\r\n");
    }

    // Режим: 32V Range, PGA /8 (320mV), 12-біт АЦП з 16 вибірками усереднення
    ina219.configure(
        ina219::Ina219BusVoltageRange::Range_32V,
        ina219::Ina219PgaGain::Gain_8_320mV,
        ina219::Ina219AdcResolution::Samples_16_8ms,
        ina219::Ina219AdcResolution::Samples_16_8ms,
        ina219::Ina219Mode::ShuntAndBusContinuous
    );

    // 4. Безкінечний цикл опитування сенсора та виводу вимірюваних параметрів
    while (1) {
        bool conversion_ready = false;

        // Неблокуюча перевірка готовності даних конверсії АЦП (CNVR)
        if (ina219.checkConversionReady(conversion_ready) == HAL_OK && conversion_ready) {
            float v_bus_V = 0.0f;
            float v_shunt_mV = 0.0f;
            float current_mA = 0.0f;
            float power_mW = 0.0f;
            bool is_overflow = false;

            // Комплексне зчитування напруги, струму та потужності
            HAL_StatusTypeDef status = ina219.readAll(v_bus_V, v_shunt_mV, current_mA, power_mW);

            // Неблокуюча перевірка прапорця математичного переповнення (OVF)
            ina219.checkOverflow(is_overflow);

            if (status == HAL_OK) {
                // Завадостійке відправлення телеметрії у послідовний порт UART
                telemetry.sendPowerData(v_bus_V, v_shunt_mV, current_mA, power_mW, is_overflow);
            } else {
                telemetry.sendString("[WARN] Failed to read measurements from INA219!\r\n");
            }
        }

#if defined(HAL_I2C_MODULE_ENABLED) || defined(STM32F4xx_HAL_H)
        HAL_Delay(500); // Період опитування 500 мс
#else
        break;
#endif
    }

    return 0;
}

// Заглушки функцій конфігурації периферії STM32 CubeMX
static void SystemClock_Config(void) {}
static void MX_GPIO_Init(void) {}
static void MX_I2C1_Init(void) {}
static void MX_USART2_UART_Init(void) {}
