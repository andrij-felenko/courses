# 📑 Специфікація інтерфейсу AST-рушія функцій Кальмара

Ця специфікація визначає стандартний інтерфейс прикладного програмування (C/C++ API) для синтаксичного представлення, статичного аналізу складності, перевірки формальних інваріантів та детермінованого обчислення арифметичних виразів у класі елементарних функцій за Кальмаром `E`.

Архітектура рушія розроблена для практичного застосування у вбудованих системах реального часу, SMT-розв'язувачах, компіляторах смарт-контрактів та верифікаторах формальних доведень, де критично необхідні строгі математичні гарантії завершення обчислень, передбачуване використання пам'яті та повна відсутність невизначеної поведінки (`undefined behavior`).

## Архітектурні принципи та фундаментальні інваріанти системи

Проектування інтерфейсу рушія підпорядковане п'яти базовим інженерним та теоретичним інваріантам, які забезпечують надійність виконання на будь-яких цільових архітектурах:

1. **Інваріант тотальності операцій (Total Function Invariant):**
Кожна базова операція рушія є всюди визначеною математичною функцією над множиною невід'ємних цілих чисел `ℕⁿ`. Усі математичні сингулярності та невизначеності традиційної машинної арифметики нормалізовані: цілочисельне ділення на нуль `Div(x, 0)` детерміновано повертає `0`, степінь `0⁰` повертає `1`, а монічне віднімання `x ∸ y` при `x < y` зрізається до `0`. Завдяки цьому рушій ніколи не викликає апаратних винятків процесора (`SIGFPE`, переривання ділення на нуль або недійсні інструкції).

2. **Інваріант вежової складності (Tower Complexity Invariant):**
Будь-яке синтаксичне дерево має однозначно обчислювану верхню межу висоти вежі експонент `k`. Статичний аналізатор гарантує, що значення виразу на будь-якому вхідному наборі даних не перевищить величину `2 ↑↑ k (max(x_i))`. Цей показник обчислюється виключно на основі структури дерева без запуску самого обчислення.

3. **Інваріант ізоляції пам'яті та відсутності динамічних виділень (Zero-Allocation Invariant):**
Під час безпосереднього виконання виразу обчислювач не здійснює жодних динамічних виділень пам'яті на купі (`heap allocations`). Усі змінні, аргументи функцій та лічильники циклів розміщуються у попередньо виділеному лінійному буфері фіксованого розміру (`KalmarEnvironment`). Це усуває ризики фрагментації пам'яті та робить рушій придатним для вбудованих систем із жорсткими обмеженнями пам'яті (Hard Real-Time Systems).

4. **Інваріант гарантованої завершуваності (Guaranteed Termination):**
Усі цикли підсумовування, перемноження та пошуку мають явні верхні числові межі, що обчислюються до входу в тіло циклу. Нескінченне зациклення або рекурсивний переповнення стека синтаксично неможливі, оскільки в AST відсутні інструкції довільних переходів або неструктуровані рекурсивні виклики.

5. **Інваріант потокобезпечності та реентерабельності (Reentrancy Invariant):**
Усі структури AST після їхньої побудови є строго незмінними (`immutable`). Одне й те саме синтаксичне дерево може одночасно обчислюватися у декількох паралельних потоках виконання з різними векторами середовища `KalmarEnvironment` без необхідності синхронізації м'ютексами. Піддерева констант та чистих операцій можуть безпечно розділятися між різними виразами (Shared Subterm Optimization), що суттєво зменшує загальне споживання оперативної пам'яті в багатоагентних обчислювальних середовищах.

## Структури даних та перечислення

### Коди операцій та типи вузлів AST

Перечислення типів вузлів кодує повний набір примітивів базису Кальмара:

:::tabs
```c
typedef enum {
    KALMAR_NODE_CONST       = 0x01,  /* Числова константа uint64_t */
    KALMAR_NODE_VAR         = 0x02,  /* Читання змінної за індексом середовища */
    KALMAR_NODE_ADD         = 0x10,  /* Додавання (lhs + rhs) */
    KALMAR_NODE_SUB         = 0x11,  /* Зрізане віднімання (lhs ∸ rhs) */
    KALMAR_NODE_MUL         = 0x12,  /* Множення (lhs · rhs) */
    KALMAR_NODE_DIV         = 0x13,  /* Безпечне цілочисельне ділення */
    KALMAR_NODE_EXP         = 0x14,  /* Цілочисельне піднесення до степеня */
    KALMAR_NODE_SUM         = 0x20,  /* Обмежена сума ∑_{z ≤ bound} body */
    KALMAR_NODE_PROD        = 0x21,  /* Обмежений добуток ∏_{z ≤ bound} body */
    KALMAR_NODE_SEARCH      = 0x22   /* Обмежений μ-пошук найменшого кореня */
} KalmarNodeType;
```
```cpp
enum class NodeType : uint8_t {
    Constant      = 0x01,
    Variable      = 0x02,
    Add           = 0x10,
    Subtract      = 0x11,
    Multiply      = 0x12,
    Divide        = 0x13,
    Exponent      = 0x14,
    BoundedSum    = 0x20,
    BoundedProd   = 0x21,
    BoundedSearch = 0x22
};
```
:::

### Коди результатів та помилок

:::tabs
```c
typedef enum {
    KALMAR_OK                    = 0,  /* Успішне завершення операції */
    KALMAR_ERR_NULL_POINTER      = 1,  /* Передано нульовий вказівник на вузол або буфер */
    KALMAR_ERR_INVALID_VAR_INDEX = 2,  /* Індекс змінної перевищує місткість середовища */
    KALMAR_ERR_OVERFLOW          = 3,  /* Результат перевищив максимальну місткість uint64_t */
    KALMAR_ERR_BUDGET_EXCEEDED   = 4,  /* Перевищено ліміт кількості обчислювальних кроків */
    KALMAR_ERR_INVALID_AST       = 5,  /* Дерево містить некоректні посилання або цикли */
    KALMAR_ERR_OUT_OF_MEMORY     = 6   /* Недостатньо пам'яті в арені для створення вузла */
} KalmarStatus;
```
```cpp
enum class StatusCode : uint8_t {
    Ok                  = 0,
    NullPointer         = 1,
    InvalidVarIndex     = 2,
    Overflow            = 3,
    BudgetExceeded      = 4,
    InvalidAst          = 5,
    OutOfMemory         = 6
};
```
:::

### Структура вузла виразу

:::tabs
```c
typedef struct KalmarNode KalmarNode;

struct KalmarNode {
    KalmarNodeType type;        /* Тип операції або атома */
    uint64_t       constant;    /* Числове значення для KALMAR_NODE_CONST */
    size_t         var_index;   /* Індекс змінної для VAR або параметр ітератора */
    KalmarNode*    left;        /* Лівий операнд або вираз межі циклу */
    KalmarNode*    right;       /* Правий операнд або тіло циклу/предикат */
};
```
```cpp
struct AstNode {
    NodeType               type{NodeType::Constant};
    uint64_t               constant{0};
    size_t                 var_index{0};
    std::unique_ptr<AstNode> left{nullptr};
    std::unique_ptr<AstNode> right{nullptr};
};
```
:::

### Структура середовища виконання

:::tabs
```c
typedef struct {
    uint64_t* vars;             /* Вказівник на лінійний масив змінних */
    size_t    capacity;         /* Загальна кількість доступних слотів */
    size_t    step_count;       /* Лічильник виконаних елементарних операцій */
    size_t    step_limit;       /* Максимально дозволений ліміт кроків (0 = без обмеження) */
} KalmarEnvironment;
```
```cpp
struct Environment {
    std::span<uint64_t> vars{};
    size_t              step_count{0};
    size_t              step_limit{0}; // 0 = без ліміту
};
```
:::

## Специфікація функцій мови C

### 1. Фабричні функції створення AST

#### `kalmar_make_const`
Створює вузол цілочисельної невід'ємної константи.
- **Сигнатура:** `KalmarNode* kalmar_make_const(uint64_t val);`
- **Передмови:** Немає. Приймає будь-яке значення типу `uint64_t`.
- **Післяумови:** Повертає вказівник на ініціалізований вузол типу `KALMAR_NODE_CONST`. Поля `left` та `right` встановлені у `NULL`. При невдачі виділення пам'яті повертає `NULL`.
- **Властивості:** Операція `O(1)` за часом та пам'яттю.

#### `kalmar_make_var`
Створює вузол звернення до змінної з вектора середовища.
- **Сигнатура:** `KalmarNode* kalmar_make_var(size_t index);`
- **Передмови:** `index` має відповідати запланованому діапазону змінних у середовищі.
- **Післяумови:** Повертає вузол типу `KALMAR_NODE_VAR` із збереженим індексом.
- **Властивості:** Операція `O(1)`.

#### `kalmar_make_binop`
Створює вузол бінарної арифметичної операції над двома підвиразами.
- **Сигнатура:** `KalmarNode* kalmar_make_binop(KalmarNodeType type, KalmarNode* left, KalmarNode* right);`
- **Передмови:** `type` має бути одним із значень: `KALMAR_NODE_ADD`, `KALMAR_NODE_SUB`, `KALMAR_NODE_MUL`, `KALMAR_NODE_DIV`, `KALMAR_NODE_EXP`. Операнди `left` та `right` не повинні бути `NULL`.
- **Післяумови:** Повертає кореневий вузол операції, що володіє переданими піддеревами. Якщо виділення пам'яті зазнало невдачі, повертає `NULL` (клієнт відповідає за звільнення операндів).

#### `kalmar_make_bounded`
Створює вузол обмеженого оператора (підсумовування, добутку або μ-пошуку).
- **Сигнатура:** `KalmarNode* kalmar_make_bounded(KalmarNodeType type, size_t var_index, KalmarNode* bound_expr, KalmarNode* body_expr);`
- **Передмови:** `type` має належати до множини `{KALMAR_NODE_SUM, KALMAR_NODE_PROD, KALMAR_NODE_SEARCH}`. Вказівники `bound_expr` та `body_expr` не повинні бути `NULL`. Параметр `var_index` вказує номер слота в середовищі, який виділяється під лічильник циклу `z`.
- **Післяумови:** Повертає вузол циклічного оператора.

#### `kalmar_free_tree`
Рекурсивно звільняє всю пам'ять, зайняту синтаксичним деревом.
- **Сигнатура:** `void kalmar_free_tree(KalmarNode* root);`
- **Передмови:** `root` — коректний вказівник на дерево або `NULL`.
- **Післяумови:** Пам'ять усіх дочірніх вузлів вивільняється. Функція є повністю безпечною до виклику з `NULL`.

---

### 2. Керування аренами пам'яті (Arena Memory Subsystem)

Для роботи в середовищах із забороною використання стандартної купи (`malloc`/`free`) бібліотека надає інтерфейс лінійної арени.

#### `kalmar_arena_create`
Створює неперервний блок пам'яті фіксованого розміру для швидкого розміщення вузлів без фрагментації.
- **Сигнатура:** `KalmarArena* kalmar_arena_create(size_t capacity_bytes);`
- **Передмови:** `capacity_bytes > sizeof(KalmarNode)`.
- **Післяумови:** Повертає вказівник на структуру арени.

#### `kalmar_arena_alloc_node`
Виділяє пам'ять під один вузол AST всередині арени через простий інкремент вказівника зміщення.
- **Сигнатура:** `KalmarNode* kalmar_arena_alloc_node(KalmarArena* arena);`
- **Передмови:** `arena` не `NULL`.
- **Післяумови:** Повертає вирівняний вказівник на вузол або `NULL`, якщо ємність арени вичерпано.

#### `kalmar_arena_reset`
Миттєво скидає лічильник виділеної пам'яті в арені до нуля без повузлового виклику деструкторів, роблячи всю пам'ять доступною для побудови нового AST.
- **Сигнатура:** `void kalmar_arena_reset(KalmarArena* arena);`

---

### 3. Функції статичного аналізу та перевірки

#### `kalmar_compute_tower_height`
Обчислює мінімальну висоту вежі експонент `k`, яка мажорує ріст функції.
- **Сигнатура:** `size_t kalmar_compute_tower_height(const KalmarNode* root);`
- **Передмови:** `root` — валідне синтаксичне дерево.
- **Післяумови:** Повертає точне ціле число `k ≥ 0`. Складність обчислення — `O(N)`, де `N` — кількість вузлів у дереві. Функція не має побічних ефектів і не змінює структуру дерева.

#### `kalmar_estimate_max_steps`
Обчислює аналітичну оцінку максимальної кількості кроків для заданих меж аргументів.
- **Сигнатура:** `uint64_t kalmar_estimate_max_steps(const KalmarNode* root, const uint64_t* max_arg_bounds, size_t num_args);`
- **Передмови:** `root` не `NULL`; `max_arg_bounds` містить верхні оцінки значень кожного аргументу.
- **Післяумови:** Повертає максимальну кількість арифметичних операцій, які можуть бути виконані інтерпретатором у найгіршому випадку.

#### `kalmar_validate_ast`
Перевіряє коректність синтаксичного дерева: відсутність циклів, коректність типів вузлів та відповідність індексів змінних заявленим межам.
- **Сигнатура:** `KalmarStatus kalmar_validate_ast(const KalmarNode* root, size_t max_allowed_var_idx);`
- **Післяумови:** Повертає `KALMAR_OK` або відповідний код помилки.

---

### 4. Функції виконання та обчислення

#### `kalmar_eval`
Виконує обчислення виразу у наданому середовищі змінних.
- **Сигнатура:** `KalmarStatus kalmar_eval(const KalmarNode* root, KalmarEnvironment* env, uint64_t* out_result);`
- **Передмови:** `root` не `NULL`; `env` містить ініціалізований масив `vars`; `out_result` не `NULL`.
- **Післяумови:** У разі успіху повертає `KALMAR_OK`, а в `*out_result` записує результат обчислення. Якщо кількість кроків перевищує `env->step_limit` (коли ліміт ненульовий), повертає `KALMAR_ERR_BUDGET_EXCEEDED`.

#### `kalmar_eval_predicate`
Спеціалізована функція обчислення булевого предиката.
- **Сигнатура:** `KalmarStatus kalmar_eval_predicate(const KalmarNode* root, KalmarEnvironment* env, bool* out_is_true);`
- **Передмови:** Вираз `root` представляє характеристичну функцію предиката (значення `0` або `1`).
- **Післяумови:** Записує `true`, якщо результат не дорівнює `0`, і `false`, якщо результат дорівнює `0`.

#### `kalmar_eval_batch`
Пакетне виконання виразу над матрицею вхідних векторів аргументів (використовується для векторизації та масової перевірки даних).
- **Сигнатура:** `KalmarStatus kalmar_eval_batch(const KalmarNode* root, const uint64_t* input_matrix, size_t num_rows, size_t num_cols, uint64_t* output_results);`
- **Передмови:** `input_matrix` містить `num_rows × num_cols` елементів; `output_results` має місткість щонайменше `num_rows`.
- **Післяумови:** Записує результати обчислення для кожного рядка у вихідний масив.

---

## Специфікація об'єктно-орієнтованого C++20 інтерфейсу

У мові C++ API інкапсулюється у простір імен `kalmar` із використанням семантики безпечного володіння ресурсами RAII, розумних вказівників `std::unique_ptr`, типів-представлень `std::span` та механізму повернення помилок `std::expected`.

Застосування `std::span` гарантує відсутність копіювання масивів аргументів при передачі у методи обчислення, забезпечуючи нульові накладні витрати пам'яті. Тип `std::expected` дозволяє клієнтському коду обробляти потенційні помилки переповнення та вичерпання бюджету без використання винятків, що забезпечує повну детермінованість і відповідність стандарту MISRA C++:2023.

```cpp
namespace kalmar {

class Expression {
public:
    Expression(Expression&& other) noexcept;
    Expression& operator=(Expression&& other) noexcept;
    ~Expression() = default;

    Expression(const Expression&) = delete;
    Expression& operator=(const Expression&) = delete;

    [[nodiscard]] Expression clone() const;

    [[nodiscard]] size_t tower_height() const noexcept;
    [[nodiscard]] size_t node_count() const noexcept;

    [[nodiscard]] std::expected<uint64_t, StatusCode> 
    evaluate(std::span<uint64_t> env) const noexcept;

    [[nodiscard]] std::expected<bool, StatusCode> 
    evaluate_as_predicate(std::span<uint64_t> env) const noexcept;

    static Expression make_constant(uint64_t val);
    static Expression make_variable(size_t var_idx);
    static Expression make_add(Expression lhs, Expression rhs);
    static Expression make_sub(Expression lhs, Expression rhs);
    static Expression make_mul(Expression lhs, Expression rhs);
    static Expression make_div(Expression lhs, Expression rhs);
    static Expression make_pow(Expression base, Expression exponent);
    static Expression make_sum(size_t var_idx, Expression bound, Expression body);
    static Expression make_prod(size_t var_idx, Expression bound, Expression body);
    static Expression make_search(size_t var_idx, Expression bound, Expression predicate);

private:
    std::unique_ptr<AstNode> root_;
    explicit Expression(std::unique_ptr<AstNode> root) noexcept;
};

} // namespace kalmar
```

---

## Інтеграція з системами інтерактивного та автоматичного доведення теорем

Бібліотека функцій Кальмара спроектована для трансляції виразів між мовами формальної верифікації (Lean 4, Coq, Isabelle/HOL) та форматом задач для автоматичних розв'язувачів SMT-LIB2:

1. **Трансляція булевих умовних операторів (ITE-термів):**
У системах SMT конструкція `(ite condition then_expr else_expr)` транслюється у чисто арифметичний вираз Кальмара без використання розгалужень керування:
```
ITE(C, T, E) = (C · T) + ((1 ∸ C) · E)
```
Оскільки характеристична функція предиката `C` повертає строго `1` або `0`, рівно один із доданків залишається активним.

2. **Експорт сертифікатів доведення (Proof Certificates):**
Рушій містить процедуру `kalmar_export_coq_term(const KalmarNode* root, char* buffer, size_t len)`, яка генерує коректний терм у системі типів Coq (із використанням індуктивного типу `nat` та бібліотеки `Arith.PeanoNat`). Це дозволяє автоматично переносити оптимізовані арифметичні формули у верифіковані мікроядра без втрати строгості доведення.

---

## Протокол діагностики та трасування обчислень (Tracing API)

Для глибокого налагодження та профілювання обчислень бібліотека надає інтерфейс зворотних викликів:

:::tabs
```c
typedef void (*KalmarTraceCallback)(const KalmarNode* node, const KalmarEnvironment* env, uint64_t intermediate_val, void* user_data);

void kalmar_set_trace_callback(KalmarEnvironment* env, KalmarTraceCallback cb, void* user_data);
```
```cpp
using TraceCallback = std::function<void(const AstNode& node, const Environment& env, uint64_t intermediate_val)>;

void set_trace_callback(Environment& env, TraceCallback cb);
```
:::

Коли функцію зворотного виклику встановлено, інтерпретатор викликає її після завершення обчислення кожного внутрішнього піддерева AST, передаючи:
- Вказівник або посилання на поточний вузол операції;
- Знімок поточного стану вектора змінних середовища;
- Обчислене проміжне числове значення;
- Користувацький контекст.

Це дозволяє точно вимірювати розподіл часу між різними рівнями вкладених циклів та візуалізувати динаміку зміни ітераторів.

---

## Взаємодія через FFI з високорівневими мовами (Python, Rust)

Завдяки сумісності із стандартом C ABI бібліотека легко підключається до високорівневих мов програмування:

- **Інтеграція з Python:** через модуль `ctypes` або `cffi` структури `KalmarNode` транслюються у класи Python, дозволяючи будувати AST у динамічному середовищі наукових обчислень (Jupyter Notebooks) та запускати компільований рушій на максимальній швидкості C.
- **Інтеграція з Rust:** бібліотека надає безпечну обгортку (safe wrapper crate) `kalmar-rs`, яка використовує систему володіння Rust для гарантії неможливості витоків пам'яті AST-дерев на етапі компіляції.

---

## Порівняльний аналіз C ABI та C++20 інтерфейсу: безпека та продуктивність

Проектування дворівневого інтерфейсу бібліотеки вирішує дилему між низькорівневою максимальною швидкодією та типобезпекою прикладного коду:

1. **Безвиняткова дисципліна (Zero-Exception Guarantee):**
У C++ інтерфейсі свідомо не використовуються винятки (`throw`/`try`/`catch`). Замість них застосовано моноадичний тип повернення помилок `std::expected<T, StatusCode>`. Це виключає накладні витрати на таблиці розгортання стека (`unwind tables`) і забезпечує суворо детермінований час виконання кожної функції.

2. **Вирівнювання пам'яті та кеш-лінії:**
Структура `KalmarNode` оптимізована для вирівнювання за 64-байтовою межею кеш-лінії сучасних мікропроцесорів (Cache Line Alignment). Це усуває явище помилкового поділу кешу (*false sharing*) при паралельному аналізі незалежних дерев у різних потоках.

3. **Нульова вартість абстракцій (Zero-Cost Abstractions):**
Клас-обгортка `kalmar::Expression` повністю інлайниться компілятором у результуючий машинний код. Використання `std::span<uint64_t>` для представлення середовища змінних не створює жодних проміжних копій у пам'яті і транслюється безпосередньо у пару машинних регістрів (вказівник та довжина).

---

## Інваріанти сертифікації для критичних систем (DO-178C, ISO 26262, MISRA C)

У задачах сертифікації бортового програмного забезпечення авіоніки (стандарт DO-178C рівнів DAL-A/B) та автомобільної електроніки (ISO 26262 ASIL-D) бібліотека функцій Кальмара відповідає найсуворішим вимогам функціональної безпеки:

1. **Передбачуваність часу виконання в найгіршому випадку (WCET):**
Завдяки функції `kalmar_estimate_max_steps` розробник отримує точну теоретичну та апаратну верхню межу процесорних тактів до початку виконання, що унеможливлює зриви дедлайнів у циклі реального часу.

2. **Відповідність стандарту MISRA C:2012:**
- Правило 17.2 (заборона прямої або непрямої рекурсії під час виконання): функція `kalmar_eval` реалізована з можливістю ітеративного стек-обходу без використання динамічного стека викликів.
- Правило 21.3 (заборона динамічного виділення пам'яті у рантаймі): всі структури середовища є статично виділеними або розміщуються у попередньо зарезервованій арені пам'яті.
- Правило 12.4 (гарантія відсутності переповнення цілих чисел без знаку): інтерпретатор перевіряє межі перед виконанням кожної операції множення та експоненти.

---

## Формат серіалізації та бінарного представлення AST

Для збереження скомпільованих синтаксичних дерев на диск або передачі мережею бібліотека визначає компактний бінарний формат `KALMAR_BIN_V1`.

Структура бінарного пакету:
- **Заголовок (8 байт):** 4 байти магічного числа `0x4B 0x41 0x4C 0x4D` (`KALM`), 2 байти версії формату (`0x0001`), 2 байти контрольної суми CRC16.
- **Таблиця вузлів у префіксному порядку (Prefix Traversal):** кожен вузол кодується 1 байтом типу `type`, після якого йдуть додаткові поля:
  - Для `KALMAR_NODE_CONST`: 8 байт числа у форматі Little-Endian.
  - Для `KALMAR_NODE_VAR`: 4 байти індексу змінної.
  - Для бінарних операторів та кванторів: безпосередньо слідують серіалізовані піддерева лівого та правого операндів.

Функції серіалізації:
- `KalmarStatus kalmar_serialize(const KalmarNode* root, uint8_t* buffer, size_t buffer_len, size_t* out_written);`
- `KalmarStatus kalmar_deserialize(const uint8_t* buffer, size_t buffer_len, KalmarNode** out_root);`

Цей формат забезпечує швидке завантаження попередньо верифікованих формул без повторного синтаксичного аналізу.

---

## Таблиця семантичної поведінки операцій

Нижче наведено зведену таблицю математичної семантики кожної базової операції, обробки особливих станів та оцінки висоти вежі:

| Тип операції AST | Математичний запис | Поведінка на нульових входах | Обробка граничних випадків | Зміна висоти вежі `k` |
| :--- | :--- | :--- | :--- | :--- |
| `KALMAR_NODE_CONST` | `c` | Повертає `c` | Працює з усім діапазоном `uint64_t` | `k = 0` |
| `KALMAR_NODE_VAR` | `x_i` | Повертає `env[i]` | Якщо `i ≥ capacity`, повертає `0` | `k = 0` |
| `KALMAR_NODE_ADD` | `a + b` | `0 + b = b` | Переповнення фіксується статусом помилки | `max(k_a, k_b)` |
| `KALMAR_NODE_SUB` | `a ∸ b` | `0 ∸ b = 0`, `a ∸ 0 = a` | Якщо `a < b`, повертає `0` (монічне) | `max(k_a, k_b)` |
| `KALMAR_NODE_MUL` | `a · b` | `0 · b = 0` | Раннє відсікання при множенні на 0 | `max(k_a, k_b)` |
| `KALMAR_NODE_DIV` | `⌊a / b⌋` | `Div(a, 0) = 0`, `Div(0, b) = 0` | Повністю тотальна без винятків | `max(k_a, k_b)` |
| `KALMAR_NODE_EXP` | `aᵇ` | `0⁰ = 1`, `0ᵇ = 0` (при `b > 0`), `a⁰ = 1` | Обчислення за алгоритмом бінарного піднесення | `max(k_a, k_b) + 1` |
| `KALMAR_NODE_SUM` | `∑_{z ≤ y} g(z)` | При `y = 0` повертає `g(0)` | Ітерації строго детерміновані | `k_g + 1` |
| `KALMAR_NODE_PROD` | `∏_{z ≤ y} g(z)` | При `y = 0` повертає `g(0)` | Ранній вихід при виявленні `g(z) = 0` | `k_g + 1` |
| `KALMAR_NODE_SEARCH`| `μ z ≤ y [P(z)]` | При `y = 0` перевіряє `P(0)` | Якщо корінь не знайдено, повертає `y` | `k_y` |

---

## Приклад повного інтеграційного робочого циклу

Наведений нижче приклад демонструє типовий життєвий цикл використання API: побудова AST логічного предиката перевірки парності числа, статична верифікація висоти вежі експонент, виконання обчислення для вибірки чисел та автоматичне очищення ресурсів:

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

void run_c_parity_workflow(void) {
    /* Побудова виразу Rem(n, 2): n ∸ (2 · (n / 2)) */
    KalmarNode* div_expr = kalmar_make_binop(KALMAR_NODE_DIV, kalmar_make_var(0), kalmar_make_const(2));
    KalmarNode* mul_expr = kalmar_make_binop(KALMAR_NODE_MUL, kalmar_make_const(2), div_expr);
    KalmarNode* rem_expr = kalmar_make_binop(KALMAR_NODE_SUB, kalmar_make_var(0), mul_expr);
    KalmarNode* is_even  = kalmar_make_binop(KALMAR_NODE_SUB, kalmar_make_const(1), rem_expr);

    size_t k = kalmar_compute_tower_height(is_even);
    printf("C API: Verified tower height k = %zu\n", k);

    uint64_t vars[2] = {0};
    KalmarEnvironment env = { .vars = vars, .capacity = 2, .step_count = 0, .step_limit = 1000 };

    bool is_true = false;
    vars[0] = 42;
    if (kalmar_eval_predicate(is_even, &env, &is_true) == KALMAR_OK) {
        printf("Number 42 is %s\n", is_true ? "EVEN" : "ODD");
    }

    kalmar_free_tree(is_even);
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>

void run_cpp_parity_workflow() {
    using namespace kalmar;

    auto div_expr = Expression::make_div(Expression::make_variable(0), Expression::make_constant(2));
    auto mul_expr = Expression::make_mul(Expression::make_constant(2), std::move(div_expr));
    auto rem_expr = Expression::make_sub(Expression::make_variable(0), std::move(mul_expr));
    auto is_even  = Expression::make_sub(Expression::make_constant(1), std::move(rem_expr));

    size_t k = is_even.tower_height();
    std::cout << "C++ API: Verified tower height k = " << k << "\n";

    std::vector<uint64_t> env_vars(2, 0);
    env_vars[0] = 42;

    auto res = is_even.evaluate_as_predicate(env_vars);
    if (res.has_value()) {
        std::cout << "Number 42 is " << (res.value() ? "EVEN" : "ODD") << "\n";
    }
}
```
:::

Цей інтерфейс забезпечує повну ізоляцію логіки обчислень від низькорівневих деталей платформи, надаючи детермінований, математично верифікований та безпечний інструмент для роботи з елементарною арифметикою в критичних системах.
