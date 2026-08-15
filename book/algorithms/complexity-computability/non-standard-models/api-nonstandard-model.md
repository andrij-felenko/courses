# 📋 Специфікація інтерфейсу обчислювача нестандартних моделей

Ця вставка містить детальну специфікацію програмного інтерфейсу (API) бібліотеки обчислення та моделювання нестандартних арифметичних систем і машин Тюринга. Інтерфейс надає структурам даних і функціям C/C++ точний контракт для роботи з символьними нестандартними числами, оцінки логічних предикатів за допомогою принципу Оверспілу, кодування конфігурацій та управління траєкторією нестандартних машин Тюринга.

## 1. Загальна архітектура та принципи побудови API

Програмний інтерфейс розроблено за двома стандартизованими моделями:
1. **Низькорівневий C-інтерфейс (C99):** Забезпечує пряму сумісність із процедурними системами, C-ABI та системними викликами. Використовує чисті структури `struct`, фіксовані типи даних `int64_t`, `uint8_t` та функціональні вказівники. Пам'ять для об'єктів виділяється або на стеку, або передається через явні вказівники.
2. **Об'єктно-орієнтований C++20 інтерфейс:** Спирається на концепції сучасної мови C++, семантику володіння RAII, безпечні представники масивів `std::span`, трьохсторонні оператори порівняння `<=>` та безпеку винятків.

Обидва інтерфейси моделюють елементи кільця `ℤ[H]`, де `H` — символьний нестандартний елемент нескінченної величини.

## 2. Специфікація структур даних та арифметичного інтерфейсу

### 2.1. Константи та структури даних

:::tabs
```c
#define MAX_DEGREE 4
#define TAPE_SIZE 64

typedef struct {
    int64_t coeffs[MAX_DEGREE];
} NonStandardInt;

typedef struct {
    uint8_t tape[TAPE_SIZE];
    size_t head_pos;
    int current_state;
    NonStandardInt step_count;
    bool halted;
} NonStandardTM;
```
```cpp
namespace NonStandard {

constexpr size_t MAX_DEGREE = 4;
constexpr size_t TAPE_SIZE = 64;

class NonStandardInt {
private:
    std::vector<int64_t> coeffs_;
};

class NonStandardTuringMachine {
private:
    std::vector<uint8_t> tape_;
    size_t head_pos_;
    int state_;
    NonStandardInt steps_;
    bool halted_;
};

} // namespace NonStandard
```
:::

#### Поля структури `NonStandardInt`
- `coeffs`: Масив із `MAX_DEGREE` 64-бітних цілих чисел із знаком. Індекс `i` відповідає коефіцієнту при ступені `Hⁱ`. Поліном має вигляд:
```
coeffs[0] + coeffs[1]·H + coeffs[2]·H² + ... + coeffs[MAX_DEGREE-1]·H^(MAX_DEGREE-1)
```

#### Поля структури `NonStandardTM`
- `tape`: Фіксований масив байтів розміром `TAPE_SIZE`, що представляє стрічку машини Тюринга.
- `head_pos`: Поточна позиція зчитувально-записувальної головки (`0 <= head_pos < TAPE_SIZE`).
- `current_state`: Цілочисельний ідентифікатор стану автомата.
- `step_count`: Об'єкт `NonStandardInt`, що відстежує лічильник виконаних кроків (стандартних або гіпер-кроків).
- `halted`: Булевий прапор, який вказує на завершення обчислень машиною Тюринга.

---

### 2.2. Сигнатури функцій створення та арифметичних операцій

:::tabs
```c
/* Конструктори та ініціалізація */
NonStandardInt ns_create_standard(int64_t val);
NonStandardInt ns_create_inf(size_t degree, int64_t coeff);

/* Предикати та порівняння */
bool ns_is_standard(const NonStandardInt* num);
int ns_compare(const NonStandardInt* a, const NonStandardInt* b);

/* Арифметичні операції */
NonStandardInt ns_add(const NonStandardInt* a, const NonStandardInt* b);
NonStandardInt ns_multiply(const NonStandardInt* a, const NonStandardInt* b);

/* Друк */
void ns_print(const NonStandardInt* num);
```
```cpp
namespace NonStandard {

class NonStandardInt {
public:
    explicit NonStandardInt(int64_t standard_val = 0);
    static NonStandardInt make_inf(size_t degree, int64_t coeff = 1);

    [[nodiscard]] bool is_standard() const noexcept;
    [[nodiscard]] std::span<const int64_t> coefficients() const noexcept;

    auto operator<=>(const NonStandardInt& other) const noexcept;
    bool operator==(const NonStandardInt& other) const noexcept;

    NonStandardInt operator+(const NonStandardInt& other) const;
    NonStandardInt operator*(const NonStandardInt& other) const;

    [[nodiscard]] std::string to_string() const;
};

} // namespace NonStandard
```
:::

#### Опис функцій інтерфейсу

1. **`ns_create_standard(int64_t val)` / `NonStandardInt(int64_t standard_val)`**
   - **Призначення:** Створення об'єкта нестандартного числа, який відповідає стандартному натуральному або цілому числу `val ∈ ℤ`.
   - **Параметри:** `val` — 64-бітне ціле число з знаком.
   - **Повертає:** Об'єкт `NonStandardInt` з `coeffs[0] = val` та нульовими вищими коефіцієнтами.
   - **Прекондиція:** Немає.

2. **`ns_create_inf(size_t degree, int64_t coeff)` / `make_inf(degree, coeff)`**
   - **Призначення:** Створення нескінченно великого нестандартного монома вида `coeff · H^degree`.
   - **Параметри:**
     - `degree`: Специфікує ступінь нескінченного елемента `H`. Повинен задовольняти умову `0 <= degree < MAX_DEGREE`.
     - `coeff`: Цілочисельний коефіцієнт при даному ступені.
   - **Повертає:** Структуру `NonStandardInt` з `coeffs[degree] = coeff` та нулями у всіх інших позиціях.
   - **Крайові випадки:** Якщо `degree >= MAX_DEGREE`, функція обнуляє масив коефіцієнтів та повертає еквівалент `0`.

3. **`ns_is_standard(const NonStandardInt* num)` / `is_standard()`**
   - **Призначення:** Перевірка, чи належить елемент `num` стандартному початковому сегменту `ℕ`.
   - **Параметри:** `num` — невидозмінюваний вказівник на структуру `NonStandardInt`. Не повинен бути `NULL`.
   - **Повертає:** `true`, якщо всі коефіцієнти при вищих степенях `coeffs[1...MAX_DEGREE-1]` дорівнюють `0`, а `coeffs[0] >= 0`. Повертає `false`, якщо існує хоча б один ненульовий коефіцієнт `coeffs[i] != 0` для `i >= 1`, або якщо `coeffs[0] < 0`.

4. **`ns_compare(const NonStandardInt* a, const NonStandardInt* b)` / `operator<=>`**
   - **Призначення:** Визначення відношення порядку між двома нестандартними числами в моделі `ℕ + ℤ × ℚ`.
   - **Параметри:** `a`, `b` — невидозмінювані вказівники на порівнювані об'єкти.
   - **Повертає:**
     - `1` / `std::strong_ordering::greater`, якщо `a > b` у порядку моделі;
     - `-1` / `std::strong_ordering::less`, якщо `a < b`;
     - `0` / `std::strong_ordering::equal`, якщо `a == b`.
   - **Логіка порівняння:** Алгоритм здійснює зворотний перебір коефіцієнтів від `i = MAX_DEGREE - 1` до `0`. Перший індекс `i`, у якому `a->coeffs[i] != b->coeffs[i]`, визначає результат порівняння.

5. **`ns_add(a, b)` / `operator+`**
   - **Призначення:** Обчислення суми двох нестандартних чисел в кільці `ℤ[H]`.
   - **Повертає:** Нову структуру `NonStandardInt`, де `result.coeffs[i] = a->coeffs[i] + b->coeffs[i]`.
   - **Крайові випадки:** Якщо в результаті додавання виникає переповнення `int64_t`, поведінка відповідає стандарту мови для знаковим цілих.

6. **`ns_multiply(a, b)` / `operator*`**
   - **Призначення:** Обчислення добутку двох елементів з алгебраїчним відтинанням вищих степеней, що перевищують `MAX_DEGREE - 1`.
   - **Повертає:** Результат згортки многочленів.
   - **Формула обчислення:**
```
result.coeffs[k] = ∑ (a->coeffs[i] · b->coeffs[j])  для всіх i + j = k
```

---

## 3. Специфікація модуля принципу Оверспілу та нестандартних машин Тюринга

### 3.1. Інтерфейс аналізатора принципу Оверспілу

:::tabs
```c
typedef bool (*StandardPredicate)(int64_t n);

bool ns_check_overspill(StandardPredicate predicate, const NonStandardInt* limit);
```
```cpp
namespace NonStandard {

class OverspillEvaluator {
public:
    static bool evaluate(std::function<bool(int64_t)> pred, const NonStandardInt& limit);
};

} // namespace NonStandard
```
:::

#### Специфікація параметрів та поведінки

- **`pred` / `predicate`:** Унарна функція-предикат, яка отримує стандартне число `n ∈ ℕ` і повертає `true` або `false`.
- **`limit`:** Елемент `NonStandardInt`, до якого або через який розширюється предикат.
- **Повертає:** `true`, якщо предикат є істинним на скінченній тестовій вибірці `[0, 100)` і границя `limit` є нестандартною.
- **Виняткові ситуації:** Якщо предикат повертає `false` хоча б для одного натурального числа у тестовому діапазоні `[0, 100)`, перевірка Оверспілу повертає `false`.

---

### 3.2. Інтерфейс нестандартної машини Тюринга

:::tabs
```c
void tm_init(NonStandardTM* tm);
void tm_step(NonStandardTM* tm);
```
```cpp
namespace NonStandard {

class NonStandardTuringMachine {
public:
    explicit NonStandardTuringMachine(size_t tape_size = 64);

    void step();
    void execute_hyper_steps(const NonStandardInt& hyper_limit);

    [[nodiscard]] std::string get_status() const;
    [[nodiscard]] const std::vector<uint8_t>& get_tape() const noexcept;
    [[nodiscard]] const NonStandardInt& get_step_count() const noexcept;
    [[nodiscard]] bool is_halted() const noexcept;
};

} // namespace NonStandard
```
:::

#### Контракт методів виконання

1. **`tm_step(tm)` / `step()`**
   - **Опис:** Виконує один стандартний крок машини Тюринга у звичайному часі.
   - **Посткондиція:** Збільшує `step_count` на `1`. Змінює стан стрічки та позицію головки відповідно до таблиці переходів.

2. **`execute_hyper_steps(const NonStandardInt& hyper_limit)`**
   - **Опис:** Моделює виконання машини протягом нестандартного гіпер-часу `hyper_limit ∈ M \ ℕ`.
   - **Прекондиція:** `hyper_limit.is_standard() == false`.
   - **Посткондиція:** Додає значення `hyper_limit` до лічильника `step_count`. Стрічка переходить у символьний підсумковий стан гіпер-обчислення.

3. **`get_status()`**
   - **Опис:** Повертає текстове представлення поточного стану машини Тюринга (позицію головки, кількість кроків у вигляді символьного нестандартного числа та прапор зупинки).

---

## 4. Політика обробки помилок, потокобезпечність та гарантії безпеки

1. **Управління пам'яттю та RAII:** C++ API повністю позбавлено сирих вказівників і гарантує відсутність витоків пам'яті за принципом RAII. Всі об'єкти автоматично вивільняють внутрішні вектори при виході з області видимості. C API використовує передачу параметрів по заповнюваних вказівниках із обов'язковою попередньою перевіркою вказівників на `NULL`.
2. **Переповнення степеней мономів:** Множення та додавання у кільці `ℤ[H]` автоматично відтинають коефіцієнти при степенях `Hᵏ` для `k >= MAX_DEGREE`. Це запобігає неконтрольованому зростанню векторів пам'яті під час тривалих символьних маніпуляцій та моделювання алгоритмів.
3. **Потокобезпечність (Thread Safety):** Екземпляри класу `NonStandardInt` є константними (immutable) після створення і є повністю потокобезпечними для паралельного читання кількома потоками виконання без додаткового блокування. Модифікуючі методи `NonStandardTuringMachine` (зокрема `step()` та `execute_hyper_steps()`) змінюють внутрішній стан стрічки і вимагають зовнішнього синхронізаційного захисту (м'ютексів або спін-локів) при одночасному доступі з різних потоків.
4. **Сумісність із SMT-соліверами:** Специфікація типів даних `NonStandardInt` розроблена з урахуванням прямої серіалізації в формат специфікацій SMT-LIB2, що дозволяє використовувати створені об'єкти як контр-приклади при верифікації LIA-теорій у соліверах Z3 та CVC5.

