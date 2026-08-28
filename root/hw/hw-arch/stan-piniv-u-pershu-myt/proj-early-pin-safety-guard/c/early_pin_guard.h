// early_pin_guard.h
#ifndef EARLY_PIN_GUARD_H
#define EARLY_PIN_GUARD_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Коди результатів верифікації пінів
typedef enum {
    PIN_GUARD_OK                   = 0x00,
    PIN_GUARD_ERR_MISSING_PULLDOWN = 0x01,
    PIN_GUARD_ERR_MISSING_PULLUP   = 0x02,
    PIN_GUARD_ERR_SHORT_TO_GND     = 0x03,
    PIN_GUARD_ERR_SHORT_TO_VDD     = 0x04,
    PIN_GUARD_ERR_PIN_BRIDGED      = 0x05,
    PIN_GUARD_ERR_LOCK_FAILED      = 0x06,
    PIN_GUARD_ERR_CLOCK_FAILED     = 0x07
} PinGuardStatus_t;

// Очікуваний зовнішній стан лінії
typedef enum {
    EXT_PULL_NONE,      // Пін без зовнішньої підтяжки
    EXT_PULL_DOWN_HARD, // Очікується зовнішній резистор 4.7–10 кОм на GND
    EXT_PULL_UP_HARD    // Очікується зовнішній резистор 4.7–10 кОм на VDD
} ExpectedPull_t;

// Режим роботи виводу
typedef enum {
    PIN_TARGET_INPUT,
    PIN_TARGET_OUTPUT_LOW,
    PIN_TARGET_OUTPUT_HIGH
} PinTargetMode_t;

// Опис конфігурації критичного піна
typedef struct {
    uint32_t         port_base;        // Базова адреса регістра GPIO (наприклад, GPIOA_BASE)
    uint8_t          pin_num;          // Номер піна (0 .. 15)
    ExpectedPull_t   expected_pull;    // Очікуваний апаратний стан лінії на платі
    PinTargetMode_t  target_mode;      // Цільовий робочий стан піна
    bool             lock_required;    // Чи блокувати конфігурацію в регістрі LCKR
    const char*      pin_name;         // Назва сигналу для діагностики
} PinGuardConfig_t;

// Результат діагностики порту
typedef struct {
    uint32_t total_pins_tested;
    uint32_t failed_pin_index;
    PinGuardStatus_t failure_reason;
} PinGuardReport_t;

// Головна точка входу ранньої ініціалізації
PinGuardStatus_t EarlyPinGuard_Execute(const PinGuardConfig_t* configs, uint32_t count, PinGuardReport_t* report);

// Апаратний тест виявлення замикань між пінами (Walking Test)
PinGuardStatus_t EarlyPinGuard_VerifyPortBridging(uint32_t port_base, uint16_t pin_mask);

// Аварійний обробник зупинки при виявленні дефекту монтажу
void EarlyPinGuard_FatalErrorHandler(const PinGuardReport_t* report);

#ifdef __cplusplus
}
#endif

#endif // EARLY_PIN_GUARD_H
