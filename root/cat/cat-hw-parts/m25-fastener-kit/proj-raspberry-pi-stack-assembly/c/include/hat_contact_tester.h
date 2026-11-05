/**
 * @file hat_contact_tester.h
 * @brief Оголошення структур конфігурації тестування шини I2C, статистики пакетних збоїв
 *        та сигнатур функцій перевірки контакту для Raspberry Pi HAT (M2.5 fastener kit).
 */

#ifndef HAT_CONTACT_TESTER_H
#define HAT_CONTACT_TESTER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Конфігурація для тестування контакту шини I2C шилда HAT.
 */
typedef struct {
    const char *i2c_device_path; ///< Шлях до пристрою шини I2C (наприклад, "/dev/i2c-1")
    uint8_t slave_address;       ///< Адреса веденого пристрою (I2C slave address) на HAT
    uint8_t reg_address;         ///< Адреса регістра для опитування (перевірка зв'язку)
    int total_cycles;            ///< Загальна кількість циклів стрес-тестування (наприклад, 1000)
    uint32_t delay_ms;           ///< Затримка між циклами в мілісекундах
} hat_test_config_t;

/**
 * @brief Статистика пакетних збоїв та успішних транзакцій.
 */
typedef struct {
    int successful_transactions; ///< Кількість успішних транзакцій I2C
    int failed_transactions;     ///< Кількість збоїв (помилок open, ioctl, read/write)
    double failure_rate_percent; ///< Відсоток збоїв від загальної кількості
} hat_test_stats_t;

/**
 * @brief Ініціалізує структуру конфігурації значеннями за замовчуванням.
 * 
 * @param config Вказівник на структуру конфігурації.
 */
void hat_tester_init_config(hat_test_config_t *config);

/**
 * @brief Виконує повний цикл стрес-тестування контактів шилда HAT через /dev/i2c-1.
 * 
 * @param config Вказівник на конфігурацію тесту.
 * @param stats Вказівник на структуру для збереження результатів статистики.
 * @return true у разі успішного завершення тесту, false у разі критичної помилки ініціалізації.
 */
bool hat_tester_run_stress_test(const hat_test_config_t *config, hat_test_stats_t *stats);

/**
 * @brief Виводить детальний діагностичний звіт про якість монтажу стека,
 *        перекосу контактів GPIO та моменту затягування стійок М2.5.
 * 
 * @param stats Вказівник на зібрану статистику збоїв.
 */
void hat_tester_print_report(const hat_test_stats_t *stats);

#endif // HAT_CONTACT_TESTER_H
