# 📋 Довідник інтерфейсів та специфікацій: std::function, std::move_only_function та std::function_ref

Цей довідник містить вичерпний опис публічних інтерфейсів, синтаксичних констант, гарантій винятків, внутрішніх метапрограмувальних обмежень та правил вживання для універсальних типів стирання типів у мові C++: класичного володіючого контейнера `std::function` (C++11), move-only контейнера `std::move_only_function` (C++23) та безволодісного погляду `std::function_ref` (C++26).

---

## Інтерфейс std::function<R(Args...)> (C++11)

Класовий шаблон `std::function` визначено в заголовочному файлі `<functional>`. Він обгортає будь-який викликальний об'єкт (функцію, лямбду, функтор, вказівник на метод чи поле), що приймає аргументи типів `Args...` і повертає значення, що конвертується до типу `R`.

```cpp
namespace std {
    template <typename Res, typename... ArgTypes>
    class function<Res(ArgTypes...)> {
    public:
        using result_type = Res;

        // Вкладені typedefs для сумісності з C++11 (видалені у C++20)
        // using argument_type = ArgType;              (лише при 1 аргументі)
        // using first_argument_type = Arg1;           (лише при 2 аргументах)
        // using second_argument_type = Arg2;          (лише при 2 аргументах)

        // Конструктори та деструктор
        constexpr function() noexcept;
        constexpr function(nullptr_t) noexcept;
        function(const function& other);
        function(function&& other) noexcept;

        template <typename F>
        function(F&& f);

        // Історичні конструктори з алокаторами (вилучені у C++17)
        // template <typename Alloc> function(allocator_arg_t, const Alloc&) noexcept;
        // template <typename Alloc, typename F> function(allocator_arg_t, const Alloc&, F&&);

        ~function();

        // Оператори присвоєння
        function& operator=(const function& other);
        function& operator=(function&& other) noexcept;
        function& operator=(nullptr_t) noexcept;

        template <typename F>
        function& operator=(F&& f);

        template <typename F>
        function& operator=(reference_wrapper<F> f) noexcept;

        // Модифікатори
        void swap(function& other) noexcept;

        // Обстерігачі стану (State Observers)
        explicit operator bool() const noexcept;

        // Оператор виклику
        Res operator()(ArgTypes... args) const;

        // Інтроспекція типів (RTTI Target Access)
        const std::type_info& target_type() const noexcept;

        template <typename T>
        T* target() noexcept;

        template <typename T>
        const T* target() const noexcept;
    };

    // Нечленські функції порівняння та swap
    template <typename Res, typename... Args>
    bool operator==(const function<Res(Args...)>& f, nullptr_t) noexcept;

    template <typename Res, typename... Args>
    bool operator==(nullptr_t, const function<Res(Args...)>& f) noexcept;

    template <typename Res, typename... Args>
    bool operator!=(const function<Res(Args...)>& f, nullptr_t) noexcept;

    template <typename Res, typename... Args>
    bool operator!=(nullptr_t, const function<Res(Args...)>& f) noexcept;

    template <typename Res, typename... Args>
    void swap(function<Res(Args...)>& lhs, function<Res(Args...)>& rhs) noexcept;
}
```

### Деталізований специфікатор методів std::function

#### 1. Конструктори та метапрограмувальні обмеження

##### Порожній конструктор
```cpp
constexpr function() noexcept;
constexpr function(nullptr_t) noexcept;
```
Створює порожній об'єкт `std::function`, який не містить жодного збереженого функтора. Виклик `operator bool()` для таких об'єктів завжди повертає `false`. Пам'ять у купі не виділяється, внутрішні вказівники на тланки диспатчеризації ініціалізуються нульовими значеннями (`nullptr`).

##### Конструктор копіювання
```cpp
function(const function& other);
```
Копіює вміст `other`. Якщо `other` містить об'єкт типу `F`, цей тип `F` мусить задовольняти концептуальній вимозі `CopyConstructible` (тобто вираз `F(src)` повинен бути валідним). Якщо внутрішній об'єкт `F` розміщується у SBO-буфері `other`, викликається його конструктор копіювання на новому місці. Якщо ж об'єкт знаходиться у купі, викликається оператор `operator new()` для виділення нового блоку пам'яті відповідного розміру та здійснюється глибоке копіювання.
- **Гарантія винятків**: Сильна гарантія (Strong Exception Guarantee). Якщо виділення пам'яті у купі або конструктор копіювання `F` кидає виняток, створений об'єкт не залишає пошкодженого стану, а виділена пам'ять автоматично звільняється.

##### Конструктор переміщення
```cpp
function(function&& other) noexcept;
```
Забирає володіння ресурсом у `other`. Якщо `other` зберігав об'єкт у купі, відбувається швидка передача 64-бітного покажчика за `O(1)`, а `other` переводиться у порожній стан (`nullptr`). Якщо ж об'єкт розміщувався у внутрішньому SBO-буфері, його вміст переміщується у SBO-буфер нового об'єкта через placement move-конструктор, після чого вихідний об'єкт руйнується.

##### Шаблонний універсальний конструктор
```cpp
template <typename F> function(F&& f);
```
Приймає довільний об'єкт виклику `f`.
**Умови участі у розв'язанні перевантажень (SFINAE / Concepts)**:
- Вираз `std::invoke(std::declval<F&>(), std::declval<ArgTypes>()...)` має бути синтаксично виправданим та конвертуватися до типу `Res`.
- Тип `F` після видалення посилань та кваліфікаторів (`std::decay_t<F>`) не повинен збігатися з типом `std::function<Res(ArgTypes...)>`.
- Тип `F` не повинен бути обгорткою `std::reference_wrapper`.
- Якщо `f` є сирим вказівником на функцію або вказівником на метод класу, і його значення дорівнює `nullptr`, конструктор створює порожній об'єкт `std::function` замість спроби збереження нульового покажчика.

#### 2. Оператор виклику operator()

```cpp
Res operator()(ArgTypes... args) const;
```
Виконує безпосередній непрямий виклик збереженого об'єкта за допомогою `std::invoke(stored_callable, std::forward<ArgTypes>(args)...)`.
- **Гарантія винятків**: Якщо об'єкт є порожнім (`!*this`), кидає виняток `std::bad_function_call`. Якщо всередині збережено викликальний об'єкт, усі винятки, висунуті всередині його тіла, прокидаються назовні без змін.
- **Константність**: Оператор оголошено як `const`. Це означає, що `std::function` можна викликати через константне посилання. Проте, якщо внутрішній функтор має мутабельний стан (наприклад, лямбда з прапорцем `mutable`), `std::function` все одно дозволяє його виконання через непрямий виклик тланка, що є відомою прогалиною константности C++11.

#### 3. Інтроспекція та доступ до цілі: target() та target_type()

```cpp
const std::type_info& target_type() const noexcept;

template <typename T> T* target() noexcept;
template <typename T> const T* target() const noexcept;
```
Дають можливість безпечно отримати сирий покажчик на внутрішній об'єкт, якщо його справжній тип відомий під час виконання.
- `target_type()` повертає `typeid(T)`, де `T` — це тип збереженого функтора (після `std::decay`). Якщо `std::function` порожній, повертається `typeid(void)`.
- `target<T>()` перевіряє, чи збігається запрошений тип `T` із типом збереженого об'єкта `target_type() == typeid(T)`. У разі збігу повертає неконстантний або константний покажчик на цей об'єкт. У разі розбіжності типів або якщо `std::function` порожній, повертає `nullptr`.

```cpp
#include <functional>
#include <iostream>
#include <cassert>

int multiply(int a, int b) { return a * b; }

int main() {
    std::function<int(int, int)> fn = multiply;

    // Перевірка типу через target_type()
    if (fn.target_type() == typeid(int(*)(int, int))) {
        std::cout << "Target is a raw function pointer!\n";
    }

    // Отримання сирого покажчика через target<T>()
    using RawFnPtr = int(*)(int, int);
    RawFnPtr* raw_ptr = fn.target<RawFnPtr>();
    assert(raw_ptr != nullptr && *raw_ptr == multiply);
}
```

---

## Інтерфейс std::move_only_function (C++23)

Класовий шаблон `std::move_only_function` введений у C++23 у заголовочному файлі `<functional>`. Він призначений для збереження об'єктів, які не можна копіювати (наприклад, лямбд із захопленням `std::unique_ptr` чи `std::thread`).

Головною синтаксичною відмінністю є підтримка кваліфікаторів у самому шаблоні типу: `std::move_only_function<Res(Args...) cv ref noexcept>`.

```cpp
namespace std {
    template <typename Res, typename... ArgTypes>
    class move_only_function<Res(ArgTypes...) /* cv ref noexcept */> {
    public:
        using result_type = Res;

        // Конструктори
        constexpr move_only_function() noexcept;
        constexpr move_only_function(nullptr_t) noexcept;
        move_only_function(move_only_function&& other) noexcept;

        template <typename F>
        move_only_function(F&& f);

        template <typename VT, typename... Args>
        explicit move_only_function(in_place_type_t<VT>, Args&&... args);

        template <typename VT, typename U, typename... Args>
        explicit move_only_function(in_place_type_t<VT>, initializer_list<U> il, Args&&... args);

        // ДЕСТРУКТОР ТА ЗМАГАЛЬНІ ОПЕРАТОРИ КОПІЮВАННЯ ВІДСУТНІ (Deleted)
        move_only_function(const move_only_function&) = delete;
        move_only_function& operator=(const move_only_function&) = delete;

        ~move_only_function();

        // Оператори присвоєння
        move_only_function& operator=(move_only_function&& other) noexcept;
        move_only_function& operator=(nullptr_t) noexcept;

        template <typename F>
        move_only_function& operator=(F&& f);

        // Модифікатори
        void swap(move_only_function& other) noexcept;

        // Обстерігачі
        explicit operator bool() const noexcept;

        // Оператор виклику успадковує cv/ref/noexcept кваліфікатори шаблону!
        Res operator()(ArgTypes... args) /* cv ref noexcept */;
    };

    // Нечленські функції порівняння та swap
    template <typename Res, typename... Args>
    bool operator==(const move_only_function<Res(Args...)>& f, nullptr_t) noexcept;

    template <typename Res, typename... Args>
    void swap(move_only_function<Res(Args...)>& lhs, move_only_function<Res(Args...)>& rhs) noexcept;
}
```

### Специфікація кваліфікаторів сигнатури std::move_only_function

Стандарт C++23 підтримує 12 різних варіацій кваліфікаторів виклику для `std::move_only_function`:

1. `Res(Args...)`: виклик `operator()` на non-const lvalue об'єктах.
2. `Res(Args...) const`: виклик `operator()` на const lvalue об'єктах (найчастіший вибір для потоково-безпечних функцій).
3. `Res(Args...) &`: виклик дозволено лише на lvalue посиланнях.
4. `Res(Args...) const &`: виклик на const lvalue посиланнях.
5. `Res(Args...) &&`: **One-shot function** — виклик дозволено лише один раз на rvalue (`std::move(fn)(args)`). Це ідеально підходить для одноразових завдань, асинхронних промісів (promises) та тасок, які передають володіння ресурсом далі.
6. `Res(Args...) const &&`: виклик на const rvalue.
7. Версії 1–6 із специфікатором `noexcept`: оператор виклику оголошується як `noexcept`, а конструктор перевіряє за допомогою `std::is_nothrow_invocable_r`, що внутрішній об'єкт гарантує відсутність винятків.

```cpp
#include <functional>
#include <memory>
#include <iostream>

int main() {
    auto ptr = std::make_unique<int>(100);

    // 1. Move-Only лямбда із кваліфікатором const
    std::move_only_function<int() const> fn1 = [p = std::move(ptr)]() {
        return *p;
    };
    std::cout << fn1() << '\n';

    // 2. One-Shot лямбда (можна викликати лише один раз через rvalue)
    auto resource = std::make_unique<std::string>("Data Buffer");
    std::move_only_function<void() &&> fn_once = [r = std::move(resource)]() mutable {
        std::cout << "Processing " << *r << '\n';
        r.reset();
    };

    // fn_once(); // ПОМИЛКА КОМПІЛЯЦІЇ: fn_once має кваліфікатор &&
    std::move(fn_once)(); // Успішно!
}
```

### Відсутність RTTI у std::move_only_function

З метою зменшення розміру внутрішньої таблиці вказівників (Vtable) та підвищення ефективності виклику, з `std::move_only_function` **повністю вилучено RTTI-інтроспекцію**. Об'єкт не має методів `target()` та `target_type()`. Це дозволяє усунути генерацію `typeid` для кожної лямбди у програмі та зменшує розмір таблиці диспатчеризації до двох або трьох покажчиків.

---

## Інтерфейс std::function_ref (C++26)

Класовий шаблон `std::function_ref` входить до стандарту C++26 (заголовочний файл `<functional>`). Це легковаговий безволодісний об'єкт-погляд (view), що складається з покажчика на об'єкт `void*` та покажчика на статичну тланк-функцію.

```cpp
namespace std {
    template <typename Res, typename... ArgTypes>
    class function_ref<Res(ArgTypes...) /* cv noexcept */> {
    public:
        // Конструктори від будь-якого callable без алокацій
        template <typename F>
        constexpr function_ref(F* f) noexcept;

        template <typename F>
        constexpr function_ref(F&& f) noexcept;

        // Конструктор від методів класів (Bound member pointers)
        template <auto f, typename T>
        constexpr function_ref(T&& obj) noexcept;

        template <auto f>
        constexpr function_ref() noexcept;

        // Конструктори та оператори копіювання (trivially copyable)
        constexpr function_ref(const function_ref&) noexcept = default;
        constexpr function_ref& operator=(const function_ref&) noexcept = default;

        // Оператор виклику
        Res operator()(ArgTypes... args) const /* noexcept */;
    };

    // Автоматична вивід типів (Deduction Guides)
    template <typename F>
    function_ref(F*) -> function_ref<F>;
}
```

### Фундаментальні відмінності std::function_ref від володіючих контейнерів

1. **Відсутність володіння (Non-owning View)**: `std::function_ref` не створює копій та не переміщує переданий функтор. Він зберігає лише неконстантний вказівник на вихідний об'єкт. Переданий функтор мусить залишатися живим протягом усього часу існування `std::function_ref`.
2. **Відсутність порожнього стану (No Empty State)**: `std::function_ref` не має конструктора за замовчуванням без параметрів і не може бути ініціалізований через `nullptr`. Він завжди посилається на дійсний об'єкт виклику.
3. **Відсутність `operator bool()`**: Оскільки порожній стан відсутній, перевірка на `bool` не потрібна та вилучена з інтерфейсу.
4. **Тривіальна копійованість (Trivially Copyable)**: Розмір об'єкта становить `2 * sizeof(void*)` (16 байтів у 64-бітних системах). Він передається через процесорні регістри як звичайна структура з двох покажчиків.

```cpp
#include <functional>
#include <iostream>
#include <vector>

// Приклад використання std::function_ref у C++26 для виклику зворотного зв'язку
void filter_numbers(const std::vector<int>& numbers, std::function_ref<bool(int)> predicate) {
    for (int n : numbers) {
        if (predicate(n)) {
            std::cout << n << ' ';
        }
    }
    std::cout << '\n';
}

int main() {
    std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    int threshold = 5;
    // Лямбда передається без жодної алокації та без копіювання буфера!
    filter_numbers(data, [threshold](int val) { return val > threshold; });
}
```

---

## Підсумкова порівняльна специфікація

Нижче наведено порівняльну таблицю усіх п'яти основних способів передачі та збереження об'єктів виклику в сучасному C++:

| Властивість / Гарантія | `std::function` (C++11) | `std::move_only_function` (C++23) | `std::function_ref` (C++26) | `std::any` (C++17) | C-покажчик `R(*)(Args...)` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Заголовочний файл** | `<functional>` | `<functional>` | `<functional>` | `<any>` | Вбудований мовою |
| **Володіння ресурсом** | Повне (Heap/SBO) | Повне (Heap/SBO) | **Безволодісний (View)** | Повне (Heap/SBO) | Ні (лише код) |
| **Підтримка Copy-only лямбд** | Так | Так | Так | Так | Лише без захвату |
| **Підтримка Move-only лямбд** | **Ні** | **Так** | **Так** | Ні | **Ні** |
| **Підтримка `noexcept` сигнатур**| Ні | **Так** | **Так** | Ні | Так |
| **Підтримка `&&` (One-shot)** | Ні | **Так** | Ні | Ні | Ні |
| **Порожній стан (`nullptr`)** | Так (`operator bool`) | Так (`operator bool`) | **Ні (завжди валидний)** | Так (`has_value`) | Так |
| **Виняток при порожньому виклику**| `std::bad_function_call` | `std::bad_function_call` | Неможливо | `std::bad_any_cast` | Undefined Behavior |
| **RTTI (`target()`, `target_type()`)**| **Так** | Ні | Ні | **Так (`type()`)** | Ні |
| **Розмір об'єкта (`sizeof`)** | 32–48 байтів | 24–32 байти | **16 байтів** | 24–32 байти | 8 байтів |
| **Гарантія відсутності алокацій**| Ні (лише для SBO) | Ні (лише для SBO) | **Гарантовано (0 алокацій)** | Ні (лише для SBO) | **Гарантовано (0 алокацій)** |
