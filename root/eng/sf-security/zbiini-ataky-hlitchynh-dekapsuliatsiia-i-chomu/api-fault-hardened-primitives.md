# 📋 Інтерфейси відмовостійких типів та бар'єрів виконання

Довідник програмних інтерфейсів, структур даних та апаратних бітових масок для проектування низькорівневого коду, стійкого до апаратних збоїв (Fault Injection), тактових аномалій та зондування напівпровідникового кристала.

## 1. Базові типи даних та коди станів

У традиційних мовах програмування булеві типи `bool` або `_Bool` представляються у пам'яті одним байтом, де нуль `0x00` відповідає значенню «хибність», а `0x01` (або будь-яке ненульове значення) — значенню «істина». На рівні мікропроцесорного ядра такі змінні розміщуються в 32-бітних регістрах загального призначення (`R0`–`R12` в архітектурі ARM Cortex-M). Для перетворення логічної хибності `0x00000000` на логічну істину `0x00000001` зловмиснику достатньо викликати збій, який перекине рівно один молодший біт у регістрі або на шині пам'яті.

Щоб унеможливити подібну атаку, у захищеному коді стандартні примітиви замінюються на 32-бітні багатозначні типи даних із фіксованою відстанню Геммінга. Відстань Геммінга визначає кількість бітових позицій, у яких значення відрізняються одне від одного. Для захищених перевірок мінімальна допустима відстань становить не менше 16 бітів.

| Символічна константа | Шістнадцяткове значення | Двійкове представлення (32 біти) | Опис та призначення |
|---|---|---|---|
| `HARDENED_TRUE` | `0x5555AAAA` | `01010101010101011010101010101010` | Логічне підтвердження успішної авторизації чи валідності підпису. |
| `HARDENED_FALSE` | `0xAAAA5555` | `10101010101010100101010101010101` | Логічне відхилення операції, помилка перевірки. |
| `HARDENED_INVALID` | `0x00000000` | `00000000000000000000000000000000` | Стан скидання або неініціалізованої пам'яті. Заборонений для авторизації. |
| `HARDENED_FAULT` | `0xFFFFFFFF` | `11111111111111111111111111111111` | Стан зафіксованої апаратної тривоги. Спричиняє негайне блокування. |
| `HARDENED_STATUS_OK` | `0x3C3C5A5A` | `00111100001111000101101001011010` | Успішне завершення функції з верифікацією інваріантів. |
| `HARDENED_STATUS_ERROR` | `0xC3C3A5A5` | `11000011110000111010010110100101` | Помилка виконання криптографічної операції. |

Між константами `HARDENED_TRUE` та `HARDENED_FALSE` відстань Геммінга дорівнює точно 32: кожен біт значення є побітовою інверсією відповідного біта протилежного значення. Будь-який частковий апаратний збій, що зачепить від 1 до 31 біта, переведе регістр у недопустимий проміжний стан, який не пройде фінальну перевірку.

Ймовірність того, що випадковий фізичний шум напруги або тактового сигналу перекине всі 32 біти регістра у строго визначений черговий патерн нулів та одиниць, оцінюється як мізерно мала величина. Якщо кожен біт змінюється незалежно з імовірністю `p = 0.05`, сумарна ймовірність успішного випадкового переходу між валідними станами становить `p^32 ≈ 2.3 · 10^-42`.

---

## 2. Заголовкові інтерфейси та примітиви компіляції

Нижче наведено повні інтерфейсні заголовки мовами C та C++, які реалізують безпечне порівняння, асемблерні бар'єри оптимізації та контроль шляху виконання.

:::tabs
```c
#ifndef HARDENED_PRIMITIVES_H
#define HARDENED_PRIMITIVES_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t hardened_bool_t;
typedef uint32_t hardened_status_t;

#define HARDENED_TRUE            ((hardened_bool_t)0x5555AAAAU)
#define HARDENED_FALSE           ((hardened_bool_t)0xAAAA5555U)
#define HARDENED_INVALID         ((hardened_bool_t)0x00000000U)
#define HARDENED_FAULT           ((hardened_bool_t)0xFFFFFFFFU)

#define HARDENED_STATUS_OK       ((hardened_status_t)0x3C3C5A5AU)
#define HARDENED_STATUS_ERROR    ((hardened_status_t)0xC3C3A5A5U)

/**
 * @brief Асемблерний бар'єр оптимізації компілятора.
 * Запобігає об'єднанню або видаленню повторних перевірок компілятором.
 */
#define HARDENED_BARRIER()       __asm__ volatile("" ::: "memory")

/**
 * @brief Безпечне порівняння двох 32-бітних величин на строгу рівність.
 * @param a Перший операнд.
 * @param b Другий операнд.
 * @return HARDENED_TRUE у разі рівності, інакше HARDENED_FALSE.
 */
static inline hardened_bool_t hardened_equal(uint32_t a, uint32_t b) {
    HARDENED_BARRIER();
    uint32_t diff = a ^ b;
    HARDENED_BARRIER();
    
    /* Подвійна перевірка з прямим та комплементарним обчисленням */
    if (diff == 0U) {
        HARDENED_BARRIER();
        if ((a ^ ~b) == 0xFFFFFFFFU) {
            return HARDENED_TRUE;
        }
    }
    return HARDENED_FALSE;
}

/**
 * @brief Перевірка відмовостійкого статусу на відповідність значенню УСПІХ.
 * @param val Перевірюваний статус.
 * @return HARDENED_TRUE якщо статус валідний, інакше HARDENED_FALSE.
 */
static inline hardened_bool_t hardened_verify_success(hardened_status_t val) {
    HARDENED_BARRIER();
    if (val == HARDENED_STATUS_OK) {
        HARDENED_BARRIER();
        if ((val ^ ~HARDENED_STATUS_OK) == 0xFFFFFFFFU) {
            return HARDENED_TRUE;
        }
    }
    return HARDENED_FALSE;
}

/**
 * @brief Негайне блокування пристрою при виявленні невідповідності інваріантів.
 */
void hardened_panic_lockout(void);

#ifdef __cplusplus
}
#endif

#endif /* HARDENED_PRIMITIVES_H */
```
```cpp
#ifndef HARDENED_PRIMITIVES_HPP
#define HARDENED_PRIMITIVES_HPP

#include <cstdint>
#include <concepts>
#include <span>

namespace security {

enum class Bool : uint32_t {
    True    = 0x5555AAAAU,
    False   = 0xAAAA5555U,
    Invalid = 0x00000000U,
    Fault   = 0xFFFFFFFFU
};

enum class Status : uint32_t {
    Ok      = 0x3C3C5A5AU,
    Error   = 0xC3C3A5A5U,
    Fault   = 0xFFFFFFFFU
};

/**
 * @brief Бар'єр пам'яті для запобігання оптимізаціям мертвого коду (Dead Code Elimination).
 */
inline void memory_barrier() noexcept {
    asm volatile("" ::: "memory");
}

/**
 * @brief Шаблонне безпечне порівняння скалярних цілочисельних типів.
 */
template <std::integral T>
[[nodiscard]] inline Bool safe_compare_equal(T a, T b) noexcept {
    memory_barrier();
    const auto ua = static_cast<uint32_t>(a);
    const auto ub = static_cast<uint32_t>(b);
    const auto diff = ua ^ ub;
    memory_barrier();
    
    if (diff == 0U) {
        memory_barrier();
        if ((ua ^ ~ub) == 0xFFFFFFFFU) {
            return Bool::True;
        }
    }
    return Bool::False;
}

/**
 * @brief Клас захисту графа виконання програми (Flow Integrity Guard).
 */
class ExecutionGuard {
public:
    constexpr explicit ExecutionGuard(uint32_t seed) noexcept 
        : accumulated_token_(seed), initial_seed_(seed) {}

    void record_step(uint32_t step_signature) noexcept {
        memory_barrier();
        accumulated_token_ ^= step_signature;
        memory_barrier();
    }

    [[nodiscard]] bool verify_path(uint32_t expected_final_mask) const noexcept {
        memory_barrier();
        const uint32_t expected = initial_seed_ ^ expected_final_mask;
        const uint32_t current = accumulated_token_;
        memory_barrier();
        return (current == expected) && ((current ^ ~expected) == 0xFFFFFFFFU);
    }

private:
    volatile uint32_t accumulated_token_;
    uint32_t initial_seed_;
};

[[noreturn]] void panic_lockout() noexcept;

} // namespace security

#endif /* HARDENED_PRIMITIVES_HPP */
```
:::

---

## 3. Контракти функцій та інваріанти безпеки

Кожна функція у захищеному API має суворий контракт, який описує поведінку системи до, під час та після виконання операції:

1. **Передумови (Preconditions):**
   - Усі вхідні буфери та дескриптори ключів повинні бути перевірені на ненульові покажчики та коректні межі пам'яті до передачі в ядро обробки.
   - Поточний стан системи у регістрі статусу повинен відповідати дозволеному режиму (наприклад, стан ініціалізації або стан відкритої сесії).
2. **Постумови (Postconditions):**
   - Функція завжди повертає строго типізоване багатобітове значення (`HARDENED_TRUE` або `HARDENED_FALSE`). Повернення проміжних значень або нульових байтів розцінюється як апаратна аварія.
   - Усі проміжні криптографічні контексти та розширені ключі в оперативній пам'яті повинні бути перезаписані нулями за допомогою захищеної функції очищення перед поверненням керування.
3. **Інваріанти виконання (Invariants):**
   - Інваріант взаємного доповнення: для будь-якої змінної `x` та її тіньової копії `x_shadow` завжди виконується умова `x ^ x_shadow = 0xFFFFFFFF`.
   - Інваріант неподільності: критичні операції верифікації виконуються в атомарному контексті з вимкненими маскованими перериваннями для запобігання підміні даних через обробники переривань або канали прямого доступу до пам'яті (DMA).

---

## 4. Апаратний контролер безпеки та конфігураційні регістри

У захищених мікроконтролерах керування детекторами збоїв, активним екраном металізації та схемами аварійного знищення ключів реалізовано через виділений периферійний блок Tamper and Fault Controller (TFC).

### 4.1 Карта регістрів периферійного модуля (Базова адреса `0x4002B000`)

| Регістр | Зсув адреси | Права доступу | Опис функціонального блоку |
|---|---|---|---|
| `TFC_CR` | `0x00` | Читання / Запис | Головний регістр конфігурації захисту (Control Register). |
| `TFC_SR` | `0x04` | Лише читання | Регістр стану та джерел зафіксованих апаратних тривог (Status Register). |
| `TFC_IER` | `0x08` | Читання / Запис | Регістр дозволу немаскованих переривань безпеки (Interrupt Enable). |
| `TFC_SCR` | `0x0C` | Лише запис | Регістр скидання прапорців тривоги (Status Clear Register). |
| `TFC_SECR` | `0x10` | Читання / Запис | Регістр налаштування активної сітки екранування (Shield Config). |
| `TFC_ZCR` | `0x14` | Читання / Запис | Регістр конфігурації апаратного обнулення ключів (Zeroization Control). |

### 4.2 Бітові поля керування та прапорці тривог

Детальний розподіл бітових масок у регістрах `TFC_CR` та `TFC_SR`:

- **Біт 0 (`TFC_CR_GLITCH_EN`, `0x00000001`):** Увімкнення аналогового віконного детектора напруги живлення ядра (Voltage Glitch Detector). При падінні напруги нижче 1.08 В або зростанні вище 1.32 В генерує тривогу.
- **Біт 1 (`TFC_CR_CLK_MON_EN`, `0x00000002`):** Увімкнення монітора тактової частоти (Clock Monitor). Фіксує раптові зміни тривалості напівперіодів тактового сигналу та пропуск імпульсів.
- **Біт 2 (`TFC_CR_TEMP_MON_EN`, `0x00000004`):** Активація сенсора екстремальних температур кристала (діапазон спрацьовування: нижче −40 °C або вище +125 °C).
- **Біт 4 (`TFC_CR_SHIELD_EN`, `0x00000010`):** Активація активної захисної сітки верхнього шару металізації (Top Metal Tamper Shield).
- **Біт 8 (`TFC_CR_ZEROIZE_ON_TRIP`, `0x00000100`):** Дозвіл миттєвого апаратного скидання пам'яті резервних ключів (BBRAM Zeroization) при спрацьовуванні будь-якого з увімкнених сенсорів безпеки.
- **Біт 0 у `TFC_SR` (`TFC_SR_GLITCH_FLAG`, `0x00000001`):** Прапорець зафіксованого апаратного просідання або викиду напруги живлення.
- **Біт 4 у `TFC_SR` (`TFC_SR_SHIELD_CUT_FLAG`, `0x00000010`):** Прапорець обриву, замикання або зміни ємності ліній захисного екрана кристала.

---

## 5. Процедура ініціалізації та обробка апаратних тривог

Під час старту системи модуль апаратного захисту повинен бути сконфігурований до початку виконання будь-яких криптографічних операцій або перевірок цифрового підпису прошивки.

:::tabs
```c
#include "hardened_primitives.h"

#define TFC_BASE_ADDR            0x4002B000U
#define TFC_CR                   (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x00U))
#define TFC_IER                  (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x08U))
#define TFC_SR                   (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x04U))
#define TFC_ZCR                  (*(volatile uint32_t *)(TFC_BASE_ADDR + 0x14U))

#define TFC_CONFIG_SECURE_MASK   (0x00000117U) /* Glitch + Clock + Temp + Shield + Zeroize */
#define TFC_INTERRUPT_ENABLE     (0x00000001U) /* NMI Security Interrupt */

void hardware_security_init(void) {
    HARDENED_BARRIER();
    
    /* Крок 1: Увімкнення схеми швидкого розряду захищеної пам'яті ключів */
    TFC_ZCR = 0x000000A5U; /* Ключ активації схеми Zeroization */
    HARDENED_BARRIER();
    
    /* Крок 2: Активація всіх сенсорів моніторингу та активного екрана */
    TFC_CR = TFC_CONFIG_SECURE_MASK;
    HARDENED_BARRIER();
    
    /* Крок 3: Дозвіл генерації немаскованого переривання NMI */
    TFC_IER = TFC_INTERRUPT_ENABLE;
    HARDENED_BARRIER();
    
    /* Верифікація успішного запуску апаратної системи захисту */
    if ((TFC_CR & TFC_CONFIG_SECURE_MASK) != TFC_CONFIG_SECURE_MASK) {
        hardened_panic_lockout();
    }
}

/* Обробник немаскованого переривання апаратної тривоги */
void NMI_Handler(void) {
    HARDENED_BARRIER();
    /* Апаратна схема автоматично очищає ключі, програмний обробник зупиняє ядро */
    while (1) {
        __asm__ volatile("wfi");
    }
}
```
```cpp
#include "hardened_primitives.hpp"

namespace hardware {

class SecuritySubsystem {
public:
    static constexpr uintptr_t BaseAddress = 0x4002B000U;

    struct alignas(uint32_t) Registers {
        volatile uint32_t cr;
        volatile uint32_t sr;
        volatile uint32_t ier;
        volatile uint32_t scr;
        volatile uint32_t secr;
        volatile uint32_t zcr;
    };

    static void initialize() noexcept {
        auto *regs = reinterpret_cast<Registers *>(BaseAddress);
        security::memory_barrier();

        constexpr uint32_t ZeroizeUnlockKey = 0x000000A5U;
        constexpr uint32_t EnableAllSensors = 0x00000117U; // Glitch + Clock + Temp + Shield + Zeroize
        constexpr uint32_t EnableNmiMask    = 0x00000001U;

        regs->zcr = ZeroizeUnlockKey;
        security::memory_barrier();

        regs->cr = EnableAllSensors;
        security::memory_barrier();

        regs->ier = EnableNmiMask;
        security::memory_barrier();

        if ((regs->cr & EnableAllSensors) != EnableAllSensors) {
            security::panic_lockout();
        }
    }

    [[nodiscard]] static bool has_tamper_event() noexcept {
        auto *regs = reinterpret_cast<Registers *>(BaseAddress);
        security::memory_barrier();
        return (regs->sr != 0U);
    }
};

} // namespace hardware
```
:::

Обробник немаскованого переривання (NMI) виконується з найвищим пріоритетом у системі, який неможливо заблокувати звичайними інструкціями заборони переривань `CPSID i`. Коли сенсор напруги чи захисна сітка фіксують втручання:
1. Апаратний контролер безпеки миттєво відключає лінії живлення від комірок пам'яті BBRAM і закорочує їх на землю, гарантуючи повне стирання секретних ключів за час менше 10 наносекунд.
2. Процесор перериває виконання поточної інструкції і переходить за вектором NMI.
3. Програмний обробник виконує інструкцію нескінченного очікування `WFI` (Wait For Interrupt) або ініціює примусове апаратне перезавантаження через системний таймер Watchdog із виставленням прапорця постійного блокування пристрою.

Використання цих інтерфейсів гарантує узгоджену поведінку апаратного та програмного шарів: будь-яке фізичне втручання або збій викликає негайне спрацьовування апаратних компараторів, а програмний шар блокує подальший хід виконання інструкцій за допомогою бар'єрів і багатобітових інваріантів.
