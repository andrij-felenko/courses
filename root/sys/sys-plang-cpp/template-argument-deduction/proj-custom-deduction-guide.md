# ⚙️ Практична реалізація ідіоми Overloaded та користувацьких deduction guides

Коли розробник створює узагальнені контейнери, диспетчери обробки подій для `std::variant` або системні буфери фіксованого розміру для вбудованих систем реального часу, стандартного автоматичного синтезу кандидатів виведення з конструкторів класу виявляється недостатньо. Конструктори можуть приймати ітератори замість самих елементів, приймати масиви зі збереженням їхнього статичного розміру або вимагати агрегації довільної кількості лямбда-виразів у єдиний функціональний об'єкт без втрати інформації про типи.

Для вирішення цих завдань у сучасному C++ застосовують користувацькі керівні правила виведення (User-defined Deduction Guides) у поєднанні з передавальними посиланнями, пакетами параметрів та недедукованими контекстами. Нижче розглянуто покрокову розробку системних компонентів, діагностику помилок компіляції та профілювання накладних витрат на етапі збірки:
1. Диспетчера зіставлення зразків `Overloaded` для поліморфної обробки типів у `std::variant`.
2. Статичного кільцевого буфера `StaticRingBuffer` з виведенням місткості з сирих C-масивів та пар ітераторів.
3. Багатовимірної матриці `FixedMatrix` з автоматичним обчисленням розмірностей із вкладених списків ініціалізації.
4. Диспетчера підписки на події `EventObserver` з виведенням типів методів класів.
5. Асинхронної задачі пулу потоків `ThreadPoolTask` з виведенням типів результатів виклику через `std::invoke_result_t`.
6. Алокатор-орієнтованого потокобезпечного кеша `ThreadSafeCache` із захистом від неоднозначного виведення за допомогою `std::type_identity`.

## Шаблон 1: Диспетчер зіставлення зразків Overloaded для std::variant

Типовим завданням у функціональному та системному дизайні є обробка значень типу `std::variant`. Для відвідування варіанта через `std::visit` стандартна бібліотека очікує єдиний функтор, що містить перевантажені версії `operator()` для кожного можливого типу, що зберігається у варіанті.

Написання окремого класу вручну вимагає створення структури з десятком методів `operator()`, що порушує локальність коду та змушує дублювати логіку обробки. Якщо у проєкті є десятки різних викликів `std::visit`, створення іменованих класів-відвідувачів призводить до захаращення кодової бази дрібними структурами-одноденками.

Замість цього розробники використовують ідіому `Overloaded`. Вона базується на множинному успадкуванні від списку безіменних лямбда-виразів, які передаються безпосередньо за місцем виклику:

```cpp
#include <iostream>
#include <variant>
#include <string>
#include <concepts>
#include <type_traits>

// Базовий шаблон зі змінною кількістю аргументів (Variadic Template)
template<typename... Ts>
struct Overloaded : Ts... {
    using Ts::operator()...; // Розпакування using-оголошень для всіх базових класів (C++17)
};

// Користувацьке правило виведення (Deduction Guide)
template<typename... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;
```

### Покроковий механізм виведення типів для Overloaded

Розглянемо в деталях кожен внутрішній крок, який виконує компілятор C++ під час створення та інстанціації об'єкта `Overloaded`:

1. **Генерація типів лямбда-виразів.** Програміст записує вираз створення диспетчера:
   ```cpp
   auto visitor = Overloaded{
       [](int x) { std::cout << "Ціле число: " << x << '\n'; },
       [](double d) { std::cout << "Дійсне число: " << d << '\n'; },
       [](const std::string& s) { std::cout << "Текстовий рядок: " << s << '\n'; }
   };
   ```
   Кожна безіменна лямбда у мові C++ є унікальним анонімним функціональним класом із власним згенерованим оператором виклику `operator()`. Позначимо ці типи як `L1`, `L2` та `L3`.

2. **Пошук правил виведення для класу.** Оскільки в коді вказано ім'я шаблону `Overloaded` без кутових дужок `<...>`, компілятор активує алгоритм Class Template Argument Deduction (CTAD). У структурі `Overloaded` немає жодного явно оголошеного конструктора, тому компілятор не може побудувати неявних кандидатів на основі конструкторів. Він знаходить користувацький Deduction Guide:
   `template<typename... Ts> Overloaded(Ts...) -> Overloaded<Ts...>;`.

3. **Зіставлення параметрів.** Фактичні типи аргументів `(L1, L2, L3)` порівнюються з формою формальних параметрів `(Ts...)`. Компілятор виводить пакет параметрів: `Ts = {L1, L2, L3}`.

4. **Синтез спеціалізації класу.** Відбувається підстановка виведеного пакета типів у первинний шаблон:
   `struct Overloaded<L1, L2, L3> : L1, L2, L3`.

5. **Об'єднання просторів перевантаження.** Завдяки пакетному using-оголошенню `using Ts::operator()...;`, яке з'явилося у стандарті C++17, оператори виклику `L1::operator()`, `L2::operator()` та `L3::operator()` потрапляють в одну спільну область видимості новоствореного класу.

Приклад повноцінного використання з `std::variant`:

```cpp
void run_variant_dispatcher() {
    using Message = std::variant<int, double, std::string>;

    Message msg1 = 42;
    Message msg2 = 3.14159;
    Message msg3 = std::string("Системна подія #104");

    auto handler = Overloaded{
        [](int val) {
            std::cout << "[Обробник Int]: значення = " << val << '\n';
        },
        [](double val) {
            std::cout << "[Обробник Double]: значення = " << val << '\n';
        },
        [](const std::string& val) {
            std::cout << "[Обробник String]: довжина = " << val.length() 
                      << ", вміст = " << val << '\n';
        }
    };

    std::visit(handler, msg1);
    std::visit(handler, msg2);
    std::visit(handler, msg3);
}
```

Без явно вказаного deduction guide механізм CTAD у стандарті C++17 завершився б помилкою збірки, оскільки компілятор не зміг би зв'язати аргументи ініціалізації з типами базових класів агрегату.

## Шаблон 2: Статичний кільцевий буфер StaticRingBuffer

У критичних затримках вбудованих систем, ядрах операційних систем та драйверах пристроїв динамічне виділення пам'яті в купі (heap allocation) категорично заборонено через загрозу недетермінованих затримок і фрагментації пам'яті. Потрібен кільцевий буфер фіксованого розміру, місткість якого є константою компіляції `Capacity`.

Проблема звичайних функцій полягає в тому, що передача масиву за значенням призводить до деградації типу (Array-to-pointer decay): масив `int[16]` розпадається у звичайний покажчик `int*`, втрачаючи статичний розмір 16. Щоб зберегти розмір масиву у типі контейнера, необхідне правило виведення, що приймає аргумент за посиланням на масив.

Нижче наведено реалізацію `StaticRingBuffer`, що самостійно дедукує тип `T` та місткість `Capacity`:

```cpp
#include <cstddef>
#include <array>
#include <iterator>
#include <type_traits>
#include <stdexcept>
#include <iostream>
#include <concepts>

template<typename T, std::size_t Capacity>
class StaticRingBuffer {
public:
    static_assert(Capacity > 0, "Місткість буфера повинна бути більшою за нуль!");

    using value_type = T;
    using size_type = std::size_t;

    constexpr StaticRingBuffer() noexcept = default;

    // Конструктор 1: із фіксованого масиву
    constexpr explicit StaticRingBuffer(const T (&arr)[Capacity]) {
        for (std::size_t i = 0; i < Capacity; ++i) {
            push_back(arr[i]);
        }
    }

    // Конструктор 2: із пари ітераторів
    template<std::input_iterator Iter>
    constexpr StaticRingBuffer(Iter first, Iter last) {
        while (first != last && m_size < Capacity) {
            push_back(*first);
            ++first;
        }
    }

    // Конструктор 3: зі списку ініціалізації
    constexpr explicit StaticRingBuffer(std::initializer_list<T> list) {
        if (list.size() > Capacity) {
            throw std::out_of_range("Розмір списку ініціалізації перевищує місткість буфера");
        }
        for (const auto& item : list) {
            push_back(item);
        }
    }

    constexpr bool push_back(const T& val) {
        if (m_size >= Capacity) {
            return false; // Буфер заповнений
        }
        m_data[(m_head + m_size) % Capacity] = val;
        ++m_size;
        return true;
    }

    constexpr bool pop_front(T& out_val) {
        if (m_size == 0) {
            return false; // Буфер порожній
        }
        out_val = m_data[m_head];
        m_head = (m_head + 1) % Capacity;
        --m_size;
        return true;
    }

    [[nodiscard]] constexpr size_type size() const noexcept { return m_size; }
    [[nodiscard]] constexpr size_type capacity() const noexcept { return Capacity; }
    [[nodiscard]] constexpr bool empty() const noexcept { return m_size == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return m_size == Capacity; }

    [[nodiscard]] constexpr const T& operator[](size_type idx) const {
        if (idx >= m_size) {
            throw std::out_of_range("Індекс виходить за межі заповненого буфера");
        }
        return m_data[(m_head + idx) % Capacity];
    }

private:
    std::array<T, Capacity> m_data{};
    std::size_t m_head = 0;
    std::size_t m_size = 0;
};

// -----------------------------------------------------------------------------
// Керівні правила виведення (Deduction Guides)
// -----------------------------------------------------------------------------

// Правило 1: Виведення типу T та точного розміру N із C-масиву за посиланням
template<typename T, std::size_t N>
StaticRingBuffer(const T (&)[N]) -> StaticRingBuffer<std::decay_t<T>, N>;

// Правило 2: Виведення типу елемента з ітераторів (місткість за замовчуванням = 64)
template<std::input_iterator Iter>
StaticRingBuffer(Iter, Iter) 
    -> StaticRingBuffer<typename std::iterator_traits<Iter>::value_type, 64>;

// Правило 3: Виведення зі списку ініціалізації (місткість за замовчуванням = 32)
template<typename T>
StaticRingBuffer(std::initializer_list<T>) -> StaticRingBuffer<T, 32>;
```

### Механіка зв'язування за посиланням на масив

Розглянемо, чому правило `template<typename T, std::size_t N> StaticRingBuffer(const T (&)[N]) -> StaticRingBuffer<std::decay_t<T>, N>;` зберігає розмір масиву.

Коли у звичайну функцію передається масив, параметр за значенням не зберігає інформацію про межі виділеної пам'яті. Але коли параметр оформлено як посилання на масив `const T (&)[N]`, стандарт C++ забороняє розпад типу. Компілятор виконує зіставлення структури типів:
- Тип фактичного аргументу: `double[4]`.
- Шаблон параметра у правилі виведення: `const T (&)[N]`.
- Результат структурного вирівнювання: `T = double`, `N = 4`.

У результаті клас інстанціюється як `StaticRingBuffer<double, 4>`, виділяючи рівно 32 байти пам'яті без жодного байта у динамічній купі.

```cpp
void test_static_ring_buffer() {
    // 1. Ініціалізація з масиву: T = double, Capacity = 4
    double raw_sensor_data[] = {23.4, 24.1, 23.9, 25.0};
    StaticRingBuffer buffer(raw_sensor_data);

    static_assert(buffer.capacity() == 4, "Місткість повинна бути обчислена точно як 4");
    std::cout << "Створено буфер місткістю " << buffer.capacity() 
              << ", перший елемент: " << buffer[0] << '\n';

    // 2. Ініціалізація списком: T = int, Capacity = 32
    StaticRingBuffer init_buffer = {100, 200, 300};
    static_assert(init_buffer.capacity() == 32, "Дефолтна місткість списку = 32");

    // 3. Ініціалізація ітераторами: T = double, Capacity = 64
    StaticRingBuffer iter_buffer(std::begin(raw_sensor_data), std::end(raw_sensor_data));
    static_assert(iter_buffer.capacity() == 64, "Дефолтна місткість ітераторів = 64");
}
```

## Шаблон 3: Багатовимірна матриця FixedMatrix із виведенням розмірностей

У лінійній алгебрі, обробці тривимірної графіки та системах комп'ютерного зору матриці фіксованого розміру повинні зберігатися у неперервній пам'яті зі строго фіксованими під час компіляції розмірностями рядків та стовпчиків `Rows × Cols`.

Якщо ініціалізувати матрицю вкладеними двовимірними C-масивами, виведення обох констант `Rows` та `Cols` разом із типом скаляра `T` вимагає дворівневого зіставлення посилань на масиви:

```cpp
#include <cstddef>
#include <array>
#include <iostream>
#include <type_traits>

template<typename T, std::size_t Rows, std::size_t Cols>
class FixedMatrix {
public:
    static_assert(Rows > 0 && Cols > 0, "Розміри матриці повинні бути більшими за 0!");

    // Конструктор із 2D-масиву посилань
    constexpr explicit FixedMatrix(const T (&arr)[Rows][Cols]) {
        for (std::size_t r = 0; r < Rows; ++r) {
            for (std::size_t c = 0; c < Cols; ++c) {
                m_data[r * Cols + c] = arr[r][c];
            }
        }
    }

    [[nodiscard]] constexpr std::size_t rows() const noexcept { return Rows; }
    [[nodiscard]] constexpr std::size_t cols() const noexcept { return Cols; }

    [[nodiscard]] constexpr const T& at(std::size_t r, std::size_t c) const {
        return m_data[r * Cols + c];
    }

    void print() const {
        for (std::size_t r = 0; r < Rows; ++r) {
            std::cout << "[ ";
            for (std::size_t c = 0; c < Cols; ++c) {
                std::cout << at(r, c) << ' ';
            }
            std::cout << "]\n";
        }
    }

private:
    std::array<T, Rows * Cols> m_data{};
};

// Керівне правило виведення для 2D-масивів
template<typename T, std::size_t Rows, std::size_t Cols>
FixedMatrix(const T (&)[Rows][Cols]) -> FixedMatrix<std::decay_t<T>, Rows, Cols>;
```

### Як компілятор аналізує вкладені масиви

Коли програміст передає масив:
```cpp
float transform_matrix[3][3] = {
    {1.0f, 0.0f, 0.0f},
    {0.0f, 1.0f, 0.0f},
    {0.0f, 0.0f, 1.0f}
};
FixedMatrix mat(transform_matrix);
```

Компілятор бачить тип аргументу як `float[3][3]`. Структурне зіставлення з шаблоном `const T (&)[Rows][Cols]` дедукує:
- `T = float`
- `Rows = 3`
- `Cols = 3`

Утиліта `std::decay_t<T>` гарантує зняття можливих кваліфікаторів `const`, дозволяючи створити внутрішній масив `std::array<float, 9>` із лінійним розміщенням у пам'яті для кеш-локальності та векторизації SIMD.

## Шаблон 4: Диспетчер підписки на події EventObserver

У подієво-орієнтованих архітектурах (GUI-фреймворках, мережевих серверах, рушіях ігор) часто створюють об'єкти підписки, які прив'язують вказівник на метод класу-одержувача до екземпляра цього класу.

Якщо писати шаблон `EventObserver<Class, ReturnType, Args...>` без deduction guides, виклик вимагає вказівки повного типу класу та сигнатури методу:
`EventObserver<AudioEngine, void, int, float> obs(&AudioEngine::on_event, &engine);`.

Завдяки спеціалізованому правилу виведення для покажчиків на методи класів, компілятор самостійно розбирає сигнатуру методу на складові типи:

```cpp
#include <iostream>
#include <functional>
#include <type_traits>

template<typename Receiver, typename ReturnType, typename... Args>
class EventObserver {
public:
    using MethodPtr = ReturnType (Receiver::*)(Args...);

    EventObserver(MethodPtr method, Receiver* instance)
        : m_method(method), m_instance(instance) {}

    ReturnType trigger(Args... args) const {
        if (m_instance && m_method) {
            return (m_instance->*m_method)(std::forward<Args>(args)...);
        }
        if constexpr (!std::is_void_v<ReturnType>) {
            return ReturnType{};
        }
    }

private:
    MethodPtr m_method = nullptr;
    Receiver* m_instance = nullptr;
};

// -----------------------------------------------------------------------------
// Керівне правило виведення для покажчиків на методи
// -----------------------------------------------------------------------------

template<typename Receiver, typename ReturnType, typename... Args>
EventObserver(ReturnType (Receiver::*)(Args...), Receiver*)
    -> EventObserver<Receiver, ReturnType, Args...>;
```

### Як компілятор розбирає сигнатуру покажчика на метод

Коли розробник викликає конструктор:
```cpp
struct TelemetryLogger {
    void log_status(int code, double latency) {
        std::cout << "[Telemetry] Код: " << code << ", Затримка: " << latency << " мс\n";
    }
};

void test_event_observer() {
    TelemetryLogger logger;
    // CTAD автоматично виводить: Receiver = TelemetryLogger, ReturnType = void, Args = {int, double}
    EventObserver observer(&TelemetryLogger::log_status, &logger);

    observer.trigger(200, 1.45);
}
```

Компілятор зіставляє тип аргументу `&TelemetryLogger::log_status` (який є `void (TelemetryLogger::*)(int, double)`) із формою `ReturnType (Receiver::*)(Args...)`. Механізм зіставлення виділяє тип класу `Receiver = TelemetryLogger`, повертаний тип `ReturnType = void` та розгортає пакет параметрів `Args = {int, double}`. У клієнтському коді повністю зникають громіздкі кутові дужки.

## Шаблон 5: Асинхронна задача ThreadPoolTask із виведенням invoke_result

У багатопотокових бібліотеках диспетчеризації завдань (Task Graphs, Work Stealing Thread Pools) задача повинна обгортати довільний функтор або лямбда-вираз, зберігаючи тип результату обчислення `std::invoke_result_t<Callable, Args...>`.

Створення обгортки завдання без явних параметрів шаблону вимагає координації між типом функтора та типами переданих аргументів:

```cpp
#include <iostream>
#include <functional>
#include <future>
#include <type_traits>
#include <tuple>

template<typename Callable, typename... Args>
class ThreadPoolTask {
public:
    using return_type = std::invoke_result_t<Callable, Args...>;

    explicit ThreadPoolTask(Callable fn, Args... args)
        : m_func(std::move(fn)), m_args(std::move(args)...) {}

    return_type execute() {
        return std::apply(m_func, m_args);
    }

private:
    Callable m_func;
    std::tuple<Args...> m_args;
};

// Керівне правило виведення для обгортки завдання
template<typename Callable, typename... Args>
ThreadPoolTask(Callable, Args...) 
    -> ThreadPoolTask<std::decay_t<Callable>, std::decay_t<Args>...>;
```

Утиліта `std::decay_t` для кожного аргументу в пакеті `Args...` гарантує, що передані константні посилання або масиви перетворюються на типи, безпечні для асинхронного збереження всередині `std::tuple`.

## Шаблон 6: Алокатор-орієнтований кеш та недедуковані контексти

У бібліотеках високопродуктивних структур даних часто виникає ситуація, коли клас має кілька незалежних параметрів: тип ключа `Key`, тип значення `Value`, тип компаратора `Compare` та тип алокатора пам'яті `Alloc`.

Розглянемо клас `ThreadSafeCache`, де конструктор приймає початковий ключ, початкове значення та необов'язковий об'єкт алокатора. Якщо користувач передає значення, тип якого потребує неявного перетворення (наприклад, строковий літерал `"primary_node"` замість `std::string`), наївне виведення типів призведе до конфліктів або створить спеціалізацію з типом `const char[13]`.

Для вирішення цієї проблеми застосовують комбінацію `std::decay_t`, `std::type_identity_t` та явних специфікаторів `explicit`:

```cpp
#include <memory>
#include <string>
#include <string_view>
#include <mutex>
#include <type_traits>
#include <iostream>

template<
    typename Key, 
    typename Value, 
    typename Alloc = std::allocator<std::pair<const Key, Value>>
>
class ThreadSafeCache {
public:
    using key_type = Key;
    using mapped_type = Value;
    using allocator_type = Alloc;

    // Конструктор за замовчуванням
    explicit ThreadSafeCache(const Alloc& alloc = Alloc{})
        : m_alloc(alloc) {}

    // Конструктор з ініціалізацією першого запису
    ThreadSafeCache(Key key, Value val, const Alloc& alloc = Alloc{})
        : m_last_key(std::move(key)), m_last_value(std::move(val)), m_alloc(alloc) {}

    // Метод оновлення: type_identity_t блокує виведення Value з другого аргументу,
    // дозволяючи неявне приведення типів аргументу до вже відомого типу Value
    void update_value(const Key& key, std::type_identity_t<Value> val) {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_last_key = key;
        m_last_value = std::move(val);
    }

    void dump_state() const {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::cout << "[Cache State] Ключ: " << m_last_key 
                  << ", Значення: " << m_last_value << '\n';
    }

private:
    Key m_last_key{};
    Value m_last_value{};
    Alloc m_alloc{};
    mutable std::mutex m_mutex{};
};

// -----------------------------------------------------------------------------
// Керівне правило виведення (Deduction Guide)
// -----------------------------------------------------------------------------

template<
    typename Key, 
    typename Value, 
    typename Alloc = std::allocator<std::pair<const std::decay_t<Key>, std::decay_t<Value>>>>
ThreadSafeCache(Key&&, Value&&, Alloc = Alloc{}) 
    -> ThreadSafeCache<std::decay_t<Key>, std::decay_t<Value>, Alloc>;
```

### Чому необхідний std::decay_t у Deduction Guide

Якщо передати у конструктор вираз:
`ThreadSafeCache cache("primary_node", 9999);`

Типом першого аргументу є строковий літерал `const char[13]`. Без використання `std::decay_t` компілятор синтезував би спеціалізацію:
`ThreadSafeCache<const char[13], int>`

Спроба зберегти поле типу масиву `const char[13]` всередині класу призведе до помилки компіляції під час спроби копіювання чи присвоєння, оскільки масиви в мові C++ не можна копіювати через вбудований оператор присвоєння `=`. Застосування `std::decay_t<Key>` у керівному правилі перетворює `const char[13]` на покажчик `const char*`, забезпечуючи коректне копіювання значень у внутрішні поля структури.

## Діагностика типових помилок та аналіз повідомлень компілятора

Під час реалізації користувацьких правил виведення розробники найчастіше стикаються з п'ятьма критичними категоріями помилок збірки.

### 1. Неоднозначність кандидатів виведення (Ambiguity in Overload Resolution)

Розглянемо випадок, коли клас має конструктор для одного покажчика і конструктор для скалярного значення:

```cpp
template<typename T>
struct SmartHandle {
    SmartHandle(T val);
    SmartHandle(T* ptr);
};

// Помилкове керівне правило без розрізнення покажчиків:
template<typename U>
SmartHandle(U*) -> SmartHandle<U*>;
```

Якщо викликати `SmartHandle h(nullptr);`, компілятор зустрічає два однаково підходящі кандидати:
- Неявний кандидат з першого конструктора: `T = std::nullptr_t` -> `SmartHandle<std::nullptr_t>`.
- Явний кандидат з deduction guide: `U* = nullptr` -> `SmartHandle<std::nullptr_t*>`.

Компілятор GCC видає детальне повідомлення про помилку:
```text
error: class template argument deduction failed:
error: call of overloaded 'SmartHandle(std::nullptr_t)' is ambiguous
note: candidate 1: SmartHandle<T>::SmartHandle(T) [with T = std::nullptr_t]
note: candidate 2: SmartHandle<U*>::SmartHandle(U*) [with U = std::nullptr_t]
```

*Як усунути:* Використовувати обмеження концептами (Concepts `requires`), щоб явно виключити конфліктні типи з набору перевантажень:

```cpp
template<typename U>
requires (!std::is_null_pointer_v<U>)
SmartHandle(U*) -> SmartHandle<U*>;
```

### 2. Специфікатор explicit у правилах виведення

Правила виведення можуть мати кваліфікатор `explicit`. Це вкрай важливо для класів, чиї конструктори є `explicit`.

Якщо конструктор позначений як `explicit`, але deduction guide оголошено без `explicit`, виникає аномалія: виведення типів спрацьовує під час неявної копіювальної ініціалізації, проте наступний виклик конструктора відхиляється:

```cpp
template<typename T>
struct SafeBuffer {
    explicit SafeBuffer(T size);
};

// Правильне узгоджене керівне правило з explicit
template<typename T>
explicit SafeBuffer(T) -> SafeBuffer<T>;
```

Тепер запис `SafeBuffer buf = 100;` буде коректно відхилений компілятором ще на етапі вибору форми ініціалізації, тоді як пряма ініціалізація `SafeBuffer buf(100);` спрацює бездоганно.

### 3. Приховування копіювального конструктора списком ініціалізації

У стандарті C++17 існує спеціальне правило розв'язання конфлікту між конструктором копіювання/переміщення та конструктором зі списком ініціалізації:

```cpp
std::vector v1{1, 2, 3};

// Створюється std::vector<int> через виклик конструктора копіювання,
// а НЕ std::vector<std::vector<int>> з одним елементом!
std::vector v2{v1};

// Створюється std::vector<std::vector<int>>, оскільки аргументів більше одного
std::vector v3{v1, v1};
```

Компілятор гарантує, що якщо список ініціалізації складається рівно з одного аргументу, тип якого повністю збігається з типом спеціалізації класу, перевага завжди надається копіюванню, що рятує програми від випадкового створення вкладених контейнерів.

### 4. Несумісність типів у дедукованих контекстах кількох аргументів

Якщо функція або конструктор приймають кілька параметрів однакового типу `template<typename T> void process(T a, T b)`, виклик `process(10, 3.14)` призводить до помилки компіляції:
`error: deduced conflicting types for parameter 'T' ('int' and 'double')`.

Компілятор C++ принципово не виконує стандартні неявні перетворення типів під час виведення параметрів шаблону. Щоб дозволити неявне перетворення одного з аргументів, слід використати недедукований контекст `std::type_identity_t`:

```cpp
template<typename T>
void process_flexible(T primary, std::type_identity_t<T> fallback) {
    // Тип T визначається виключно за першим аргументом,
    // а другий аргумент неявно приводиться до T
}
```

### 5. Помилка дедукції для вкладених залежних типів

Спроба вивести тип-параметр через залежний тип `typename Container::value_type` завжди завершується невдачею, якщо компілятор не має прямого правила зіставлення:

```cpp
template<typename T>
void extract(typename std::vector<T>::iterator it); // Недедукований контекст!

// extract(vec.begin()); // ПОМИЛКА: компілятор не може вивести T у зворотному напрямку
```

Оскільки різні спеціалізації `std::vector` теоретично могли б мати однаковий тип `iterator` (наприклад, сирий вказівник `typedef int* iterator`), компілятор не має математичної гарантії однозначності зворотного відображення типу. Для вирішення цієї проблеми шаблон параметризують типом самого ітератора: `template<typename Iter> void extract(Iter it);` та витягують тип значення через `std::iterator_traits<Iter>::value_type`.

## Архітектурні правила проектування надійних Deduction Guides

Щоб уникнути несподіваних помилок компіляції та неоднозначностей у великих проєктах, під час створення власних правил виведення слід дотримуватися чотирьох фундаментальних інженерних принципів:

### 1. Симетрія між конструкторами та правилами виведення

Якщо клас надає конструктор, що приймає аргументи за значенням `Widget(T val)`, але неявний синтез кандидатів CTAD не охоплює деякі типи перетворень, явний deduction guide повинен відтворювати поведінку конструктора, включаючи застосування `std::decay_t` або зняття константності. Неузгодженість між правилом виведення та конструктором призводить до того, що компілятор успішно обирає тип класу під час дедукції, але зазнає невдачі на наступному кроці ініціалізації тіла об'єкта.

### 2. Завжди застосовуйте std::decay_t для передачі за значенням

Коли правило виведення створюється для збереження копій об'єктів усередині контейнера, параметри правила повинні трансформуватися через `std::decay_t`. Це запобігає випадковому створенню класів із типами масивів `char[N]`, функцій або надлишкових посилань, гарантуючи, що екземпляр класу завжди містить коректні, самодостатні типи значень.

### 3. Захищайте залежні типи через концептуальні обмеження

Якщо deduction guide оперує ітераторами або діапазонами, обов'язково обмежуйте типи за допомогою концептів стандарту C++20 (наприклад, `std::input_iterator` або `std::ranges::range`) або перевірок `std::is_constructible_v`. Без таких обмежень керівне правило може брати участь у виборі перевантаження для зовсім сторонніх типів (наприклад, цілих чисел, які випадково підходять під сигнатуру з двома аргументами), блокуючи роботу стандартних конструкторів.

### 4. Використовуйте explicit для блокування прихованих конверсій

Якщо конструктор позначений специфікатором `explicit`, відповідний deduction guide обов'язково повинен містити `explicit`. Це блокує випадкову ініціалізацію копіюванням через оператор присвоєння `=` і змушує розробника явно викликати пряму ініціалізацію з круглими або фігурними дужками.

## Вплив на час компіляції та профілювання збірки

Використання CTAD та користувацьких правил виведення переносить частину синтаксичного аналізу на етап побудови набору кандидатів перевантаження. Під час компіляції великих проєктів виникає закономірне питання: скільки коштує активне використання керівних правил для компілятора?

За допомогою інструменту Clang `-ftime-trace` (або прапорця GCC `-ftime-report`) можна відстежити час, витрачений на кожну фазу інстанціації:

1. **Фаза синтезу кандидатів (Candidate Synthesis):** Компілятор створює внутрішні представлення уявних функцій для кожного конструктора первинного шаблону та кожного явного deduction guide. Для класу з п'ятьма конструкторами та двома deduction guides компілятор генерує набір із 7 функцій-кандидатів. Оскільки ці функції генеруються лише в пам'яті AST і не вимагають генерації коду об'єктного файлу, їхній внесок у час компіляції становить менше 2–4 мікросекунд на точку виклику.
2. **Фаза вибору перевантаження (Overload Resolution):** Звичайний вибір перевантаження функцій оптимізовано в сучасних компіляторах на рівні бінарних дерев хешування типів.
3. **Економія на проміжних інстанціаціях:** Порівняно зі старими фабричними функціями на кшталт `std::make_pair`, CTAD створює безпосередньо цільовий об'єкт класу без необхідності парсингу додаткових шаблонів функцій-обгорток, що знижує глибину стеку інстанціації компілятора на один рівень і зменшує споживання пам'яті компілятора на 15–20% у шаблоно-інтенсивних модулях. Завдяки цьому сучасний C++ код із CTAD компілюється швидше та споживає менше ресурсів пам'яті компілятора, ніж еквівалентний код на базі фабрик C++98/C++03. Глибоке розуміння та правильне практичне застосування цих інструментів дозволяє створювати надійні, високопродуктивні архітектурні рішення у масштабних промислових проєктах.

## Тестування та верифікація правил виведення у CI/CD

Для гарантії стабільності поведінки бібліотеки всі користувацькі правила виведення рекомендується покривати модульними тестами з використанням `static_assert` та `std::is_same_v`. Це дозволяє перехоплювати регресії ще на етапі компіляції тестового набору без запуску виконуваного файлу:

```cpp
void verify_deduction_invariants() {
    double data[] = {1.0, 2.0, 3.0};
    StaticRingBuffer buf(data);
    static_assert(std::is_same_v<decltype(buf), StaticRingBuffer<double, 3>>, 
                  "Помилка виведення типу або місткості для StaticRingBuffer!");
}
```
