# 📋 Інтерфейс та структура даних булевих схем AC0

Ця вставка містить повний довідник програмного інтерфейсу (API) та структур даних для роботи з комбінаційними булевими схемами класу AC⁰. Інтерфейс призначений для конструювання, аналізу геометричних параметрів графа (розмір, глибина, fan-in, fan-out), перевірки належності схеми до обмежень класу AC⁰ та конвертації між ЗНФ/КНФ формами і шаруватими чергованими графами.

## 1. Специфікація структур даних C та C++

Структура даних булевої схеми являє собою орієнтований ациклічний граф (англ. *directed acyclic graph, DAG*). Вхідні змінні позначаються окремими індексами `0, 1, ..., n - 1`. Кожен внутрішній гейт отримує унікальний ідентифікатор `GateId` (ціле число від 0 до `size(C) - 1`), що дозволяє адресувати елементи в масиві гейтів за константний час `O(1)`.

### Загальні типи даних та константи

- **GateId (`uint32_t` / `size_t`)**: Унікальний ідентифікатор гейта у графі схеми. Вентілі зберігаються у топологічно відсортованому масиві, де для будь-якого вхідного ребра `v → u` виконується сувора нерівність `v < u`.
- **VarId (`uint32_t` / `size_t`)**: Індекс вхідної бітової змінної `xᵢ ∈ {0, 1}`.
- **CircuitDepth (`size_t`)**: Глибина графа схемы (довжина найдовшого шляху від вхідного гейта до вихідного). Для класу AC⁰ цей параметр обов'язково задовольняє `depth ≤ d = O(1)`.
- **CircuitSize (`size_t`)**: Загальна кількість внутрішніх логічних елементів (гейтів) у графі.

### Опис контрактів груп функцій

1. **`circuit_create` / `AC0Builder`**: Ініціалізація структури графа із заданою кількістю входів. Створюється базовий контейнер і виділяється пам'ять під масив гейтів.
2. **`circuit_add_gate`**: Додавання гейта `AND`, `OR` або `NOT` із можливістю передачі довільної кількості вхідних ребер (unbounded fan-in). Для `NOT` кількість ребер строго дорівнює 1.
3. **`circuit_validate_ac0`**: Перевірка відповідності критеріям класу AC⁰: зафіксована константна глибина `d ≤ d_max` та поліноміальний розмір `size ≤ nᵏ`.
4. **`circuit_compute_fanin_stats`**: Обчислення статистики вхідних та вихідних валентностей гейтів (максимальна, мінімальна та середня валентність, максимальний fan-out).

### Валідаційні інваріанти та обробка помилок

- **Інваріант топологічного порядку**: Ідентифікатори вхідних гейтів у списку `fan_in` для даного гейта `u` повинні бути строго меншими за `u.id` (`v.id < u.id`). Це гарантує відсутність циклів у графі без необхідності виконання додаткового алгоритму Тар'яна на кожному кроці обчислення.
- **Інваріант вхідних бітів**: Індекси вхідних змінних `input_var` не можуть перевищувати заявлену кількість входів `num_inputs`. При виході за межі масиву функція конструювання повертає помилку `AC0_ERROR_INVALID_VAR`.
- **Помилки динамічної пам'яті**: У C API всі функції створення повертають `NULL` при невдачі виділення пам'яті. У C++ API викидається виняток `std::bad_alloc` або `std::invalid_argument`.

## 2. Публічний інтерфейс C та C++

:::tabs
```c
/* c — Публічний C-інтерфейс бібліотеки libac0circuit */
#ifndef LIBAC0_CIRCUIT_H
#define LIBAC0_CIRCUIT_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    AC0_GATE_INPUT = 0,
    AC0_GATE_NOT   = 1,
    AC0_GATE_AND   = 2,
    AC0_GATE_OR    = 3
} ac0_gate_type_t;

typedef struct ac0_gate_t {
    size_t id;
    ac0_gate_type_t type;
    size_t var_index;       /* Тільки для AC0_GATE_INPUT */
    size_t* fan_in_ids;     /* Масив ідентифікаторів вхідних гейтів */
    size_t fan_in_count;
    size_t fan_out_count;   /* Кількість вихідних ребер */
    size_t layer;           /* Рівень гейта у графі (0 для входів) */
} ac0_gate_t;

typedef struct ac0_circuit_t {
    size_t num_inputs;
    size_t num_gates;
    size_t max_gates;
    ac0_gate_t* gates;
    size_t output_gate_id;
    size_t computed_depth;  /* Кешована глибина схеми */
} ac0_circuit_t;

typedef struct ac0_fanin_stats_t {
    size_t max_fan_in;
    size_t min_fan_in;
    double avg_fan_in;
    size_t max_fan_out;
} ac0_fanin_stats_t;

/* Функції створення та вилучення */
ac0_circuit_t* ac0_circuit_create(size_t num_inputs, size_t initial_capacity);
void ac0_circuit_destroy(ac0_circuit_t* circuit);

/* Функції конструювання графа */
size_t ac0_circuit_add_input(ac0_circuit_t* circuit, size_t var_index);
size_t ac0_circuit_add_gate(ac0_circuit_t* circuit, ac0_gate_type_t type, const size_t* inputs, size_t count);
bool ac0_circuit_set_output(ac0_circuit_t* circuit, size_t gate_id);

/* Аналітичні функції */
size_t ac0_circuit_get_depth(ac0_circuit_t* circuit);
size_t ac0_circuit_get_size(ac0_circuit_t* circuit);
ac0_fanin_stats_t ac0_circuit_get_stats(const ac0_circuit_t* circuit);

/* Валідація критеріїв AC0 */
bool ac0_circuit_validate(const ac0_circuit_t* circuit, size_t max_allowed_depth, size_t max_allowed_size);

/* Обчислення значення */
uint8_t ac0_circuit_evaluate(const ac0_circuit_t* circuit, const uint8_t* input_bits, size_t input_len);

#ifdef __cplusplus
}
#endif

#endif /* LIBAC0_CIRCUIT_H */
```
```cpp
// cpp — Заголовочний файл C++20 класу AC0CircuitAPI
#ifndef AC0_CIRCUIT_API_HPP
#define AC0_CIRCUIT_API_HPP

#include <vector>
#include <memory>
#include <span >
#include <optional>
#include <string>
#include <cstddef>

namespace ac0 {

enum class GateKind { Input, Not, And, Or };

struct GateStats {
    size_t max_fan_in{0};
    size_t min_fan_in{0};
    double avg_fan_in{0.0};
    size_t max_fan_out{0};
};

class CircuitAPI {
public:
    virtual ~CircuitAPI() = default;

    virtual size_t add_input(size_t var_index) = 0;
    virtual size_t add_gate(GateKind kind, std::span<const size_t> inputs) = 0;
    virtual void set_output_gate(size_t gate_id) = 0;

    [[nodiscard]] virtual size_t get_depth() const = 0;
    [[nodiscard]] virtual size_t get_size() const = 0;
    [[nodiscard]] virtual GateStats get_stats() const = 0;
    [[nodiscard]] virtual bool is_valid_ac0(size_t max_depth, size_t max_size) const noexcept = 0;

    [[nodiscard]] virtual uint8_t evaluate(std::span<const uint8_t> input_bits) const = 0;
};

class CircuitBuilder : public CircuitAPI {
public:
    explicit CircuitBuilder(size_t num_inputs);
    ~CircuitBuilder() override = default;

    size_t add_input(size_t var_index) override;
    size_t add_gate(GateKind kind, std::span<const size_t> inputs) override;
    void set_output_gate(size_t gate_id) override;

    [[nodiscard]] size_t get_depth() const override;
    [[nodiscard]] size_t get_size() const override;
    [[nodiscard]] GateStats get_stats() const override;
    [[nodiscard]] bool is_valid_ac0(size_t max_depth, size_t max_size) const noexcept override;

    [[nodiscard]] uint8_t evaluate(std::span<const uint8_t> input_bits) const override;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace ac0

#endif // AC0_CIRCUIT_API_HPP
```
:::

## 3. Детальний розбір алгоритмів аналізу графа схеми

### Обчислення глибини графа (Dynamic Programming Depth Calculation)
Глибина схеми визначає тривалість критичного шляху проходження бітового сигналу від входу до виходу. Для обчислення глибини функція `ac0_circuit_get_depth` реалізує алгоритм динамічного програмування у топологічному порядку:

```
layer(v_input) = 0
layer(u)       = 1 + max { layer(v) | v ∈ fan_in(u) }
depth(C)       = layer(output_gate)
```

Оскільки масив `gates` підтримується у топологічному порядку, розрахунок рівнів `layer(u)` виконується за один лінійний прохід `O(size(C) + edges)`. Підсумкове значення зберігається у кеш-полі `computed_depth` структури `ac0_circuit_t`, що робить повторні виклики `O(1)`.

### Статистичний аналіз валентностей (Fan-in / Fan-out Statistics)
Для перевірки належності схеми до обмежень AC⁰ важливо контролювати розподіл вхідних та вихідних валентностей гейтів. Функція `ac0_circuit_get_stats` здійснює повну інспекцію графа:

- **Максимальний fan-in (`max_fan_in`)**: Максимальна кількість вхідних ребер серед усіх гейтів схеми. Для схем класу AC⁰ цей параметр може досягати `O(n)`.
- **Мінімальний fan-in (`min_fan_in`)**: Мінімальна кількість вхідних ребер серед внутрішніх вентилів `AND/OR/NOT`.
- **Середній fan-in (`avg_fan_in`)**: Відношення сумарної кількості внутрішніх ребер графа до кількості внутрішніх гейтів `∑ fan_in_count / num_internal_gates`.
- **Максимальний fan-out (`max_fan_out`)**: Максимальна кількість вихідних сигналів, що розгалужуються від одного гейта на наступні шари.

### Валідація належності до класу AC0
Метод `ac0_circuit_validate` виконує комплексну перевірку графа схеми на відповідність трьом формальним критеріям:

1. **Константність глибини**: Перевіряється, чи не перевищує обчислена глибина `computed_depth` зафіксований поріг `max_allowed_depth` (наприклад, `d ≤ 5`).
2. **Поліноміальність розміру**: Перевіряється, чи не перевищує загальна кількість вентилів `num_gates` заданий поліноміальний поріг `max_allowed_size = nᵏ`.
3. **Коректність логічного базису**: Перевіряється, що схеми побудовані виключно з гейтів `INPUT`, `NOT`, `AND` та `OR`, а гейти `NOT` розміщені лише на рівні вхідних бітів або мають `fan_in_count == 1`.

Якщо хоча б один із критеріїв порушено, метод повертає `false` та встановлює код помилки валідації, що запобігає подальшому використанню нестандартних схем у симуляторі.

## 4. Опис параметрів та поведінки методів

### Створення та керування пам'яттю
- `ac0_circuit_create(num_inputs, initial_capacity)`: Виділяє динамічну пам'ять під структуру `ac0_circuit_t` та внутрішній масив `gates` ємністю `initial_capacity`. Повертає вказівник на створений об'єкт або `NULL` при помилці пам'яті.
- `ac0_circuit_destroy(circuit)`: Рекурсивно звільняє масиви вхідних ребер `fan_in_ids` для кожного елемента схеми, а потім звільняє головний масив гейтів і сам об'єкт `ac0_circuit_t`.

### Конструювання логічних шарів
- `ac0_circuit_add_input(circuit, var_index)`: Додає новий вхідний гейт типу `AC0_GATE_INPUT`, пов'язаний із бітовою змінною з індексом `var_index`. Повертає `GateId` доданого гейта.
- `ac0_circuit_add_gate(circuit, type, inputs, count)`: Додає внутрішній логічний гейт типу `type` (`AND`, `OR` або `NOT`). Масив `inputs` розміру `count` містить ідентифікатори вхідних гейтів попередніх шарів. Функція виділяє динамічну пам'ять для зберігання `fan_in_ids` і копіює дані. Повертає `GateId` доданого елемента.
- `ac0_circuit_set_output(circuit, gate_id)`: Призначає гейт із номером `gate_id` головним вихідним гейтом схеми. Значення цього гейта буде повернуто при виклику `ac0_circuit_evaluate`.

### Аналіз топології та обчислення значень
- `ac0_circuit_get_depth(circuit)`: Обчислює глибину графа за допомогою динамічного програмування вздовж топологічного порядку. Для кожного гейта `u` його рівень визначається як `layer(u) = 1 + max_{v ∈ fan_in(u)} layer(v)`. Кешує значення у полі `computed_depth`.
- `ac0_circuit_get_size(circuit)`: Повертає загальну кількість гейтів `num_gates` у схемі, включаючи вхідні гейти та логічні вентилі.
- `ac0_circuit_get_stats(circuit)`: Проводить статистичний обхід графа та обчислює максимальну, мінімальну й середню вхідну валентність (fan-in), а також максимальне розгалуження сигналу (fan-out).
- `ac0_circuit_evaluate(circuit, input_bits, input_len)`: Виконує обчислення схеми на вхідному векторі `input_bits` довжиною `input_len`. Перевіряє сумісність довжини вектора із заявленою кількістю входів `num_inputs`. Обходить гейти у топологічному порядку та повертає підсумковий біт `0` або `1`.

### Інтеграція C++ API
У C++ реалізації `ac0::CircuitBuilder` надає безпечний обгортковий інтерфейс pImpl (pointer to implementation), що приховує деталі логіки конструювання схеми за інкапсульованим вказівником `std::unique_ptr<Impl>`. Методи `CircuitBuilder` приймають бітові послідовності та списки входів у вигляді `std::span`, що виключає потребу у ручному управлінні покажчиками та виділенні тимчасових масивів.

Даний C/C++ API контракт забезпечує суворий тип-безпечний інтерфейс для інтеграції симулятора AC⁰ у системи логічного синтезу та перевірки схемних меж.
