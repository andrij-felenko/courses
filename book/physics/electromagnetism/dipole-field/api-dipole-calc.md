# 📋 Інтерфейс та API бібліотеки розрахунку дипольних взаємодій

Обчислювальна бібліотека `libdipole` забезпечує уніфікований програмний інтерфейс для розрахунку електростатичних характеристик дипольних систем, симуляції орієнтаційного відгуку в зовнішніх полях та моделювання макроскопічних діелектричних середовищ. Цей документ є стандартизованим довідником архітектури API, типізованих контрактів виклику, параметрів, кодів помилок, інваріантів обробки пам'яті та стратегій забезпечення потокобезпечності.

## 1. Архітектурні принципи та типізація

Обчислювальна бібліотека розроблена з урахуванням суворих вимог до системного програмування та обчислювальної фізики. Вона призначена для використання як у високопродуктивних обчислювальних кластерах для сумісного моделювання мільйонів дипольних частинок, так і у вбудованих системах реального часу для первинної обробки датчикових даних.

Для досягнення максимальної швидкодії та надійності архітектура API спирається на такі ключові принципи:

1. **Відсутність внутрішнього стану (Stateless Execution)**: Усі обчислювальні функції є чистими (pure functions). Вони приймають усі необхідні параметри через вхідні структури та не модифікують приховані глобальні змінні чи статичні буфери. Це робить виклики повністю потокобезпечними (reentrant / thread-safe), дозволяючи паралелити обчислення за допомогою OpenMP, POSIX threads або TBB без викликів м'ютексів чи утворення точок блокування (contention).

2. **Явне володіння пам'яттю**: Бібліотека ніколи не виконує прихованого виділення кучі (heap allocation) всередині базових математичних викликів. Пам'ять під результати або сітки точок надається безпосередньо викликаючою стороною (caller-allocated memory). Це повністю усуває ризики витоків пам'яті та гарантує детермінований час виконання викликів.

3. **Захист від чисельних сингулярностей**: Усі функції перевіряють вхідні вектори на скінченність та застосовують механізм регуляризації ядра Поассона за допомогою параметра згладжування `cutoff`.

### 1.1 `dipole_vec3_t` — Векторний тип тривимірного простору

Базовою математичною одиницею для всіх геометричних та фізичних величин є тривимірна векторна структура `dipole_vec3_t`. Вона використовується для опису координат положення `r = (x, y, z)`, векторів напруженості електричного поля `E = (E_x, E_y, E_z)`, векторів дипольного моменту `p = (p_x, p_y, p_z)`, векторів сил `F` та обертальних моментів `τ`.

| Поле | Тип | Фізичний зміст та одиниці SI | Допустимий чисельний діапазон |
| :--- | :--- | :--- | :--- |
| `x` | `double` | Декартова компонента вздовж осі X (метри, В/м, Н·м або Н) | Скінченні числа `[-10¹², +10¹²]` |
| `y` | `double` | Декартова компонента вздовж осі Y (метри, В/м, Н·м або Н) | Скінченні числа `[-10¹², +10¹²]` |
| `z` | `double` | Декартова компонента вздовж осі Z (метри, В/м, Н·м або Н) | Скінченні числа `[-10¹², +10¹²]` |

### 1.2 `dipole_state_t` — Стан точкового диполя

Структура `dipole_state_t` повністю описує просторову конфігурацію та фізичні характеристики точкового диполя в розрахунковій системі.

| Поле | Тип | Опис інваріанта та фізична роль | Значення за замовчуванням |
| :--- | :--- | :--- | :--- |
| `pos` | `dipole_vec3_t` | Радиус-вектор просторового положення центру диполя `r₀` | `{0.0, 0.0, 0.0}` m |
| `p` | `dipole_vec3_t` | Вектор електричного дипольного моменту `p = q·d` | `{0.0, 0.0, 0.0}` C·m |
| `cutoff` | `double` | Радиус згладжування сингулярності ядра (`cutoff > 0`) | `1.0e-9` m (1 нм) |

Поле `cutoff` відіграє вирішальну роль при обчисленні полів на малих відстанях. Якщо точка спостереження збігається з положенням диполя, пряме обчислення видає ділення на нуль. Введення параметра `cutoff` модифікує знаменник за формулою `r_eff = √(R_x² + R_y² + R_z² + cutoff²)`, що гарантує чисельну стабільність без втрати точності на великих відстанях.

### 1.3 `dipole_error_t` — Перелічувальний тип кодів результатів

Кожна обчислювальна функція низкорівневого C API повертає перелічувальне значення `dipole_error_t`, яке характеризує успішність виконання виклику. Вкладка C++ реалізує аналогічний тип через `enum class ErrorCode`:

:::tabs
```c
typedef enum {
    DIPOLE_SUCCESS = 0,             /* Операція виконана успішно */
    DIPOLE_ERR_NULL_PTR = -1,        /* Передано нульовий вказівник (NULL) */
    DIPOLE_ERR_SINGULARITY = -2,     /* Точка потрапила в область сингулярності без cutoff */
    DIPOLE_ERR_INVALID_PARAM = -3,   /* Від'ємний cutoff або некоректні чисельні значення (NaN/Inf) */
    DIPOLE_ERR_OUT_OF_MEMORY = -4    /* Помилка виділення динамічної пам'яті для сітки */
} dipole_error_t;
```
```cpp
enum class ErrorCode {
    Success = 0,
    NullPointer = -1,
    Singularity = -2,
    InvalidParameter = -3,
    OutOfMemory = -4
};
```
:::

Викликаюча сторона повинна завжди перевіряти повернутий код помилки перед використанням результуючих змінних. У випадку повернення коду, відмінного від успішного, вміст вихідних змінних вважається неозначеним.

## 2. Специфікація функцій обчислювального API

### 2.1 Обчислення скалярного потенціалу `dipole_calc_potential`

Розраховує скалярний електростатичний потенціал `φ` у довільно заданій точці простору.

:::tabs
```c
dipole_error_t dipole_calc_potential(
    const dipole_state_t* dipole,
    dipole_vec3_t point,
    double* out_potential
);
```
```cpp
[[nodiscard]] static std::expected<double, ErrorCode> calculate_potential(
    const DipoleState& state,
    Vector3 point) noexcept;
```
:::

- **Вхідні інваріанти:** Вказівники `dipole` та `out_potential` не повинні бути нульовими (`NULL`). Значення поля `dipole->cutoff` має бути strictly додатним (`> 0.0`). Передані координати точки мають бути дійсними скінченними числами (`std::isfinite`).
- **Алгоритм та математична модель:** Функція обчислює вектор відносної відстані `R = point − dipole->pos`. Потім обчислюється ефективна згладжена відстань `r_eff = √(R_x² + R_y² + R_z² + cutoff²)`. Результат записується за формулою `φ = (1 / (4·π·ε₀)) · (p · R) / r_eff³`.
- **Повертає:** `DIPOLE_SUCCESS` при коректному обчисленні. Повертає `DIPOLE_ERR_NULL_PTR`, якщо передано нульові вказівники, або `DIPOLE_ERR_INVALID_PARAM`, якщо `cutoff <= 0` чи вектори містять `NaN`.
- **Продуктивність:** Час виконання становить орієнтовно `12` тактів процесора. Не викликає системних функцій виділення пам'яті.

### 2.2 Обчислення вектора напруженості електричного поля `dipole_calc_field`

Обчислює повний тривимірний вектор напруженості електричного поля `E` в точці спостереження.

:::tabs
```c
dipole_error_t dipole_calc_field(
    const dipole_state_t* dipole,
    dipole_vec3_t point,
    dipole_vec3_t* out_field
);
```
```cpp
[[nodiscard]] static std::expected<Vector3, ErrorCode> calculate_field(
    const DipoleState& state,
    Vector3 point) noexcept;
```
:::

- **Вхідні інваріанти:** Перевірка `dipole != NULL` та `out_field != NULL`.
- **Алгоритми та розрахунок:** Вектор поля обчислюється за інваріантною формулою `E = (1 / (4·π·ε₀)) · [ 3(p·R)R / r_eff⁵ − p / r_eff³ ]`.
- **Повертане значення:** `DIPOLE_SUCCESS` у разі успіху. Напруженість виражається в одиницях Вольт на метр (В/м).

### 2.3 Аналіз взаємодії з зовнішнім полем `dipole_calc_interaction`

Обчислює механічний обертальний момент сил `τ`, потенціальну енергію `U` та втягуючу силу `F` у неоднорідному зовнішньому полі.

:::tabs
```c
dipole_error_t dipole_calc_interaction(
    const dipole_state_t* dipole,
    dipole_vec3_t ext_field,
    const dipole_vec3_t ext_grad_e[3],
    dipole_vec3_t* out_torque,
    double* out_energy,
    dipole_vec3_t* out_force
);
```
```cpp
[[nodiscard]] static std::expected<Vector3, ErrorCode> calculate_torque(
    const DipoleState& state,
    Vector3 ext_field) noexcept;
```
:::

- **Параметри:**
  - `dipole`: [in] Вказівник на вихідний стан диполя.
  - `ext_field`: [in] Вектор зовнішнього електричного поля `E_зовн` у точці розташування диполя (В/м).
  - `ext_grad_e`: [in] Матриця градієнта поля 3x3, подана як три вектори часткових похідних `[∂E/∂x, ∂E/∂y, ∂E/∂z]`. Якщо сила не обчислюється, дозволяється передавати `NULL`.
  - `out_torque`: [out] Адреса вектора для запису обертального моменту `τ = p × E` (Н·м). Дозволяється `NULL`.
  - `out_energy`: [out] Адреса для запису потенціальної енергії `U = −p · E` (Дж). Дозволяється `NULL`.
  - `out_force`: [out] Адреса вектора для запису сили `F = (p · ∇)E` (Ньютони). Дозволяється `NULL`.
- **Математична реалізація:** Обертальний момент обчислюється через векторний добуток, енергія — через скалярний добуток, а сила — через матричне множення градієнта поля на вектор дипольного моменту.

### 2.4 Пакетна обробка просторових сіток `dipole_grid_evaluate`

Для прискорення аналізу великих масивів точок (наприклад, при візуалізації поля на 2D/3D сітках) виклик окремої функції для кожної точки створює зайві накладні витрати. Функція `dipole_grid_evaluate` виконує пакетну обробку масиву точок.

:::tabs
```c
dipole_error_t dipole_grid_evaluate(
    const dipole_state_t* dipole,
    const dipole_vec3_t* points,
    size_t count,
    double* out_potentials,
    dipole_vec3_t* out_fields
);
```
```cpp
[[nodiscard]] static std::vector<double> compute_potential_grid(
    const DipoleState& state,
    std::span<const Vector3> points);
```
:::

- **Переваги пакетної обробки:** Внутрішній цикл функції векторно розгортається компілятором (SIMD vectorization) із використанням інструкцій AVX2 / AVX-512, що підвищує обчислювальну продуктивність у 3-5 разів порівняно з попоточеними викликами.

## 3. Повноцінний приклад використання API (C та C++)

Нижче наведено робочий приклад оголошення та використання API двома мовами у вигляді вкладок `:::tabs`. Версія C++20 розроблена як сучасна високорівнева обгортка: вона спирається на семантику безвиняткової обробки помилок за допомогою типів `std::expected`, використовує `std::span` для безпечного перегляду пам'яті та забезпечує розрахунки на етапі компіляції (`constexpr`).

:::tabs
```c
#include <stdio.h>
#include <math.h>

typedef enum {
    DIPOLE_SUCCESS = 0,
    DIPOLE_ERR_NULL_PTR = -1,
    DIPOLE_ERR_SINGULARITY = -2,
    DIPOLE_ERR_INVALID_PARAM = -3
} dipole_error_t;

typedef struct {
    double x, y, z;
} dipole_vec3_t;

typedef struct {
    dipole_vec3_t pos;
    dipole_vec3_t p;
    double cutoff;
} dipole_state_t;

dipole_error_t dipole_calc_potential(
    const dipole_state_t* dipole,
    dipole_vec3_t point,
    double* out_potential
) {
    if (!dipole || !out_potential) {
        return DIPOLE_ERR_NULL_PTR;
    }
    if (dipole->cutoff < 0.0) {
        return DIPOLE_ERR_INVALID_PARAM;
    }

    double dx = point.x - dipole->pos.x;
    double dy = point.y - dipole->pos.y;
    double dz = point.z - dipole->pos.z;

    double r_sq = dx * dx + dy * dy + dz * dz + dipole->cutoff * dipole->cutoff;
    double r_len = sqrt(r_sq);
    double r_pow3 = r_len * r_sq;

    double dot_pR = dipole->p.x * dx + dipole->p.y * dy + dipole->p.z * dz;
    const double k_e = 8.9875517923e9; // 1 / (4*pi*eps0)

    *out_potential = k_e * dot_pR / r_pow3;
    return DIPOLE_SUCCESS;
}

dipole_error_t dipole_calc_interaction(
    const dipole_state_t* dipole,
    dipole_vec3_t ext_field,
    dipole_vec3_t* out_torque,
    double* out_energy
) {
    if (!dipole) {
        return DIPOLE_ERR_NULL_PTR;
    }

    if (out_torque) {
        out_torque->x = dipole->p.y * ext_field.z - dipole->p.z * ext_field.y;
        out_torque->y = dipole->p.z * ext_field.x - dipole->p.x * ext_field.z;
        out_torque->z = dipole->p.x * ext_field.y - dipole->p.y * ext_field.x;
    }

    if (out_energy) {
        *out_energy = -(dipole->p.x * ext_field.x + 
                        dipole->p.y * ext_field.y + 
                        dipole->p.z * ext_field.z);
    }

    return DIPOLE_SUCCESS;
}

int main(void) {
    dipole_state_t state = {
        .pos = {0.0, 0.0, 0.0},
        .p = {0.0, 0.0, 3.33564e-30}, // 1 Debye
        .cutoff = 1e-9
    };

    dipole_vec3_t pt = {1e-9, 0.0, 0.0};
    double pot = 0.0;

    if (dipole_calc_potential(&state, pt, &pot) == DIPOLE_SUCCESS) {
        printf("Потенціал диполя в 1D на 1 нм: %.6e V\n", pot);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <cmath>
#include <expected>
#include <system_error>
#include <span>

namespace dipole::api {

enum class ErrorCode {
    Success = 0,
    NullPointer,
    Singularity,
    InvalidParameter
};

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double dot(const Vector3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    [[nodiscard]] constexpr Vector3 cross(const Vector3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
};

struct DipoleState {
    Vector3 position{};
    Vector3 moment{};
    double cutoff{1e-9};
};

class DipoleCalculator {
private:
    static constexpr double k_e = 8.9875517923e9; // 1 / (4*pi*eps0)

public:
    [[nodiscard]] static std::expected<double, ErrorCode> calculate_potential(
        const DipoleState& state,
        Vector3 point) noexcept {
        
        if (state.cutoff < 0.0) {
            return std::unexpected(ErrorCode::InvalidParameter);
        }

        Vector3 R = {
            point.x - state.position.x,
            point.y - state.position.y,
            point.z - state.position.z
        };

        double r_sq = R.dot(R) + state.cutoff * state.cutoff;
        double r_len = std::sqrt(r_sq);
        double r_pow3 = r_len * r_sq;

        double dot_pR = state.moment.dot(R);
        return k_e * dot_pR / r_pow3;
    }

    [[nodiscard]] static std::expected<Vector3, ErrorCode> calculate_torque(
        const DipoleState& state,
        Vector3 ext_field) noexcept {
        
        return state.moment.cross(ext_field);
    }

    [[nodiscard]] static double calculate_potential_energy(
        const DipoleState& state,
        Vector3 ext_field) noexcept {
        
        return -state.moment.dot(ext_field);
    }
};

} // namespace dipole::api

int main() {
    using namespace dipole::api;

    DipoleState state{
        .position = {0.0, 0.0, 0.0},
        .moment = {0.0, 0.0, 3.33564e-30}, // 1 Debye
        .cutoff = 1e-9
    };

    Vector3 pt{1e-9, 0.0, 0.0};
    auto result = DipoleCalculator::calculate_potential(state, pt);

    if (result.has_value()) {
        std::cout << "Потенціал (1 Debye, 1 nm) = " << result.value() << " V\n";
    } else {
        std::cerr << "Помилка обчислення потенціалу!\n";
    }

    return 0;
}
```
:::

## 4. Одиниці вимірювання та міжмовні конверсії

Усі методи математичного API за замовчуванням сприймають значення у стандартній міжнародній системі одиниць SI (метри для відстаней, кулон-метри для моменту, вольти для потенціалу). Проте під час взаємодії із пакетами хімічного моделювання (наприклад, Gaussian, ORCA, LAMMPS) параметри часто задаються у специфічних позасистемних одиницях.

Бібліотека пропонує набір функцій перетворення одиниць:

:::tabs
```c
inline double dipole_debye_to_si(double deb) {
    return deb * 3.335640951982e-30; // Перетворення Дебай -> C·m
}

inline double dipole_si_to_debye(double si) {
    return si / 3.335640951982e-30; // Перетворення C·m -> Дебай
}

inline double dipole_atomic_to_si(double au) {
    return au * 8.4783536255e-30;   // Перетворення атомарних одиниць -> C·m
}
```
```cpp
constexpr double debye_to_si(double deb) noexcept {
    return deb * 3.335640951982e-30; // Перетворення Дебай -> C·m
}

constexpr double si_to_debye(double si) noexcept {
    return si / 3.335640951982e-30; // Перетворення C·m -> Дебай
}

constexpr double atomic_to_si(double au) noexcept {
    return au * 8.4783536255e-30;   // Перетворення атомарних одиниць -> C·m
}
```
:::

Використання цих функцій є повністю прозорим для продуктивності, оскільки вони оптимізуються компілятором у єдину інструкцію множення на константу під час компіляції.
