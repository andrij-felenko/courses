#ifndef POWER_DOWN_EEPROM_H
#define POWER_DOWN_EEPROM_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file power_down_eeprom.h
 * @brief Оголошення модуля виявлення просідання живлення (PVD/BOD) та збереження даних в EEPROM.
 */

#define POWER_DOWN_MAGIC_HEADER 0x57415452U /* "WATR" у 16-й системі */

/**
 * @brief Структура запису накопичених даних для EEPROM/Flash.
 */
typedef struct __attribute__((packed)) {
    uint32_t magic;               /**< Магічний заголовок верифікації */
    double total_volume_liters;   /**< Сумарний накопичений об'єм води у літрах */
    uint64_t total_pulse_count;   /**< Загальна кількість імпульсів */
    uint32_t write_counter;       /**< Лічильник циклів запису */
    uint16_t crc16;               /**< Контрольна сума CRC16-CCITT */
} power_down_record_t;

/**
 * @brief Конфігурація модуля Power-Down.
 */
typedef struct {
    uint16_t eeprom_address;      /**< Адреса комірки в non-volatile пам'яті */
    uint32_t vcc_threshold_mv;    /**< Поріг спрацьовування PVD переривання у мВ */
} power_down_config_t;

/**
 * @brief Ініціалізація модуля PVD та зчитування стану.
 * @param config Вказівник на конфігураційні параметри.
 * @return true у разі успішної ініціалізації.
 */
bool power_down_eeprom_init(const power_down_config_t *config);

/**
 * @brief ISR-обробник аварійного переривання виявлення просідання живлення (PVD).
 * Забезпечує миттєвий запис поточного об'єму у non-volatile пам'ять.
 */
void power_down_pvd_isr(void);

/**
 * @brief Аварійне або примусове збереження даних у EEPROM.
 * @param volume_liters Накопичений об'єм води.
 * @param pulse_count Загальний лічильник імпульсів.
 * @return true, якщо збереження пройшло успішно з валідною контрольною сумою.
 */
bool power_down_eeprom_save_now(double volume_liters, uint64_t pulse_count);

/**
 * @brief Відновлення збереженого об'єму під час включення/перезавантаження мікроконтролера.
 * @param out_volume_liters Вказівник для зчитування відновленого об'єму у літрах.
 * @param out_pulse_count Вказівник для зчитування відновленої кількості імпульсів.
 * @return true, якщо CRC16 та магічне число пройшли перевірку цілісності.
 */
bool power_down_eeprom_restore(double *out_volume_liters, uint64_t *out_pulse_count);

/**
 * @brief Обчислення контрольної суми CRC16-CCITT для масиву даних.
 * @param data Вказівник на буфер даних.
 * @param length Довжина буфера у байтах.
 * @return Розрахована 16-бітна контрольна сума.
 */
uint16_t power_down_crc16(const uint8_t *data, size_t length);

#endif /* POWER_DOWN_EEPROM_H */
