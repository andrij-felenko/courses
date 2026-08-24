# 📋 Інтерфейс бібліотеки симуляції та аналізу броунівського руху

У цій вставці наведено повну специфікацію програмного інтерфейсу (API) бібліотеки `libbrownian` — обчислювального інструменту для чисельного моделювання стохастичних траєкторій колоїдних частинок, розрахунку часового та ансамблевого середнього квадрата зсуву (MSD), вимірювання коефіцієнтів дифузії та автоматизованої діагностики режимів аномальної дифузії у складних середовищах.

Програмний інтерфейс розроблено за принципами сумісності та продуктивності: він надає низькорівневий C API для гнучкої інтеграції в обчислювальні системи, а також об'єктно-орієнтовану C++ обгортку з підтримкою RAII, безпеки типів та винятків.

### 1. Специфікація фізичних одиниць, координатних систем та нормалізації

Одна з найпоширеніших помилок при чисельному симулюванні фізичних систем пов'язана з невідповідністю одиниць вимірювання або неправильним вибором масштабування. Для уникнення плутанини всі виклики API бібліотеки `libbrownian` строго оперують величини у міжнародній системі СІ (SI).

| Параметр | Символ в API | Одиниці СІ | Опис, фізичний зміст та стандартні значення |
| :--- | :--- | :--- | :--- |
| Термодинамічна температура | `temperature` | `К` (Кельвіни) | Абсолютна температура термостату. Стандартне кімнатне значення дорівнює `300.0` К. |
| Динамічна в'язкість | `viscosity` | `Па·с` | Динамічна в'язкість середовища. Для дистильованої води при 20 °C складає `1.002e-3` Па·с. |
| Гідродинамічний радіус | `particle_radius` | `м` (метри) | Еквівалентний радіус сфери за Стоксом. Для типових колоїдів становить від `1.0e-8` м до `1.0e-5` м. |
| Маса частинки | `particle_mass` | `кг` (кілограми) | Ефективна маса частинки (з урахуванням плавучості). Для сфери 1 мкм у воді складає `~4.189e-15` кг. |
| Часовий крок інтегрування | `dt` | `с` (секунди) | Крок дискретизації за часом. Повинен бути суттєво меншим за час релаксації `τ_p = m / γ`. |
| Коефіцієнт дифузії | `diffusion_coeff` | `м²/с` | Розрахункова величина. Для кульки 1 мкм у воді становить приблизно `2.14e-13` м²/с. |

Для розрахунку коефіцієнтів тертя бібліотека використовує класичну формулу Стокса `γ = 6 · π · η · a`, де `η` — динамічна в'язкість, а `a` — радіус частинки. Якщо частинка перебуває поблизу плоского субстрату чи стінки капіляра, макроскопічна в'язкість корегується за поправкою Факсена.

---

### 2. Детальний опис структур даних та типів

#### Режими симуляції (`BrownianSimMode` / `brownian::SimMode`)

Енумераційний тип визначає фізичну модель, яка використовується обчислювальним ядром для генерації кожного наступного кроку траєкторії:

:::tabs
```c
typedef enum {
    BROWNIAN_MODE_EXACT_LANGEVIN = 0, /* Повне рівняння Ланжевена: інерція та білий шум */
    BROWNIAN_MODE_OVERDAMPED     = 1, /* Перевизначений режим (без інерції) */
    BROWNIAN_MODE_ROTATIONAL     = 2, /* Обертальний броунівський рух */
    BROWNIAN_MODE_ACTIVE_SWIMMER = 3  /* Активний броунівський рух */
} BrownianSimMode;
```
```cpp
namespace brownian {

enum class SimMode {
    ExactLangevin = 0, // Повне рівняння Ланжевена
    Overdamped     = 1, // Перевизначений режим без інерції
    Rotational     = 2, // Обертальна дифузія
    ActiveSwimmer  = 3  // Активний мікроплавець
};

} // namespace brownian
```
:::

У режимі `BROWNIAN_MODE_EXACT_LANGEVIN` бібліотека повністю інтегрує стохастичну систему для швидкості та координат, що дає змогу бачити балістичний режим на коротких часах. У режимі `BROWNIAN_MODE_OVERDAMPED` обчислення прискорюються в кілька разів, оскільки крок розраховується безпосередньо для координат, що ідеально підходить для моделювання повільної макроскопічної дифузії.

#### Конфігураційна структура (`BrownianConfig` / `brownian::Config`)

Конфігураційні типи задають параметри системи для C та C++ інтерфейсів:

:::tabs
```c
typedef struct {
    double temperature;        /* Абсолютна температура середовища, К (> 0) */
    double viscosity;          /* Динамічна в'язкість рідини, Па·с (> 0) */
    double particle_radius;    /* Гідродинамічний радіус частинки, м (> 0) */
    double particle_mass;      /* Маса частинки, кг (> 0) */
    double active_velocity;    /* Швидкість власного руху для активних частинок, м/с */
    double dt;                 /* Часовий крок інтегрування, с (> 0) */
    size_t trajectory_steps;   /* Загальна кількість кроків у кожній траєкторії */
    size_t ensemble_size;      /* Кількість частинок в ансамблі */
    unsigned int random_seed;  /* Базове зерно генератора випадкових чисел */
    BrownianSimMode mode;      /* Фізичний режим моделювання */
    int dimension;             /* Просторова розмірність: 1, 2 або 3 */
} BrownianConfig;
```
```cpp
namespace brownian {

struct Config {
    double temperature{300.0};       // К
    double viscosity{1.002e-3};      // Па·с
    double particle_radius{1.0e-6};  // м
    double particle_mass{4.189e-15}; // кг
    double active_velocity{0.0};     // м/с
    double dt{1.0e-7};               // с
    std::size_t trajectory_steps{1000};
    std::size_t ensemble_size{500};
    unsigned int random_seed{0};
    SimMode mode{SimMode::ExactLangevin};
    int dimension{2};

    [[nodiscard]] double calculate_gamma() const noexcept {
        constexpr double pi = 3.14159265358979323846;
        return 6.0 * pi * viscosity * particle_radius;
    }

    [[nodiscard]] double calculate_theoretical_D() const noexcept {
        constexpr double kB = 1.380649e-23;
        return (kB * temperature) / calculate_gamma();
    }
};

} // namespace brownian
```
:::

Перед початком обчислень симулятор виконує перевірку полів конфігурації. Якщо передано від'ємне значення температури, нульовий крок по часу або невизначену розмірність, симуляція переривається з відповідним кодом помилки або винятком `std::invalid_argument`.

#### Структура стану частинки (`BrownianState` / `brownian::State`)

Векторний стан частинки містить миттєві просторові координати, компоненти швидкості та часову мітку:

:::tabs
```c
typedef struct {
    double position[3];  /* Просторові координати [x, y, z] у метрах */
    double velocity[3];  /* Компоненти швидкості [vx, vy, vz] у м/с */
    double timestamp;    /* Фізичний час від початку симуляції, секунди */
} BrownianState;
```
```cpp
namespace brownian {

struct State {
    std::array<double, 3> position{0.0, 0.0, 0.0};
    std::array<double, 3> velocity{0.0, 0.0, 0.0};
    double timestamp{0.0};
};

} // namespace brownian
```
:::

#### Структура аналізу MSD (`BrownianMsdResult` / `brownian::MsdAnalysis`)

Після виконання симуляції або завантаження експериментальних траєкторій модуль статистичного аналізу формує структуру результатів:

:::tabs
```c
typedef struct {
    double *time_lags;          /* Масив часових затримок τ, с */
    double *msd_values;         /* Обчислені значення MSD <Δr²(τ)>, м² */
    double *std_errors;         /* Стандартні помилки MSD */
    size_t num_lags;            /* Кількість порахованих часових затримок */
    double estimated_D;         /* Оцінений коефіцієнт дифузії D, м²/с */
    double r_squared;           /* Якість лінійної апроксимації (R²) */
    double anomalous_exponent;  /* Показник аномальності α (<r²> ~ τ^α) */
    int status_code;            /* Код стану або помилки обчислень */
} BrownianMsdResult;
```
```cpp
namespace brownian {

struct MsdAnalysis {
    std::vector<double> time_lags;
    std::vector<double> msd_values;
    std::vector<double> std_errors;
    double estimated_D{0.0};
    double r_squared{0.0};
    double anomalous_exponent{1.0};
};

} // namespace brownian
```
:::

Значення показника аномальності `anomalous_exponent` дозволяє автоматично класифікувати тип руху: якщо `α ≈ 1.0`, спостерігається нормальна броунівська дифузія; якщо `α < 0.9`, має місце субдифузія (повільний рух у пористому середовищі або гель-матриці); якщо `α > 1.1`, спостерігається супердифузія або активний спрямований транспорт.

---

### 3. Реєстр кодів повернення та діагностика помилок (`BrownianStatus`)

Усі функції низькорівневого C API повертають цілочисельний статус. Нульовий код означає успішне виконання, від'ємні коди вказують на конкретну критичну помилку:

| Код | Символічна назва в C API | Причина виникнення та інструкції з усунення |
| :--- | :--- | :--- |
| `0` | `BROWNIAN_SUCCESS` | Успішне виконання операції. |
| `-1` | `BROWNIAN_ERR_INVALID_PARAM` | Один із параметрів виходить за допустимий фізичний діапазон. Перевірте значення `dt`, `temp`, `radius`. |
| `-2` | `BROWNIAN_ERR_NO_MEMORY` | Не вдалося виділити буфер динамічної пам'яті. Зменшіть розмір ансамблю або кількість кроків. |
| `-3` | `BROWNIAN_ERR_UNSTABLE_DT` | Часовий крок `dt` перевищує умову стійкості Ейлера (`dt > 2 m / γ`). Зменшіть `dt` або змініть режим на `Overdamped`. |
| `-4` | `BROWNIAN_ERR_NULL_POINTER` | Передано нульовий вказівник `NULL` у якості аргументу функції. |
| `-5` | `BROWNIAN_ERR_DIM_MISMATCH` | Спроба виконати аналіз розмірності, яка не відповідає даним траєкторії (наприклад, 3D аналіз 2D даних). |

---

### 4. Заголовочні файли та декларації заголовочних контрактів C і C++

Нижче наведено повні контракти публічних інтерфейсів `brownian_sim.h` та `brownian_sim.hpp`:

:::tabs
```c
#ifndef BROWNIAN_SIM_H
#define BROWNIAN_SIM_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Заповнює структуру конфігурації стандартними фізичними параметрами (вода, 300K, 1 мкм).
 * @param config Вказівник на структуру конфігурації.
 * @return BROWNIAN_SUCCESS або BROWNIAN_ERR_NULL_POINTER.
 */
int brownian_config_default(BrownianConfig *config);

/**
 * @brief Обчислює теоретичний коефіцієнт дифузії Стокса—Ейнштейна.
 * @param temperature_k Температура термостату, К.
 * @param viscosity_pas Динамічна в'язкість рідини, Па·с.
 * @param radius_m Гідродинамічний радіус частинки, м.
 * @param out_diff_coeff Вказівник на змінну для запису результату (м²/с).
 * @return BROWNIAN_SUCCESS або BROWNIAN_ERR_INVALID_PARAM.
 */
int brownian_calculate_theoretical_D(double temperature_k,
                                     double viscosity_pas,
                                     double radius_m,
                                     double *out_diff_coeff);

/**
 * @brief Запускає симуляцію ансамблю броунівських частинок.
 * @param config Вказівник на параметри конфігурації.
 * @param out_states Виділений буфер для зберігання станів.
 * @return BROWNIAN_SUCCESS або відповідний код помилки.
 */
int brownian_simulate_ensemble(const BrownianConfig *config,
                               BrownianState *out_states);

/**
 * @brief Обчислює ансамблевий MSD та виконує лінійний аналіз дифузії.
 * @param config Параметри симуляції.
 * @param states Буфер згенерованих станів.
 * @param out_result Структура результату.
 * @return BROWNIAN_SUCCESS або код помилки.
 */
int brownian_analyze_msd(const BrownianConfig *config,
                         const BrownianState *states,
                         BrownianMsdResult *out_result);

/**
 * @brief Звільняє динамічну пам'ять, виділену всередині структури BrownianMsdResult.
 * @param result Вказівник на структуру результату.
 */
void brownian_free_msd_result(BrownianMsdResult *result);

#ifdef __cplusplus
}
#endif

#endif /* BROWNIAN_SIM_H */
```
```cpp
#ifndef BROWNIAN_SIM_HPP
#define BROWNIAN_SIM_HPP

#include <vector>
#include <array>
#include <memory>
#include <optional>
#include <cstddef>
#include <stdexcept>

namespace brownian {

class Simulator {
public:
    explicit Simulator(Config config) : config_(std::move(config)) {}

    ~Simulator() = default;

    Simulator(const Simulator&) = delete;
    Simulator& operator=(const Simulator&) = delete;
    Simulator(Simulator&&) noexcept = default;
    Simulator& operator=(Simulator&&) noexcept = default;

    [[nodiscard]] std::vector<std::vector<State>> run_ensemble();
    [[nodiscard]] MsdAnalysis analyze(const std::vector<std::vector<State>>& trajectories) const;

    [[nodiscard]] const Config& config() const noexcept { return config_; }

private:
    Config config_;
};

} // namespace brownian

#endif // BROWNIAN_SIM_HPP
```
:::

---

### 5. Стрімінговий накопичувач та граничні умови

#### Типи граничних умов (`BrownianBoundaryType` / `brownian::BoundaryType`)

Для моделювання частинок у обмежених мікрофлюїдних каналах або мембранних порах API надає вибір геометричних обмежень:

:::tabs
```c
typedef enum {
    BROWNIAN_BOUND_UNBOUNDED = 0, /* Безмежний простір (без меж) */
    BROWNIAN_BOUND_REFLECT   = 1, /* Віддзеркалювальна тверда стінка */
    BROWNIAN_BOUND_PERIODIC  = 2, /* Періодичні граничні умови */
    BROWNIAN_BOUND_ABSORB    = 3  /* Поглинаюча поверхня */
} BrownianBoundaryType;
```
```cpp
namespace brownian {

enum class BoundaryType {
    Unbounded = 0,
    Reflect   = 1,
    Periodic  = 2,
    Absorb    = 3
};

} // namespace brownian
```
:::

#### Стрімінговий накопичувач пам'яті (`BrownianStreamAccumulator` / `brownian::StreamAccumulator`)

Коли кількість частинок в ансамблі вимірюється мільйонами або довжина траєкторії сягає мільярдів кроків, збереження всіх станів у RAM є неможливим. Для цього призначено стрімінговий накопичувач, який оновлює значення MSD безпосередньо «на льоту»:

:::tabs
```c
typedef struct {
    double *msd_sum;      /* Масив накопичених сум квадрата зсуву */
    size_t *sample_count; /* Масив кількості відліків */
    size_t num_lags;      /* Кількість проміжків часу */
} BrownianStreamAccumulator;

int brownian_stream_init(BrownianStreamAccumulator *acc, size_t num_lags);
int brownian_stream_push_step(BrownianStreamAccumulator *acc, size_t lag, double dx, double dy, double dz);
int brownian_stream_finalize(const BrownianStreamAccumulator *acc, BrownianMsdResult *out_result);
void brownian_stream_free(BrownianStreamAccumulator *acc);
```
```cpp
namespace brownian {

class StreamAccumulator {
public:
    explicit StreamAccumulator(std::size_t num_lags);
    ~StreamAccumulator() = default;

    void push_step(std::size_t lag, double dx, double dy, double dz = 0.0);
    [[nodiscard]] MsdAnalysis finalize() const;

private:
    std::vector<double> msd_sum_;
    std::vector<std::size_t> sample_count_;
};

} // namespace brownian
```
:::

#### Експорт даних та серіалізація у CSV / JSON

Для подальшої візуалізації у Python (Matplotlib, SciPy) або Gnuplot бібліотека містить допоміжні функції серіалізації:

:::tabs
```c
int brownian_export_csv(const char *filename, const BrownianState *states, size_t count);
int brownian_export_msd_json(const char *filename, const BrownianMsdResult *result);
```
```cpp
namespace brownian {

void export_csv(const std::string& filename, const std::vector<State>& states);
void export_msd_json(const std::string& filename, const MsdAnalysis& result);

} // namespace brownian
```
:::

---

### 6. Гарантії безпеки винятків, управління пам'яттю та сумісність

1. **Багатопотокова паралелізація:** оскільки траєкторії різних частинок в ансамблі є повністю незалежними, обчислення можна паралелити по частинках без жодних блокувань (lock-free). Для кожного потоку слід створювати власний екземпляр генератора випадкових чисел з унікальним зерном (`seed`), щоб уникнути міжпотокової кореляції та фальшивого змагання кешу (false sharing).
2. **Оптимізація пам'яті та кешу:** збереження повного масиву станів для великого ансамблю (скажімо, 10 000 частинок по 100 000 кроків) вимагає понад 4.8 ГБ оперативної пам'яті. У таких випадках рекомендовано використовувати стрімінговий режим `StreamAccumulator`, де суми для MSD накопичуються безпосередньо під час інтегрування krok-за-кроком, що знижує споживання RAM до кількох кілобайт.
3. **Обробка винятків та стабільність:** у C++ реалізації класу `Simulator` методи гарантують строгу безпеку винятків (*strong exception guarantee*). У разі виникнення помилки виділення пам'яті `std::bad_alloc` або передачі від'ємного часового кроку стан об'єкта залишається незмінним, а системні ресурси звільняються автоматично завдяки смарт-вказівникам `std::unique_ptr`.
4. **Правила володіння пам'яттю у C API:** масиви `time_lags`, `msd_values` та `std_errors` у структурі `BrownianMsdResult` виділяються бібліотекою динамічно через `calloc`. Клієнтський код зобов'язаний звільнити цю пам'ять шляхом єдиного виклику `brownian_free_msd_result()`. Повторне звільнення або ручний виклик `free()` для окремих полів структури є забороненим і призведе до невизначеної поведінки (*undefined behavior*).
5. **Життєвий цикл системних ресурсів та потокова безпека:** об'єкти конфігурації `BrownianConfig` є незмінними (*immutable*) під час розрахунку. Це дає змогу безпечно читати конфігурацію з багатьох обчислювальних потоків без використання синхранізаційних примітивів (мутексів чи спінлоків). Стрімінгові накопичувачі `BrownianStreamAccumulator` вимагають монопольного володіння в межах одного потоку; при використанні спільної пам'яті між потоками додавання нових відліків має захищатися атомарними операціями `std::atomic` або локальними накопичувачами з подальшим підсумковим об'єднанням (*reduction*).

Приклади реалізації обчислювальних алгоритмів наведено у вставці [Симуляція броунівського руху](topic:physics/brownian-motion/proj-brownian-simulation.md).

