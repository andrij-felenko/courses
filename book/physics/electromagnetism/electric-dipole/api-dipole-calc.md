# 📋 Інтерфейс обчислення дипольних взаємодій та полів

Цей довідковий документ визначає публічний контракт, структури даних, фізичні інваріанти та детальну специфікацію функцій програмного інтерфейсу (API) для обчислення електростатичних полів, потенціалів, обертальних моментів та сил взаємодії електричних диполів у класичній електродинаміці.

Інтерфейс розроблено для використання у високопродуктивних обчислювальних модулях фізичного моделювання, пакетах розрахунку молекулярної динаміки, САПР антенних систем та моделювання мікрофлюїдних чипів (діелектрофоретичного сортування біооб'єктів).

## 1. Архітектурні принципи та структури даних

Всі обчислення в даному інтерфейсі виконуються строго у Міжнародній системі одиниць SI з використанням чисел подвійної точності (`double`). Для забезпечення високої швидкодії та сумісності з C/C++ бібліотеками всі векторні структури вирівняні за межею 64 біт.

Обчислювальне ядро є повністю потокобезпечним (`thread-safe`) та не містить внутрішнього статичного стану чи прихованих глобальних змінних. Будь-які два треди можуть паралельно викликати розрахункові функції для різних або спільних об'єктів диполів без додаткового блокування мутексами.

### 1.1. Тривимірний вектор (`dipole_vec3_t` / `DipoleVec3`)
Структура є базовим математичним примітивом для представлення координат точок у просторі, векторів дипольних моментів, напруженості електричного поля та поступальних сил.

:::tabs
```c
/* Тривимірний вектор дійсної точності у C */
typedef struct {
    double x; /* Компонента по осі X [метри, В/м, Кл·м або Н] */
    double y; /* Компонента по осі Y */
    double z; /* Компонента по осі Z */
} dipole_vec3_t;
```
```cpp
// Тривимірний вектор із константними операторами у C++20
struct DipoleVec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr DipoleVec3 operator+(const DipoleVec3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr DipoleVec3 operator-(const DipoleVec3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr DipoleVec3 operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};
```
:::

### 1.2. Об'єкт точкового диполя (`electric_dipole_t` / `ElectricDipoleData`)
Структура повністю описує фізичний стан точкового диполя у просторі. Вона містить координати його центру `position`, векторний дипольний момент `moment` у системі SI (`C·m`) та допоміжне поле `moment_debye` для збереження дипольного моменту у позасистемних одиницях дебая.

:::tabs
```c
/* Структура точкового електричного диполя у просторі (C) */
typedef struct {
    dipole_vec3_t position; /* Координати центру диполя r_0 [метри, м] */
    dipole_vec3_t moment;   /* Вектор дипольного моменту p [кулон-метри, C·m] */
    double moment_debye;    /* Модуль дипольного моменту у дебаях [D] */
} electric_dipole_t;
```
```cpp
// Структура точкового електричного диполя (C++)
struct ElectricDipoleData {
    DipoleVec3 position;      // Координати центру диполя [м]
    DipoleVec3 moment;        // Вектор дипольного моменту [C·m]
    double moment_debye{0.0}; // Дипольний момент у дебаях [D]
};
```
:::

### 1.3. Контейнер результатів розрахунку поля (`dipole_field_result_t` / `DipoleFieldResult`)
Структура зберігає значення електростатичного потенціалу `potential` (у вольтах) та вектора напруженості `E_field` (у вольтах на метр) в обраній точці спостереження. Поле `is_singular` є прапорцем, який сигналізує про вихід точки спостереження у зону сингулярності (ближче за заданий радіус відсічки `min_r_cutoff`).

:::tabs
```c
/* Результат обчислення поля та потенціалу у точці спостереження (C) */
typedef struct {
    double potential;        /* Електростатичний потенціал Phi [вольти, В] */
    dipole_vec3_t E_field;   /* Вектор напруженості електричного поля E [В/м] */
    double E_magnitude;      /* Модуль напруженості |E| [В/м] */
    int is_singular;         /* Прапорець сингулярності (1, якщо r < r_min) */
} dipole_field_result_t;
```
```cpp
// Результат обчислення поля та потенціалу у точці спостереження (C++)
struct DipoleFieldResult {
    double potential{0.0};
    DipoleVec3 E_field;
    double E_magnitude{0.0};
    bool is_singular{false};
};
```
:::

### 1.4. Контейнер сил та моментів (`dipole_dynamics_t` / `DipoleDynamicsResult`)
Структура повертає повний набір силових характеристик диполя у зовнішньому електричному полі: обертальний момент `torque`, поступальну силу `force` та потенціальну енергію взаємодії `potential_energy`.

:::tabs
```c
/* Силові та обертальні характеристики диполя у зовнішньому полі (C) */
typedef struct {
    dipole_vec3_t torque;      /* Обертальний момент tau = p x E [Н·м] */
    dipole_vec3_t force;       /* Поступальна сила F = (p · grad)E [ньютони, Н] */
    double potential_energy;   /* Потенціальна енергія U = -p · E [джоулі, Дж] */
} dipole_dynamics_t;
```
```cpp
// Силові та обертальні характеристики диполя у зовнішньому полі (C++)
struct DipoleDynamicsResult {
    DipoleVec3 torque;       // Обертальний момент tau = p x E [Н·м]
    DipoleVec3 force;        // Поступальна сила F = (p · grad)E [Н]
    double potential_energy{0.0}; // Потенціальна енергія [Дж]
};
```
:::

## 2. Коефіцієнти перерахунку та фізичні інваріанти

Нижче подано таблицю фундаментальних фізичних констант, співвідношень та коефіцієнтів конвертації, що застосовуються в обчислювальному ядрі бібліотеки.

| Фізична величина | Одиниця SI | Позасистемна одиниця | Коефіцієнт перерахунку в SI |
| :--- | :--- | :--- | :--- |
| Дипольний момент `p` | `C·m` (Кулон-метр) | `D` (Дебай) | `1 D = 3.33564095 · 10⁻³⁰ C·m` |
| Електрична стала `ε₀` | `Ф/м` (Фарад/метр) | — | `8.8541878128 · 10⁻¹² Ф/м` |
| Електростатична стала `k_e` | `Н·м²/Кл²` | — | `1 / (4·π·ε₀) = 8.9875517923 · 10⁹` |
| Напруженість поля `E` | `В/м` (Вольт/метр) | `CGS` (СГСЕ) | `1 CGS_E = 2.99792458 · 10⁴ В/м` |
| Потенціальна енергія `U` | `Дж` (Джоуль) | `eV` (Електрон-вольт) | `1 eV = 1.602176634 · 10⁻¹⁹ Дж` |

При виконанні обчислень у середовищі з відносною діелектричною проникністю `ε_r` (наприклад, у рідкій воді `ε_r ≈ 80` або спирті `ε_r ≈ 25`) електростатичний коефіцієнт `k_e` модифікується як `k_e' = k_e / ε_r`. Це зменшує модуль напруженості поля та потенціалу у `ε_r` разів.

## 3. Специфікація функцій публічного API

У цьому розділі наведено детальний опис контрактів виконання, параметрів, вхідних і вихідних умов та математичних гарантій функцій API.

### 3.1. Перерахунок дипольного моменту (`dipole_debye_to_si`)
Функція здійснює точний конверсійний перерахунок модуля дипольного моменту з позасистемних одиниць дебая (`D`) у кулон-метри SI (`C·m`).

:::tabs
```c
/**
 * @brief Перераховує дипольний момент з дебаїв у C·m.
 * @param debye Значення моменту у дебаях [D].
 * @return Значення у кулон-метрах [C·m].
 */
double dipole_debye_to_si(double debye);
```
```cpp
// Конвертація з дебаїв у C·m у C++
constexpr double debye_to_si(double debye) noexcept {
    return debye * 3.33564095e-30;
}
```
:::

- **Параметри:** `debye` — дійсне число подвійної точності, що відповідає дипольному моменту в дебаях (може бути нульовим або додатним).
- **Повертане значення:** дійсне число у кулон-метрах `C·m`.
- **Крайові умови та валідація:** якщо `debye < 0`, функція повертає `0.0` і встановлює код помилки у глобальній змінній `errno = EINVAL`.

### 3.2. Розрахунок потенціалу та поля одиночного диполя (`dipole_calc_field`)
Обчислює вектор напруженості `E` та потенціал `Φ`, створені точковим диполем у довільній точці простору.

:::tabs
```c
/**
 * @brief Обчислює потенціал та поле точкового диполя.
 * @param dipole Вказівник на структуру точкового диполя.
 * @param obs_point Координати точки спостереження [м].
 * @param min_r_cutoff Мінімальний радіус зрізу для запобігання сингулярності [м].
 * @param result Вказівник на структуру для запису результату.
 * @return Код помилки (0 — успіх, -1 — null pointer, 1 — точка в зоні сингулярності).
 */
int dipole_calc_field(const electric_dipole_t* dipole,
                      const dipole_vec3_t* obs_point,
                      double min_r_cutoff,
                      dipole_field_result_t* result);
```
```cpp
// Опис функції поля диполя у C++20 через std::expected або статус
[[nodiscard]] DipoleFieldResult calculate_dipole_field(const ElectricDipoleData& dipole,
                                                       const DipoleVec3& obs_point,
                                                       double min_r_cutoff = 1e-12) noexcept;
```
:::

**Математичний контракт виконання:**
Обчислення виконуються у строго зафіксованому математичному порядку:
```
r = obs_point - dipole->position
R = |r|
if R < min_r_cutoff:
    result->is_singular = 1
    result->potential = 0.0
    result->E_field = (0, 0, 0)
    result->E_magnitude = 0.0
    return 1

r_hat = r / R
p_dot_rhat = dipole->moment · r_hat

result->potential = (1 / (4·π·ε₀)) · (p_dot_rhat / R²)
result->E_field = (1 / (4·π·ε₀)) · (3 · p_dot_rhat · r_hat - dipole->moment) / R³
result->E_magnitude = |result->E_field|
result->is_singular = 0
return 0
```
- **Параметр відсічки `min_r_cutoff`:** задається користувачем (типово `10⁻¹²` м). Якщо відстань до точки спостереження менша за цей поріг, функція не виконує ділення на близькі до нуля числа, заповнює результат нулями і повертає спеціальний статус `1`.
- **Гарантія безпеки за вказівниками:** якщо `dipole == NULL`, `obs_point == NULL` або `result == NULL`, функція негайно повертає код `-1` без виконання обчислень.

### 3.3. Розрахунок сили та моменту у зовнішньому полі (`dipole_calc_dynamics`)
Обчислює обертальний момент `τ = p × E`, потенціальну енергію `U = −p · E` та поступальну силу діелектрофорезу `F = (p · ∇)E`.

:::tabs
```c
/**
 * @brief Обчислює енергію, момент і силу, що діють на диполь.
 * @param dipole Вказівник на структуру диполя.
 * @param E_ext Вектор напруженості зовнішнього поля E у точці диполя [В/м].
 * @param grad_E_x Градієнт dE/dx (вектор трьох похідних dEx/dx, dEy/dx, dEz/dx).
 * @param grad_E_y Градієнт dE/dy.
 * @param grad_E_z Градієнт dE/dz.
 * @param result Вказівник на структуру результату динаміки.
 * @return Код помилки (0 — успіх, -1 — null pointer).
 */
int dipole_calc_dynamics(const electric_dipole_t* dipole,
                         const dipole_vec3_t* E_ext,
                         const dipole_vec3_t* grad_E_x,
                         const dipole_vec3_t* grad_E_y,
                         const dipole_vec3_t* grad_E_z,
                         dipole_dynamics_t* result);
```
```cpp
// Розрахунок динаміки диполя у C++20
[[nodiscard]] DipoleDynamicsResult calculate_dipole_dynamics(const ElectricDipoleData& dipole,
                                                             const DipoleVec3& E_ext,
                                                             const DipoleVec3& grad_E_x,
                                                             const DipoleVec3& grad_E_y,
                                                             const DipoleVec3& grad_E_z) noexcept;
```
:::

**Математичний контракт виконання:**
```
// Потенціальна енергія U = -p · E
result->potential_energy = -(dipole->moment.x * E_ext->x +
                             dipole->moment.y * E_ext->y +
                             dipole->moment.z * E_ext->z);

// Обертальний момент tau = p x E
result->torque.x = dipole->moment.y * E_ext->z - dipole->moment.z * E_ext->y;
result->torque.y = dipole->moment.z * E_ext->x - dipole->moment.x * E_ext->z;
result->torque.z = dipole->moment.x * E_ext->y - dipole->moment.y * E_ext->x;

// Поступальна сила F = (p · grad)E
result->force.x = dipole->moment.x * grad_E_x->x + dipole->moment.y * grad_E_y->x + dipole->moment.z * grad_E_z->x;
result->force.y = dipole->moment.x * grad_E_x->y + dipole->moment.y * grad_E_y->y + dipole->moment.z * grad_E_z->y;
result->force.z = dipole->moment.x * grad_E_x->z + dipole->moment.y * grad_E_y->z + dipole->moment.z * grad_E_z->z;
```
- **Фізична логіка сил:** поступальна сила обчислюється як добуток матриці тензора градієнта поля `∇E` на вектор дипольного моменту `p`. Якщо градієнт поля дорівнює нулю (`grad_E = 0`), сила `force` строго дорівнює нулю, навіть якщо напруженість поля `E_ext` велетенська.

### 3.4. Парна взаємодія двох диполів (`dipole_calc_interaction_energy`)
Обчислює потенціальну енергію парної взаємодії двох диполів у вакуумі чи діелектричному середовищі.

:::tabs
```c
/**
 * @brief Обчислює енергію взаємодії двох диполів U_12.
 * @param d1 Вказівник на перший диполь.
 * @param d2 Вказівник на другий диполь.
 * @param relative_permittivity Відносна діелектрична проникність середовища eps_r.
 * @param energy Вказівник на змінну для запису енергії [Дж].
 * @return Код помилки (0 — успіх, -1 — null pointer, 1 — збіг координат диполів).
 */
int dipole_calc_interaction_energy(const electric_dipole_t* d1,
                                    const electric_dipole_t* d2,
                                    double relative_permittivity,
                                    double* energy);
```
```cpp
// Енергія парної взаємодії двох диполів у C++20
[[nodiscard]] double calculate_interaction_energy(const ElectricDipoleData& d1,
                                                  const ElectricDipoleData& d2,
                                                  double relative_permittivity = 1.0);
```
:::

**Математичний контракт виконання:**
```
r_vec = d2->position - d1->position
R = |r_vec|
if R < 1e-12:
    return 1

r_hat = r_vec / R
p1_dot_p2 = d1->moment · d2->moment
p1_dot_rhat = d1->moment · r_hat
p2_dot_rhat = d2->moment · r_hat

coeff = 1.0 / (4.0 * pi * eps_0 * eps_r * R^3)
*energy = coeff * (p1_dot_p2 - 3.0 * p1_dot_rhat * p2_dot_rhat)
return 0
```
- **Валідація діелектричного середовища:** якщо `relative_permittivity < 1.0`, функція використовує значення `1.0` (вакуум) для уникнення фізично некоректних від'ємних чи нульових значень проникності.

## 4. Класи C++ (Об'єктно-орієнтований інтерфейс C++20)

Для сучасних C++ додатків надається header-only обгортка у просторі назв `physics::electromagnetism`. Клас `ElectricDipole` реалізує семантику переміщення, RAII та об'єктно-орієнтовані методи обчислення полів без прямої маніпуляції C-вказівниками.

```cpp
namespace physics::electromagnetism {

class ElectricDipole {
public:
    constexpr ElectricDipole() noexcept = default;
    constexpr ElectricDipole(const dipole_vec3_t& pos, const dipole_vec3_t& mom) noexcept
        : position_(pos), moment_(mom) {}

    [[nodiscard]] static ElectricDipole from_debye(const dipole_vec3_t& pos, 
                                                   const dipole_vec3_t& mom_dir, 
                                                   double debye_val) noexcept {
        const double factor = debye_val * 3.33564e-30;
        return ElectricDipole{pos, {mom_dir.x * factor, mom_dir.y * factor, mom_dir.z * factor}};
    }

    [[nodiscard]] const dipole_vec3_t& position() const noexcept { return position_; }
    [[nodiscard]] const dipole_vec3_t& moment() const noexcept { return moment_; }

    [[nodiscard]] dipole_field_result_t calculate_field(const dipole_vec3_t& obs_point, 
                                                         double cutoff = 1e-12) const noexcept {
        dipole_field_result_t res{};
        electric_dipole_t raw{position_, moment_, 0.0};
        dipole_calc_field(&raw, &obs_point, cutoff, &res);
        return res;
    }

private:
    dipole_vec3_t position_{0.0, 0.0, 0.0};
    dipole_vec3_t moment_{0.0, 0.0, 0.0};
};

} // namespace physics::electromagnetism
```

## 5. Типові пастки та крайові випадки при розрахунках

При використанні даного API обчислювачу слід враховувати такі важливі крайові випадки:

1. **Сингулярність наближення точкового диполя при `r → 0`.**
   Формули `1/r³` та `1/r²` є наближеннями далекого поля (`r » d`). При відстанях `r`, порівнянних із фізичним розміром диполя `d`, вирази точкового диполя дають величезну похибку. Для ближнього поля необхідно обчислювати точні суми двох кулонівських потенціалів двох зарядів.

2. **Залежність дипольного моменту від вибору початку координат для заряджених систем.**
   Якщо система має ненульовий сумарний заряд (`Q ≠ 0`), спроба обчислити дипольний момент без вказівки фіксованого початку координат призведе до невідтворюваних результатів. Перед розрахунком завжди перевіряйте умову електронейтральності `Q = ∑ qᵢ = 0`.

3. **Нехтування діелектричною проникністю середовища.**
   При обчисленні поля диполів у розчинах чи біологічних тканинах необхідно враховувати статичну або високочастотну діелектричну проникність середовища `ε_r`, ділячи коефіцієнт `k_e` на `ε_r`. Для води при кімнатній температурі `ε_r ≈ 80`, що зменшує силу взаємодії у 80 разів.
