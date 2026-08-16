# 📋 Специфікація програмного інтерфейсу розрахунку фазових рівноваг

Цей довідник описує програмний контракт (API), структури даних, сигнатури функцій, коди помилок та специфікацію JSON-конфігурації бібліотеки `libgibbs_phase`, призначеної для інтеграції розрахунку правил фаз Гіббса у промислові системи чисельного термодинамічного моделювання, геологічні симулятори та САПР матеріалів.

### Призначення та архітектура бібліотеки

Бібліотека `libgibbs_phase` розроблена як легкий, високопродуктивний middleware-компонент із нульовими зовнішніми залежностями. Вона слугує проміжним шаром між фазовими базами даних (формати TDB, Thermo-Calc) та чисельними оптимізаторами термодинамічної рівноваги (такими як Cantera, OpenCALPHAD чи Aspen Plus).

Головні задачі API полягають у наступному:
1. **Валідація фазових конфігурацій:** Швидка перевірка коректності заданого користувачем або автоматичним алгоритмом фазового стану до початку нелінійних ітерацій.
2. **Обчислення ступеней вільності:** Динамічний розрахунок `F` та `F'` для довільної кількості компонентів, реакцій, додаткових обмежень та зовнішніх полів.
3. **Класифікація стану:** Автоматичне присвоєння категорії стану (від `GIBBS_STATE_OVERCONSTRAINED` до `GIBBS_STATE_MULTIVARIANT`).
4. **Забезпечення FFI-сумісності:** Надання чистого C-ABI для прямого виклику з мов Python, Rust, C#, Julia та MATLAB.

### Детальний розбір структур даних та типів

Для забезпечення повної сумісності між різними мовами програмування C-інтерфейс бібліотеки використовує строго фіксовані за розміром типи даних із `stdint.h` (`uint32_t`, `int32_t`, `uint8_t`), а C++ заголовок дає ідіоматичні типи з простору імен `std`.

#### 1. Коди помилок та статуси повернення (`GibbsStatus`)

Кожен виклик функцій бібліотеки повертає цілочисельний код статусу `GibbsStatus`. Значення `0` (`GIBBS_STATUS_SUCCESS`) гарантує, що розрахунок виконано успішно й отриманий результат у структурі `GibbsPhaseAnalysis` є коректним.

Від'ємні коди свідчать про помилки у вхідних даних:
- `GIBBS_STATUS_INVALID_POINTER` (`-1`): Передано нулевий вказівник (NULL) на одну зі структур конфігурації чи результату.
- `GIBBS_STATUS_INVALID_SPECIES_COUNT` (`-2`): Кількість речовин `N` вказана меншою за 1, що є фізично неможливим для будь-якої середовищної системи.
- `GIBBS_STATUS_INVALID_PHASE_COUNT` (`-3`): Кількість фаз `P` вказана меншою за 1 (система має містити хоча б одну фазу).
- `GIBBS_STATUS_NEGATIVE_COMPONENTS` (`-4`): Кількість незалежних компонентів `C = N - R - r` виявилася меншою за 1 внаслідок надлишкової кількості заданих хімічних реакцій або обмежень.
- `GIBBS_STATUS_OVERCONSTRAINED_SYSTEM` (`-5`): Заданий фазовий стан має від'ємне число ступеней вільності (`F < 0`), тобто є перевизначеною термодинамічною системою.

:::tabs
```cpp
enum class Status : std::int32_t {
    Success = 0,               // Успішне виконання розрахунку
    InvalidPointer = -1,       // Помилка: передано нульовий вказівник
    InvalidSpeciesCount = -2,  // Помилка: кількість речовин N < 1
    InvalidPhaseCount = -3,    // Помилка: кількість фаз P < 1
    NegativeComponents = -4,   // Помилка: незалежні компоненти C < 1
    OverconstrainedSystem = -5 // Помилка: перевизначена система (F < 0)
};
```
```c
typedef enum {
    GIBBS_STATUS_SUCCESS               =  0, /* Успішне виконання розрахунку */
    GIBBS_STATUS_INVALID_POINTER       = -1, /* Передано нулевий вказівник (NULL) */
    GIBBS_STATUS_INVALID_SPECIES_COUNT = -2, /* Кількість речовин N < 1 */
    GIBBS_STATUS_INVALID_PHASE_COUNT   = -3, /* Кількість фаз P < 1 */
    GIBBS_STATUS_NEGATIVE_COMPONENTS   = -4, /* Кількість компонентів C = N - R - r < 1 */
    GIBBS_STATUS_OVERCONSTRAINED_SYSTEM = -5  /* Перевизначена система (F < 0) */
} GibbsStatus;
```
:::

#### 2. Перелічувач класифікації фазового стану (`GibbsStateClassification`)

Класифікація виражає термодинамічний характер стану та геометрію образу на фазовій діаграмі:
- `GIBBS_STATE_OVERCONSTRAINED` (`-1`): Перевизначена система (`F < 0`), термодинамічно неможливий стан;
- `GIBBS_STATE_NONVARIANT` (`0`): Нонваріантний стан (`F = 0`), зображується точкою на фазовій діаграмі (наприклад, потрійна точка або евтоктична точка);
- `GIBBS_STATE_UNIVARIANT` (`1`): Моноваріантний стан (`F = 1`), зображується лінією (криві випаровування, ліквідусу);
- `GIBBS_STATE_BIVARIANT` (`2`): Біваріантний стан (`F = 2`), зображується площиною або двовимірним полем;
- `GIBBS_STATE_MULTIVARIANT` (`3`): Мультиваріантний стан (`F > 2`), багатовимірний термодинамічний простір.

:::tabs
```cpp
enum class Classification : std::int32_t {
    Overconstrained = -1, // F < 0: неможливий стан (система перевизначена)
    Nonvariant = 0,      // F = 0: нонваріантний стан (зображується точкою)
    Univariant = 1,      // F = 1: моноваріантний стан (зображується лінією)
    Bivariant = 2,       // F = 2: біваріантний стан (зображується поверхнею/полем)
    Multivariant = 3     // F > 2: мультиваріантний стан (багатовимірний простір)
};
```
```c
typedef enum {
    GIBBS_STATE_OVERCONSTRAINED = -1, /* F < 0: неможливий стан (система перевизначена) */
    GIBBS_STATE_NONVARIANT      =  0, /* F = 0: нонваріантний стан (зображується точкою) */
    GIBBS_STATE_UNIVARIANT      =  1, /* F = 1: моноваріантний стан (зображується лінією) */
    GIBBS_STATE_BIVARIANT       =  2, /* F = 2: біваріантний стан (зображується поверхнею/полем) */
    GIBBS_STATE_MULTIVARIANT    =  3  /* F > 2: мультиваріантний стан (багатовимірний простір) */
} GibbsStateClassification;
```
:::

#### 3. Структура конфігурації вхідної системи (`GibbsSystemConfig`)

Структура описує фізичний склад та фіксовані умови системи:
- `species_count`: Загальна кількість речовин `N` (молекулярних видів або іонів);
- `reactions_count`: Кількість незалежних хімічних реакцій `R`;
- `constraints_count`: Кількість додаткових співвідношень `r` (наприклад, електронейтральність);
- `phases_count`: Кількість рівноважних фаз `P`;
- `is_isobaric`: Прапорець зафіксованого тиску (`1` якщо `P = const`, інакше `0`);
- `is_isothermal`: Прапорець зафіксованої температури (`1` якщо `T = const`, інакше `0`);
- `external_fields_m`: Кількість додаткових зовнішніх інтенсивних полів `m`.

:::tabs
```cpp
struct Config {
    std::uint32_t species_count{1};     // N: загальна кількість речовин
    std::uint32_t reactions_count{0};   // R: кількість хімічних реакцій
    std::uint32_t constraints_count{0}; // r: додаткові обмеження
    std::uint32_t phases_count{1};      // P: кількість рівноважних фаз
    bool is_isobaric{false};            // 1 якщо P = const
    bool is_isothermal{false};          // 1 якщо T = const
    std::uint32_t external_fields_m{0}; // m: зовнішні поля
};
```
```c
typedef struct {
    uint32_t species_count;      /* N: загальна кількість хімічних речовин (молекул/іонних видів) */
    uint32_t reactions_count;    /* R: кількість незалежних хімічних реакцій */
    uint32_t constraints_count;  /* r: кількість додаткових обмежень (електронейтральність) */
    uint32_t phases_count;       /* P: кількість співіснуючих рівноважних фаз */
    uint8_t  is_isobaric;        /* 1 якщо тиск фіксований (P = const), інакше 0 */
    uint8_t  is_isothermal;      /* 1 якщо температура фіксована (T = const), інакше 0 */
    uint32_t external_fields_m;  /* m: кількість додаткових інтенсивних полів (магнітне тощо) */
} GibbsSystemConfig;
```
:::

#### 4. Структура результату розрахунку (`GibbsPhaseAnalysis`)

Структура заповнюється функцією аналізу й містить розраховані параметри:
- `independent_components_C`: Загальне число незалежних компонентів `C = N - R - r`;
- `degrees_of_freedom_F`: Обчислене число вільних інтенсивних параметрів `F`;
- `classification`: Перелічувальне значення категорії стану;
- `is_physically_realizable`: Булевий прапорець (`1` якщо `F ≥ 0`, `0` якщо `F < 0`).

:::tabs
```cpp
struct Analysis {
    std::int32_t components_C{0};       // Кількість компонентів C = N - R - r
    std::int32_t freedom_F{0};          // Підсумкові ступені вільності F
    Classification classification{Classification::Nonvariant};
    bool is_realizable{true};           // true якщо F >= 0
};
```
```c
typedef struct {
    int32_t  independent_components_C; /* Кількість незалежних компонентів C = N - R - r */
    int32_t  degrees_of_freedom_F;     /* Підсумкова кількість ступеней вільності F */
    GibbsStateClassification classification; /* Категорія термодинамічного стану */
    uint8_t  is_physically_realizable;  /* 1 якщо F >= 0 (стан можливий), 0 якщо F < 0 */
} GibbsPhaseAnalysis;
```
:::

### Специфікація API-інтерфейсу в коді

Опис викликів надається мовою C++20 у формі заголовочної бібліотеки без залежностей, а також мовою C у вигляді декларації C-ABI функцій.

:::tabs
```cpp
// C++20 Header-only Wrapper API (gibbs_phase.hpp)
#pragma once
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace gibbs {

// Головна обчислювальна функція аналізу фазової рівноваги
[[nodiscard]] constexpr std::expected<Analysis, Status>
analyze_phase_equilibrium(const Config& config) noexcept {
    if (config.species_count == 0) {
        return std::unexpected(Status::InvalidSpeciesCount);
    }
    if (config.phases_count == 0) {
        return std::unexpected(Status::InvalidPhaseCount);
    }

    const auto C = static_cast<std::int32_t>(config.species_count) -
                   static_cast<std::int32_t>(config.reactions_count) -
                   static_cast<std::int32_t>(config.constraints_count);

    if (C < 1) {
        return std::unexpected(Status::NegativeComponents);
    }

    std::int32_t offset = 2;
    if (config.is_isobaric) {
        --offset;
    }
    if (config.is_isothermal) {
        --offset;
    }

    const std::int32_t F = C - static_cast<std::int32_t>(config.phases_count) + 
                           offset + static_cast<std::int32_t>(config.external_fields_m);

    Analysis result{};
    result.components_C = C;
    result.freedom_F = F;
    result.is_realizable = (F >= 0);

    if (F < 0) {
        result.classification = Classification::Overconstrained;
    } else if (F == 0) {
        result.classification = Classification::Nonvariant;
    } else if (F == 1) {
        result.classification = Classification::Univariant;
    } else if (F == 2) {
        result.classification = Classification::Bivariant;
    } else {
        result.classification = Classification::Multivariant;
    }

    return result;
}

// Конвертація коду статусу у людиночитаний текстовий опис
[[nodiscard]] constexpr std::string_view status_to_string(Status status) noexcept {
    switch (status) {
        case Status::Success: return "Успішно";
        case Status::InvalidPointer: return "Помилка: нульовий вказівник";
        case Status::InvalidSpeciesCount: return "Помилка: некоректна кількість речовин N";
        case Status::InvalidPhaseCount: return "Помилка: некоректна кількість фаз P";
        case Status::NegativeComponents: return "Помилка: кількість компонентів C < 1";
        case Status::OverconstrainedSystem: return "Помилка: перевизначена система (F < 0)";
    }
    return "Невідомий статус";
}

} // namespace gibbs
```
```c
/* C C-ABI Header (gibbs_phase.h) */
#ifndef GIBBS_PHASE_H
#define GIBBS_PHASE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Виконує розрахунок правил фаз Гіббса для заданої конфігурації.
 * Параметри:
 *   config - вказівник на заповнену структуру конфігурації.
 *   result - вказівник на структуру, куди буде записано результат.
 * Повертає:
 *   GIBBS_STATUS_SUCCESS у разі успіху або відповідний код помилки.
 */
GibbsStatus gibbs_analyze_equilibrium(
    const GibbsSystemConfig* config,
    GibbsPhaseAnalysis* result
);

/*
 * Повертає текстовий описовий рядок для заданого коду статусу.
 */
const char* gibbs_status_to_string(GibbsStatus status);

#ifdef __cplusplus
}
#endif

#endif /* GIBBS_PHASE_H */
```
:::

### Потокобезпечність, пам'ять та гарантії продуктивності

Для досягнення максимальної надійності у реальному часі та у розпаралелених симуляціях (OpenMP, MPI, TBB) API надає наступні жорсткі гарантії:
1. **Потокобезпечність та реінтрабельність (Thread Safety & Reentrancy):** Жодна функція не має глобального чи статичного стану, не використовує локів або mutex. Будь-яка кількість потоків може одночасно викликати `gibbs_analyze_equilibrium` без блокувань.
2. **Відсутність динамічної пам'яті (Zero Memory Allocation):** Обчислення виконуються суто у реєстрах процесора або на стеку виклику. Бібліотека не робить викликів `malloc`, `free` чи `realloc`, що гарантує відсутність фрагментації оперативної пам'яті.
3. **Строга відповідність C-ABI (C Alignment Standard):** Структури затиснуті під стандартні межі вирівнювання C. Це виключає загрозу розсуву полів при передачі вказівників через механізми Foreign Function Interface (FFI) у мовах Python (бібліотека `ctypes`), Rust (модуль `bindgen`), C# (`P/Invoke`) та Julia.

### Обробка крайових випадків та виправлення помилок

У практичній розробці розрахункових модулів виникають наступні крайові сценарії:

1. **Задано надлишкове число хімічних реакцій (`R ≥ N`):**
   Якщо користувач помилково вказує кількість хімічних реакцій `R`, що перевищує або дорівнює кількості хімічних речовин `N`, чисельне значення `C = N - R - r` стає нульовим або від'ємним. У цьому випадку функція негайно перериває обчислення й повертає код `GIBBS_STATUS_NEGATIVE_COMPONENTS`. Солвер не повинен намагатися виконати віднімання на від'ємних компонентах.

2. **Спроба задати нонваріантний стан при фіксованому тиску і температурі:**
   Якщо для однокомпонентного середовища (`C = 1`) з трьома фазами (`P = 3`, потрійна точка) зафіксувати і тиск (`P = const`), і температуру (`T = const`), то формула дає `F = 1 - 3 + 2 - 1 - 1 = -1`. API поверне статус `GIBBS_STATUS_OVERCONSTRAINED_SYSTEM` та прапорець `is_physically_realizable = 0`. Прапорці `is_isobaric` та `is_isothermal` у структуру додані саме для того, щоб підсистема автоматично враховувала умови експерименту.

3. **Багатокомпонентні розплави з зовнішніми полями:**
   При моделюванні кристалізації металевих сплавів під дією ультразвукового або потужного магнітного поля, значення `external_fields_m` збільшується на 1. API збільшує кінцевий ступінь вільності `F`, дозволяючи додатково варіювати інтенсивність поля без порушення фазового складу розплаву.

### Специфікація JSON-схеми конфігурації

Для обміну даними між веб-сервісами, веб-інтерфейсами та інструментами командного рядка (CLI) специфіковано стандартний формат JSON.

#### Детальний опис полів JSON-документа:
- `system_name` (string, optional) — текстова назва або ідентифікатор термодинамічної системи;
- `species_count` (integer, required) — загальне число речовин `N` (мінімальне значення 1);
- `reactions_count` (integer, optional) — число незалежних хімічних реакцій `R` (за замовчуванням 0);
- `constraints_count` (integer, optional) — число додаткових обмежень `r` (за замовчуванням 0);
- `phases_count` (integer, required) — число рівноважних фаз `P` (мінімальне значення 1);
- `is_isobaric` (boolean, optional) — прапорець постійного тиску `P = const` (за замовчуванням false);
- `is_isothermal` (boolean, optional) — прапорець постійної температури `T = const` (за замовчуванням false);
- `external_fields_m` (integer, optional) — додаткові поля `m` (за замовчуванням 0).

#### JSON Schema (Draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GibbsPhaseSystemConfig",
  "description": "Схема конфігураційного файла фазового аналізу за правилом Гіббса",
  "type": "object",
  "properties": {
    "system_name": {
      "type": "string",
      "description": "Текстова назва системи"
    },
    "species_count": {
      "type": "integer",
      "minimum": 1,
      "description": "Кількість речовин N"
    },
    "reactions_count": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Кількість реакцій R"
    },
    "constraints_count": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Кількість обмежень r"
    },
    "phases_count": {
      "type": "integer",
      "minimum": 1,
      "description": "Кількість фаз P"
    },
    "is_isobaric": {
      "type": "boolean",
      "default": false,
      "description": "Фіксований тиск P=const"
    },
    "is_isothermal": {
      "type": "boolean",
      "default": false,
      "description": "Фіксована температура T=const"
    },
    "external_fields_m": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Кількість зовнішніх полів m"
    }
  },
  "required": ["species_count", "phases_count"]
}
```

Приклад валидного JSON-файла конфігурації для потрійної системи сплавів:

```json
{
  "system_name": "Потрійний алюмінієво-магнієво-кремнієвий сплав (Al-Mg-Si)",
  "species_count": 3,
  "reactions_count": 0,
  "constraints_count": 0,
  "phases_count": 4,
  "is_isobaric": true,
  "is_isothermal": false,
  "external_fields_m": 0
}
```
