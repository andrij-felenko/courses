#ifndef ESP8266_BOOT_PINS_H
#define ESP8266_BOOT_PINS_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Базова адреса регістрів периферії GPIO ESP8266
#define ESP8266_GPIO_BASE           0x60000300U

// Адреси низькорівневих регістрів GPIO
#define ESP8266_GPIO_OUT_REG        (ESP8266_GPIO_BASE + 0x00U) // Зміна вихідних логічних рівнів
#define ESP8266_GPIO_ENABLE_REG     (ESP8266_GPIO_BASE + 0x0CU) // Напрямок виводів (1 = вихід, 0 = вхід)
#define ESP8266_GPIO_IN_REG         (ESP8266_GPIO_BASE + 0x18U) // Зчитування вхідних логічних рівнів

// Бітові маски конфігураційних виводів завантаження (boot-strapping pins)
#define GPIO_PIN_0_BIT              (1U << 0)   // GPIO0: 1 = Flash Boot, 0 = UART Download Mode
#define GPIO_PIN_2_BIT              (1U << 2)   // GPIO2: Вимагає підтяжки до HIGH (1) під час скидання
#define GPIO_PIN_15_BIT             (1U << 15)  // GPIO15: Вимагає підтяжки до LOW (0) під час скидання (1 = SDIO Boot)

// Макрос низькорівневого читання з регістрів
#ifndef REG_READ
#define REG_READ(addr)              (*(volatile uint32_t *)(uintptr_t)(addr))
#endif

// Макрос низькорівневого запису в регістри
#ifndef REG_WRITE
#define REG_WRITE(addr, val)        (*(volatile uint32_t *)(uintptr_t)(addr) = (val))
#endif

/**
 * @brief Перелічуваний тип режимів завантаження ESP8266.
 */
typedef enum {
    BOOT_MODE_FLASH = 0,    ///< Завантаження з SPI Flash (Нормальний режим: GPIO15=0, GPIO0=1, GPIO2=1)
    BOOT_MODE_UART,         ///< Режим програмування через UART (GPIO15=0, GPIO0=0, GPIO2=1)
    BOOT_MODE_SDIO,         ///< Режим завантаження з SD-карти (GPIO15=1)
    BOOT_MODE_INVALID       ///< Неприпустимий стан (наприклад, GPIO2=0 спричиняє апаратне блокування/bootloop)
} boot_mode_t;

/**
 * @brief Структура фіксації зчитаних логічних рівнів на виводах завантаження.
 */
typedef struct {
    bool gpio0_level;       ///< Логічний рівень на GPIO0 (true = High, false = Low)
    bool gpio2_level;       ///< Логічний рівень на GPIO2 (true = High, false = Low)
    bool gpio15_level;      ///< Логічний рівень на GPIO15 (true = High, false = Low)
    boot_mode_t mode;       ///< Визначений апаратний режим завантаження
    uint32_t raw_gpio_in;   ///< Значення регістра GPIO_IN на момент перевірки
} boot_pins_status_t;

/**
 * @brief Конфігураційна структура для опитування та верифікації виводів завантаження.
 */
typedef struct {
    bool enable_internal_pullups;   ///< Увімкнення внутрішніх підтягувальних резисторів після перевірки
    bool strict_flash_check;        ///< Режим суворої верифікації виключно режиму BOOT_MODE_FLASH
    uint32_t sample_count;          ///< Кількість повторних замірів для усунення перехідних процесів і завад
} boot_pins_config_t;

/**
 * @brief Заповнює конфігураційну структуру значеннями за замовчуванням.
 * @param config Вказівник на структуру конфігурації.
 */
void esp8266_boot_pins_default_config(boot_pins_config_t *config);

/**
 * @brief Зчитує стан регістрів GPIO та повертає статус конфігураційних виводів завантаження.
 * @param config Вказівник на налаштування перевірки (або NULL для параметрів за замовчуванням).
 * @return Заповнена структура boot_pins_status_t.
 */
boot_pins_status_t esp8266_read_boot_pins(const boot_pins_config_t *config);

/**
 * @brief Декодує режим завантаження на основі комбінації логічних рівнів.
 * @param gpio15 Стан виводу GPIO15.
 * @param gpio0 Стан виводу GPIO0.
 * @param gpio2 Стан виводу GPIO2.
 * @return Декодований режим boot_mode_t.
 */
boot_mode_t esp8266_decode_boot_mode(bool gpio15, bool gpio0, bool gpio2);

/**
 * @brief Повертає текстовий опис режиму завантаження українською мовою.
 * @param mode Режим завантаження.
 * @return Рядок з описом режиму.
 */
const char* esp8266_boot_mode_to_str(boot_mode_t mode);

/**
 * @brief Безпечно переналаштовує конфігураційний вивід як периферійний інтерфейс.
 * @param pin Номер GPIO (0, 2 або 15).
 * @param is_output Напрямок: true - вихід, false - вхід.
 * @param initial_level Початковий рівень (якщо вихід).
 * @return true у разі успішного конфігурування, false якщо вивід недопустимий.
 */
bool esp8266_reconfigure_pin_safe(uint8_t pin, bool is_output, bool initial_level);

#endif // ESP8266_BOOT_PINS_H
