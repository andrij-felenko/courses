#ifndef DIP_SWITCH_H
#define DIP_SWITCH_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define DIP_SWITCH_MAX_PINS 8

// Структура налаштування прив'язки вхідних GPIO-пінів та масок бітових полів
typedef struct {
    uint8_t pin_numbers[DIP_SWITCH_MAX_PINS]; // Номери вхідних пінів GPIO для ліній DIP-блока
    uint8_t pin_count;                        // Кількість задіяних важелів перемикача (до 8)
    uint8_t address_mask;                     // Побітова маска для виділення поля адреси (наприклад, 0x0F)
    uint8_t address_shift;                    // Зсув праворуч для виділеного поля адреси
    uint8_t mode_mask;                        // Побітова маска для виділення полів режимів (наприклад, 0xF0)
    uint8_t mode_shift;                       // Зсув праворуч для виділеного поля режимів
    uint8_t debounce_samples;                 // Кількість послідовних збігів для підтвердження стабільності
} dip_switch_config_t;

// Структура декодованих даних конфігураційного блока
typedef struct {
    uint8_t raw_pins_state;     // Сирий фізичний стан ліній (0 - замкнено на GND при PULLUP)
    uint8_t config_byte;        // Інвертований конфігураційний байт (1 - увімкнений важіль ON)
    uint8_t device_address;     // Розпаковане й зсунуте значення адреси пристрою
    uint8_t mode_flags;         // Розпаковані прапорці режимів роботи
    bool is_valid;              // Прапор стабільності зчитаного стану після дебаунсу
} dip_switch_data_t;

// Ініціалізація вхідних GPIO-ліній у режим INPUT_PULLUP
void dip_switch_init(const dip_switch_config_t *config);

// Пряме зчитування паралельного байта з інверсією логіки (Active Low -> Active High)
uint8_t dip_switch_read_raw_byte(const dip_switch_config_t *config);

// Декодування конфігураційного байта з виділенням полів адреси й режимів
void dip_switch_decode(const dip_switch_config_t *config, uint8_t raw_byte, dip_switch_data_t *out_data);

// Дебаунс та валідація конфігураційного байта за серією однакових відліків
bool dip_switch_read_stable(const dip_switch_config_t *config, dip_switch_data_t *out_data);

#endif // DIP_SWITCH_H
