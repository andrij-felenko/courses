#pragma once

#include <cstdint>
#include <cstddef>

// ============================================================================
// Конфігурація апаратного шару HIC (Hardware Interface Circuit) DAPLink
// ============================================================================

// Виводи SWD-інтерфейсу (SWCLK, SWDIO, SWO)
#define PIN_SWCLK_PORT     GPIOA
#define PIN_SWCLK_PIN      (1U << 5)   // PA5
#define PIN_SWDIO_PORT     GPIOA
#define PIN_SWDIO_PIN      (1U << 6)   // PA6
#define PIN_SWO_PORT       GPIOA
#define PIN_SWO_PIN        (1U << 7)   // PA7

// Вивід скидання цільового мікроконтролера (nRESET)
#define PIN_NRESET_PORT    GPIOB
#define PIN_NRESET_PIN     (1U << 0)   // PB0

// Виводи буферів узгодження рівнів (Level Shifter Direction Controls)
#define PIN_DIR_SWCLK_PORT GPIOB
#define PIN_DIR_SWCLK_PIN  (1U << 1)   // PB1: 1 = Вихід на ціль, 0 = Вхід
#define PIN_DIR_SWDIO_PORT GPIOB
#define PIN_DIR_SWDIO_PIN  (1U << 2)   // PB2: 1 = Вихід на ціль, 0 = Вхід з цілі

// Виводи послідовного порту UART (CDC Pass-through)
#define PIN_UART_TX_PORT   GPIOA
#define PIN_UART_TX_PIN    (1U << 2)   // PA2
#define PIN_UART_RX_PORT   GPIOA
#define PIN_UART_RX_PIN    (1U << 3)   // PA3

// Індикаційні світлодіоди стану
#define PIN_LED_CONNECTED_PORT GPIOC
#define PIN_LED_CONNECTED_PIN  (1U << 13) // PC13: Статус підключення CMSIS-DAP
#define PIN_LED_RUNNING_PORT   GPIOC
#define PIN_LED_RUNNING_PIN    (1U << 14) // PC14: Статус виконання/прошивання

// Макроси швидкого маскування й прямого керування GPIO
#define SWCLK_SET_HIGH()   (PIN_SWCLK_PORT->BSRR = PIN_SWCLK_PIN)
#define SWCLK_SET_LOW()    (PIN_SWCLK_PORT->BRR  = PIN_SWCLK_PIN)
#define SWDIO_SET_HIGH()   (PIN_SWDIO_PORT->BSRR = PIN_SWDIO_PIN)
#define SWDIO_SET_LOW()    (PIN_SWDIO_PORT->BRR  = PIN_SWDIO_PIN)
#define SWDIO_GET_IN()     ((PIN_SWDIO_PORT->IDR & PIN_SWDIO_PIN) != 0U)

#define NRESET_ASSERT()    (PIN_NRESET_PORT->BRR  = PIN_NRESET_PIN) // Активний низький рівень
#define NRESET_RELEASE()   (PIN_NRESET_PORT->BSRR = PIN_NRESET_PIN) // Відпускання у Hi-Z/High

#define DIR_SWDIO_OUT()    (PIN_DIR_SWDIO_PORT->BSRR = PIN_DIR_SWDIO_PIN)
#define DIR_SWDIO_IN()     (PIN_DIR_SWDIO_PORT->BRR  = PIN_DIR_SWDIO_PIN)

/**
 * @brief Перелічення режимів роботи шини SWD
 */
enum class SwdMode : uint8_t {
    Disconnected = 0,
    SwdMode      = 1,
    JtagMode     = 2
};

/**
 * @brief Клас абстракції апаратного шару плати програматора DAPLink (TargetBoard)
 */
class TargetBoard {
public:
    TargetBoard() = default;
    ~TargetBoard() = default;

    /**
     * @brief Ініціалізація системного тактування та периферії GPIO
     */
    void init();

    /**
     * @brief Налаштування режимів сигнальних ліній SWD (SWCLK, SWDIO, nRESET)
     * @param mode Режим роботи шини
     */
    void configureSwd(SwdMode mode);

    /**
     * @brief Керування буферами узгодження рівнів для SWDIO
     * @param outputDirection true - напрямок на вихід (Output), false - на вхід (Input)
     */
    void setSwdioDirection(bool outputDirection);

    /**
     * @brief Керування лінією апаратного скидання nRESET
     * @param assertReset true - притиснути до землі (Reset active), false - відпустити (Release)
     */
    void setResetPin(bool assertReset);

    /**
     * @brief Перевірка стану лінії скидання цільового мікроконтролера
     * @return true якщо лінія скидання активна (0 В)
     */
    [[nodiscard]] bool isResetAsserted() const;

    /**
     * @brief Керування світлодіодами статусу програматора
     * @param connected Світлодіод з'єднання CMSIS-DAP
     * @param running Світлодіод активності прошивання/відлагодження
     */
    void setLedStatus(bool connected, bool running);

    /**
     * @brief Ініціалізація апаратного периферійного модуля UART (CDC Pass-through)
     * @param baudRate Швидкість передачі даних у бодах (наприклад, 115200)
     */
    void initUart(uint32_t baudRate);

private:
    SwdMode currentMode_{SwdMode::Disconnected};
    uint32_t systemClockHz_{72000000U}; // 72 МГц за замовчуванням
};
