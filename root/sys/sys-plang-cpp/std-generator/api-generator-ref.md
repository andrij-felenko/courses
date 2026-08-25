# 📋 Довідник специфікації та інтерфейсу std::generator

Цей довідник містить повну технічну специфікацію, детальний опис контракту та аналіз внутрішньої поведінки класу `std::generator`, введеного у заголовочному файлі `<generator>` стандарту C++23. Клас виступає уніфікованим синхронним корутинним генератором лінивих послідовностей і реалізує концепт `std::ranges::input_range`.

---

## 1. Сигнатура шаблону та виведення типів

Шаблон класу `std::generator` є параметованим трьома параметрами, які визначають поведінку розіменовування ітератора, внутрішнє збереження типів та користувацьке керування оперативною пам'яттю.

```cpp
namespace std {
    template<
        class Ref,
        class V = void,
        class Allocator = void
    > class generator;
}
```

### Детальний аналіз типів-параметрів

- **Параметр `Ref` (Тип розіменовування / Reference type):** Це основний параметр, який вимагається завжди. Він визначає тип, що повертається при виконанні операції розіменовування ітератора `*it`. Параметр `Ref` може набувати значень лівостороннього посилання (`const T&` або `T&`), правостороннього посилання (`T&&`) або звичайного значення `T`. Якщо `Ref` є посиланням на об'єкт, ітератор повертає посилання безпосередньо з внутрішнього буфера кадру корутини, убезпечуючи програму від зайвого копіювання.
- **Параметр `V` (Тип значення / Value type):** Визначає псевдонім `std::generator::value_type`, який використовується оболонками та алгоритмами стандартної бібліотеки. За замовчуванням параметр `V` дорівнює `void`. Якщо `V` є `void`, компілятор автоматично обчислює тип значення за допомогою виразу `std::remove_cvref_t<Ref>`. Наприклад, для `std::generator<const std::string&>` тип `Ref` дорівнює `const std::string&`, а тип `V` стає `std::string`.
- **Параметр `Allocator` (Тип розподілювача пам'яті):** Вказує тип користувацького розподілювача пам'яті (наприклад, `std::pmr::polymorphic_allocator<char>`). Якщо параметр дорівнює `void`, генератор використовує стандартне виділення кадру корутини в купі за допомогою глобального `operator new`.

### Внутрішні псевдоніми типів (Member Types)

```cpp
template<class Ref, class V, class Allocator>
class generator {
public:
    using yielded = std::conditional_t<std::is_reference_v<Ref>, Ref, const Ref&>;
    using value_type = std::conditional_t<std::is_void_v<V>, std::remove_cvref_t<Ref>, V>;
    using difference_type = std::ptrdiff_t;
    using allocator_type = Allocator;
    
    class promise_type;
    class iterator;
};
```

Псевдонім `yielded` визначає точний тип виразу, який приймається методом `promise_type::yield_value()`. Якщо `Ref` є посиланням, `yielded` збігається з `Ref`. Якщо `Ref` є значенням, `yielded` стає `const Ref&`.

---

## 2. Контракт володіння та спеціальні методи класу

Об'єкт `std::generator` є одноосібним власником ресурсу — дескриптора корутини `std::coroutine_handle<promise_type>`. Клас реалізує сувору семантику передачі володіння (Move-only Semantics) та повністю забороняє будь-які операції копіювання.

```cpp
// 1. Конструктор за замовчуванням створює порожній генератор
constexpr generator() noexcept : coroutine_(nullptr) {}

// 2. Конструктор копіювання вилучено (Copy Operations Deleted)
generator(const generator&) = delete;
generator& operator=(const generator&) = delete;

// 3. Конструктор переміщення передає дескриптор без виділення пам'яті
generator(generator&& rhs) noexcept
    : coroutine_(std::exchange(rhs.coroutine_, nullptr)) {}

// 4. Оператор присвоєння переміщенням знищує поточний кадр та забирає новий
generator& operator=(generator&& rhs) noexcept {
    if (this != std::addressof(rhs)) {
        if (coroutine_) {
            coroutine_.destroy();
        }
        coroutine_ = std::exchange(rhs.coroutine_, nullptr);
    }
    return *this;
}

// 5. Деструктор автоматично вивільняє кадр корутини у купі
~generator() {
    if (coroutine_) {
        coroutine_.destroy();
    }
}
```

### Гарантії безпеки та тривалість життя
- Виклик деструктора `~generator()` здійснює перевірку дійсності дескриптора `coroutine_`. Якщо дескриптор є дійсним, деструктор викликає `coroutine_.destroy()`. Це призводить до виконання деструкторів усіх живих локальних змінних усередині тіла корутини та вивільнення кадру з оперативноі пам'яті.
- Після переміщення через `std::move(gen)` об'єкт-джерело залишається у порожньому стані із `coroutine_ == nullptr`. Спроба викликати метод `begin()` або розіменувати ітератор переміщеного об'єкта призводить до порушення контракту та невизначеної поведінки (Undefined Behavior).

---

## 3. Інтерфейс діапазонів та лінивий запуск

Об'єкт `std::generator` забезпечує доступ до відгенерованих елементів через стандартний інтерфейс методів `begin()` та `end()`.

```cpp
iterator begin();
std::default_sentinel_t end() noexcept { return std::default_sentinel; }
```

### Покрокові правила виконання методу `begin()`
1. При створенні об'єкта генератора тіло корутини не виконується одразу, оскільки початковий стан `initial_suspend()` повертає `std::suspend_always`. Це забезпечує семантику лінивого запуску.
2. Перший виклик `begin()` запускає корутину на виконання через внутрішній виклик `coroutine_.resume()`.
3. Тіло корутини виконується до першого оператора `co_yield` або до завершення функції через `co_return`.
4. Якщо корутина призупиняється на операторі `co_yield`, метод `begin()` повертає дійсний ітератор, який вказує на згенерований елемент.
5. Якщо корутина завершується порожньою без виконання `co_yield`, метод `begin()` повертає ітератор, рівний сентинелу `end()`.
6. Повторний виклик `begin()` на вже запущеній або вичерпаній корутині є забороненим і призводить до порушення контракту однопрохідності.

---

## 4. Клас ітератора std::generator::iterator

Внутрішній клас `iterator` забезпечує переміщення по корутині та реалізує вимоги концепту `std::input_iterator`.

```cpp
class generator::iterator {
public:
    using value_type = generator::value_type;
    using difference_type = generator::difference_type;
    using iterator_concept = std::input_iterator_tag;

    iterator() noexcept : coroutine_(nullptr) {}

    // Операція розіменовування повертає посилання на згенероване значення
    yielded operator*() const noexcept(std::is_nothrow_copy_constructible_v<yielded>) {
        return coroutine_.promise().value();
    }

    // Операція інкремента відновлює виконання корутини
    iterator& operator++() {
        coroutine_.promise().resume_next();
        return *this;
    }

    void operator++(int) {
        (void)operator++();
    }

    // Порівняння з сентинелом перевіряє завершення корутини
    friend bool operator==(const iterator& it, std::default_sentinel_t) noexcept {
        return it.coroutine_.done();
    }
private:
    std::coroutine_handle<promise_type> coroutine_{nullptr};
};
```

### Важливі специфічні властивості ітератора

- **Однопрохідність (Single-pass range):** Ітератор корутини не підтримує повторний прохід по елементах. Спроба зберегти копію ітератора та виконати `operator++()` на обох копіях призведе до того, що обидва ітератори просуватимуть той самий єдиний кадр корутини.
- **Розповсюдження винятків (Exception Propagation):** Якщо всередині тіла корутини під час генерування виникає необроблений виняток, виконання корутини зупиняється, а виняток перехоплюється методом `promise_type::unhandled_exception()`. При наступній спробі викликати `operator++()` або `begin()` на ітераторі збережений виняток повторно викидається у контекст викликача через `std::rethrow_exception`.

---

## 5. Специфікація рекурсивного делегування std::ranges::elements_of

Для підтримки виразової рекурсивної генерації без сповільнення продуктивності стандарт C++23 визначає допоміжну структуру `std::ranges::elements_of`.

```cpp
namespace std::ranges {
    template<range R, class Alloc = allocator<char>>
    struct elements_of {
        [[no_unique_address]] R range;
        [[no_unique_address]] Alloc allocator = Alloc();
    };

    template<class R>
    elements_of(R&&) -> elements_of<R>;

    template<class R, class Alloc>
    elements_of(R&&, Alloc) -> elements_of<R, Alloc>;
}
```

### Механізм обробки `yield_value` для `elements_of`

Коли корутина викликає `co_yield std::ranges::elements_of(range)`, обіцянка виконує спеціалізований метод `yield_value`:

```cpp
template<class R, class Alloc>
auto yield_value(std::ranges::elements_of<R, Alloc> r) {
    // 1. Отримує дескриптор вкладеного генератора r.range
    // 2. Встановлює parent_link вкладеної обіцянки на поточну обіцянку
    // 3. Повертає awaiter, який перемикає виконання безпосередньо у вкладену корутину
    return element_awaiter{std::forward<R>(r.range)};
}
```

Завдяки цьому механізму рекурсивні виклики генераторів утворюють однозв'язний список обіцянок. Відновлення виконується за один симетричний крок `O(1)`, усуваючи проміжні призупинення та розгортання системного стеку.

---

## 6. Внутрішня специфікація класу promise_type

Клас `promise_type` відповідає за керування станом корутини, збереження тимчасових значень, виділення пам'яті та обробку винятків.

```cpp
template<class Ref, class V, class Allocator>
class generator<Ref, V, Allocator>::promise_type {
public:
    // Створення генератора з обіцянки
    generator get_return_object() noexcept {
        return generator{std::coroutine_handle<promise_type>::from_promise(*this)};
    }

    // Початкове призупинення (лінивий запуск)
    std::suspend_always initial_suspend() noexcept { return {}; }

    // Фінальне призупинення повертає керування у батьківську корутину
    auto final_suspend() noexcept {
        struct final_awaiter {
            bool await_ready() noexcept { return false; }
            std::coroutine_handle<> await_suspend(std::coroutine_handle<promise_type> h) noexcept {
                if (h.promise().parent_) {
                    return h.promise().parent_; // Симетричне повернення в батьківський генератор
                }
                return std::noop_coroutine();
            }
            void await_resume() noexcept {}
        };
        return final_awaiter{};
    }

    // Збереження згенерованого значення
    std::suspend_always yield_value(yielded val) noexcept {
        value_ptr_ = std::addressof(val);
        return {};
    }

    void return_void() noexcept {}

    void unhandled_exception() {
        exception_ = std::current_exception();
    }

    // Підтримка користувацького розподілювача пам'яті
    template<class... Args>
    static void* operator new(std::size_t size, Args&&... args);
    static void operator delete(void* ptr, std::size_t size) noexcept;
private:
    std::addressof_t<yielded> value_ptr_{nullptr};
    std::exception_ptr exception_{nullptr};
    std::coroutine_handle<> parent_{nullptr};
};
```

---

## 7. Робота з користувацькими розподілювачами пам'яті (Allocators)

Шаблон `std::generator` підтримує передачу користувацьких розподілювачів пам'яті (наприклад, `std::pmr::polymorphic_allocator`) через аргумент `std::allocator_arg`.

```cpp
#include <generator>
#include <memory_resource>
#include <iostream>

// Корутинна функція з користувацьким PMR розподілювачем
std::generator<int, void, std::pmr::polymorphic_allocator<char>>
custom_allocated_sequence(std::allocator_arg_t, std::pmr::polymorphic_allocator<char> alloc, int count) {
    for (int i = 0; i < count; ++i) {
        co_yield i;
    }
}

int main() {
    // Створюємо логічну арену пам'яті на стеку
    char buffer[1024];
    std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));
    std::pmr::polymorphic_allocator<char> alloc(&pool);

    // Передаємо розподілювач першим аргументом через std::allocator_arg
    auto gen = custom_allocated_sequence(std::allocator_arg, alloc, 5);

    for (int v : gen) {
        std::cout << v << " "; // Виділення кадру відбувається в буфері 'buffer'
    }
}
```

---

## 8. Анатомія збереження значень у купі та обробка винятків

Особливою перевагою архітектури `std::generator` є захист від витоків пам'яті під час генерації елементів. Якщо всередині тіла корутини виконується операція, яка кидає виняток (наприклад, недійсний парсинг рядка чи помилка читання з диска), система не перериває виконання вільним виходом.

Замість цього внутрішній перехоплювач `unhandled_exception()` зберігає поточний виняток у полі `std::exception_ptr`. Коли викликач на наступному кроці ітерації намагається виконати `++it` або прочитати значення `*it`, збережений виняток виринає безпосередньо у контексті викликача. Це дозволяє використовувати стандартні блоки `try-catch` навколо циклів `for (auto val : gen)`, гарантуючи коректну роботу гарантій безпеки винятків (Exception Safety Guarantees).

Деструктор кадру корутини гарантує, що при появі винятку всі створені у тілі корутини локальні об'єкти знищуються у зворотному порядку їх конструювання. Це захищає ресурси від витоків навіть при аварійному перериванні генератора.

---

## 9. Крайові випадки та невизначена поведінка (Edge Cases & Undefined Behavior)

Для гарантії надійності коду системний розробник повинен пам'ятати про наступні граничні умови використання `std::generator`:

1. **Невизначена поведінка при виклику на переміщеному генераторі:** Спроба викликати метод `begin()` або розіменувати ітератор об'єкта `std::generator`, з якого вже було здійснено переміщення через `std::move()`, є невизначеною поведінкою. Переміщений генератор містить `coroutine_ == nullptr`.
2. **Пастка рекурсивного ітерування одного об'єкта:** Спроба одночасно ітеруватися двома незалежними циклами по одному об'єкту `std::generator` є некоректною. Перший цикл повністю вичерпає стан корутини, після чого дескриптор перейде у стан `done() == true`. Другий цикл одразу отримає порожній діапазон.
3. **Висячі посилання при генерації тимчасових об'єктів:** Якщо генератор оголошено з посилальним типом `std::generator<const std::string&>`, оператор `co_yield` повинен віддавати посилання на об'єкт, який живе всередині корутини або у батьківському контексті. Спроба зробити `co_yield std::to_string(42)` з посилальним типом `Ref = const std::string&` збереже у кадрі посилання на тимчасовий рядок, який помирає наприкінці виразу `co_yield`. Це призведе до висячого посилання (Dangling Reference) та зчитування сміття з пам'яті при виконанні `*it`.

---

## 10. Підтримка компіляторами та прапорці збірки

| Компілятор / Заголовок | Мінімальна версія | Прапорці збірки |
| :--- | :--- | :--- |
| **GCC (libstdc++)** | GCC 14.1+ | `-std=c++23` або `-std=c++2b` |
| **Clang (libc++)** | Clang 17.0+ (з `libc++`) | `-std=c++23 -stdlib=libc++` |
| **MSVC (MSVC STL)** | Visual Studio 2022 v17.6+ | `/std:c++latest` або `/std:c++23` |
