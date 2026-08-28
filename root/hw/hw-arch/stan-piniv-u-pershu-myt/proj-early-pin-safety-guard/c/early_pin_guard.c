// early_pin_guard.c
#include "early_pin_guard.h"

// Регістрова карта порту GPIO (STM32 Cortex-M)
typedef struct {
    volatile uint32_t MODER;   // 0x00: Режим роботи (Input, Output, AF, Analog)
    volatile uint32_t OTYPER;  // 0x04: Тип виходу (Push-Pull, Open-Drain)
    volatile uint32_t OSPEEDR; // 0x08: Швидкість перемикання
    volatile uint32_t PUPDR;   // 0x0C: Внутрішні підтяжки
    volatile uint32_t IDR;     // 0x10: Вхідні дані
    volatile uint32_t ODR;     // 0x14: Вихідні дані
    volatile uint32_t BSRR;    // 0x18: Атомарне встановлення/скидання
    volatile uint32_t LCKR;    // 0x1C: Регістр блокування конфігурації
    volatile uint32_t AFR[2];  // 0x20: Альтернативні функції
} GpioHw_t;

// Апаратна затримка для завершення перехідних процесів ємності лінії
static void EarlyGuard_DelayCycles(volatile uint32_t cycles) {
    while (cycles > 0) {
        cycles--;
        __asm volatile ("nop");
    }
}

// 5-крокова процедура блокування конфігурації регістра LCKR
static bool EarlyGuard_LockPinConfiguration(GpioHw_t* gpio, uint8_t pin) {
    uint32_t lock_mask = (1UL << pin);
    uint32_t lock_key = lock_mask | (1UL << 16); // Біт LCKK = 16

    // Послідовність фіксації в кремнії:
    gpio->LCKR = lock_key;  // Крок 1: LCKK = 1, маска піна
    gpio->LCKR = lock_mask; // Крок 2: LCKK = 0, маска піна
    gpio->LCKR = lock_key;  // Крок 3: LCKK = 1, маска піна
    (void)gpio->LCKR;       // Крок 4: Читання LCKR

    // Крок 5: Друге читання має повернути LCKK = 1
    uint32_t verify = gpio->LCKR;
    return (verify & (1UL << 16)) != 0;
}

// Тест на виявлення замикань між пінами одного порту
PinGuardStatus_t EarlyPinGuard_VerifyPortBridging(uint32_t port_base, uint16_t pin_mask) {
    GpioHw_t* gpio = (GpioHw_t*)port_base;

    // Всі піни за маскою налаштовуємо як Input з Pull-Up
    for (uint8_t pin = 0; pin < 16; pin++) {
        if (pin_mask & (1U << pin)) {
            uint32_t shift2 = pin * 2;
            gpio->MODER &= ~(0x3UL << shift2);
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x1UL << shift2);
        }
    }
    EarlyGuard_DelayCycles(300);

    // Перевіряємо Walking Zero
    for (uint8_t pin = 0; pin < 16; pin++) {
        if (pin_mask & (1U << pin)) {
            uint32_t shift2 = pin * 2;

            // Перемикаємо пін у вихід Low
            gpio->BSRR = (1UL << (pin + 16));
            gpio->MODER = (gpio->MODER & ~(0x3UL << shift2)) | (0x1UL << shift2);
            EarlyGuard_DelayCycles(100);

            // Зчитуємо IDR: нуль повинен бути ТІЛЬКИ на піні 'pin'
            uint32_t idr_val = gpio->IDR & pin_mask;
            uint32_t expected_val = pin_mask & ~(1UL << pin);

            if (idr_val != expected_val) {
                // Виявлено взаємний вплив або замикання!
                return PIN_GUARD_ERR_PIN_BRIDGED;
            }

            // Повертаємо у вхід Pull-Up
            gpio->MODER &= ~(0x3UL << shift2);
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x1UL << shift2);
            EarlyGuard_DelayCycles(100);
        }
    }

    return PIN_GUARD_OK;
}

PinGuardStatus_t EarlyPinGuard_Execute(const PinGuardConfig_t* configs, uint32_t count, PinGuardReport_t* report) {
    if (!configs || count == 0) {
        return PIN_GUARD_OK;
    }

    // Бар'єр пам'яті для гарантування готовності шин периферії
    __asm volatile ("dsb 0xF" ::: "memory");

    for (uint32_t i = 0; i < count; i++) {
        const PinGuardConfig_t* cfg = &configs[i];
        GpioHw_t* gpio = (GpioHw_t*)cfg->port_base;
        uint8_t pin = cfg->pin_num;
        uint32_t shift2 = pin * 2;

        // -------------------------------------------------------------
        // КРОК 1: ДІАГНОСТИКА ЦІЛІСНОСТІ ЗОВНІШНЬОЇ ПІДТЯЖКИ
        // -------------------------------------------------------------
        if (cfg->expected_pull == EXT_PULL_DOWN_HARD) {
            // Перемикаємо пін у режим Input (MODER = 00b)
            gpio->MODER &= ~(0x3UL << shift2);

            // Вмикаємо внутрішній PULL-UP (PUPDR = 01b)
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x1UL << shift2);

            // Очікуємо заряду/розряду паразитної ємності лінії (стала часу RC ≈ 4 мкс)
            EarlyGuard_DelayCycles(300);

            // Якщо на платі є справний резистор 4.7 кОм на землю, IDR зобов'язаний бути 0!
            if ((gpio->IDR & (1UL << pin)) != 0) {
                // Пін підтягнувся до 3.3В -> зовнішній резистор обірваний або лінія закорочена на VDD!
                if (report) {
                    report->failed_pin_index = i;
                    report->failure_reason = PIN_GUARD_ERR_MISSING_PULLDOWN;
                    report->total_pins_tested = i;
                }
                return PIN_GUARD_ERR_MISSING_PULLDOWN;
            }

            // Перевіряємо реакцію при внутрішньому PULL-DOWN (PUPDR = 10b)
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x2UL << shift2);
            EarlyGuard_DelayCycles(300);

            if ((gpio->IDR & (1UL << pin)) != 0) {
                if (report) {
                    report->failed_pin_index = i;
                    report->failure_reason = PIN_GUARD_ERR_SHORT_TO_VDD;
                    report->total_pins_tested = i;
                }
                return PIN_GUARD_ERR_SHORT_TO_VDD;
            }
        }
        else if (cfg->expected_pull == EXT_PULL_UP_HARD) {
            // Перемикаємо пін у режим Input (MODER = 00b)
            gpio->MODER &= ~(0x3UL << shift2);

            // Вмикаємо внутрішній PULL-DOWN (PUPDR = 10b)
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x2UL << shift2);
            EarlyGuard_DelayCycles(300);

            // Якщо зовнішній резистор 4.7 кОм до 3.3В присутній, IDR зобов'язаний бути 1!
            if ((gpio->IDR & (1UL << pin)) == 0) {
                if (report) {
                    report->failed_pin_index = i;
                    report->failure_reason = PIN_GUARD_ERR_MISSING_PULLUP;
                    report->total_pins_tested = i;
                }
                return PIN_GUARD_ERR_MISSING_PULLUP;
            }
        }

        // -------------------------------------------------------------
        // КРОК 2: АТОМАРНЕ ПОПЕРЕДНЄ ЗВЕДЕННЯ ВИХОДУ ТА НАЛАШТУВАННЯ
        // -------------------------------------------------------------
        if (cfg->target_mode == PIN_TARGET_OUTPUT_LOW) {
            // Скидаємо в 0 через регістр BSRR ДО ввімкнення режиму виходу
            gpio->BSRR = (1UL << (pin + 16));

            // Вмикаємо внутрішній Pull-Down для максимальної стійкості
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x2UL << shift2);

            // Обмежуємо швидкість наростання (Low Speed) для усунення перешкод
            gpio->OSPEEDR &= ~(0x3UL << shift2);

            // Перемикаємо в режим виходу (MODER = 01b)
            gpio->MODER = (gpio->MODER & ~(0x3UL << shift2)) | (0x1UL << shift2);
        }
        else if (cfg->target_mode == PIN_TARGET_OUTPUT_HIGH) {
            // Встановлюємо в 1 через регістр BSRR ДО ввімкнення режиму виходу
            gpio->BSRR = (1UL << pin);

            // Вмикаємо внутрішній Pull-Up
            gpio->PUPDR = (gpio->PUPDR & ~(0x3UL << shift2)) | (0x1UL << shift2);

            gpio->OSPEEDR &= ~(0x3UL << shift2);

            // Перемикаємо в режим виходу (MODER = 01b)
            gpio->MODER = (gpio->MODER & ~(0x3UL << shift2)) | (0x1UL << shift2);
        }
        else {
            // Цільовий режим — вхід
            gpio->MODER &= ~(0x3UL << shift2);
        }

        // -------------------------------------------------------------
        // КРОК 3: АПАРАТНЕ БЛОКУВАННЯ РЕГІСТРІВ
        // -------------------------------------------------------------
        if (cfg->lock_required) {
            if (!EarlyGuard_LockPinConfiguration(gpio, pin)) {
                if (report) {
                    report->failed_pin_index = i;
                    report->failure_reason = PIN_GUARD_ERR_LOCK_FAILED;
                    report->total_pins_tested = i;
                }
                return PIN_GUARD_ERR_LOCK_FAILED;
            }
        }
    }

    if (report) {
        report->total_pins_tested = count;
        report->failed_pin_index = 0;
        report->failure_reason = PIN_GUARD_OK;
    }

    return PIN_GUARD_OK;
}

// Обробник фатальної апаратної відмови
void EarlyPinGuard_FatalErrorHandler(const PinGuardReport_t* report) {
    // 1. Повне відключення глобальних переривань
    __asm volatile ("cpsid i" ::: "memory");

    // 2. Апаратне блокування виходів ШІМ аварійним сигналом Break (якщо доступно)
    // 3. Зациклення ядра у безпечному стані з мінімальним енергоспоживанням
    while (1) {
        __asm volatile ("wfi");
    }
}
