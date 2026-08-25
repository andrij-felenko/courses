# 📋 Довідник нововведень стандарту C++17: мова, бібліотека та макроси

Стандарт C++17 (ISO/IEC 14882:2017) суттєво розширив синтаксичні можливості ядра мови, оптимізував метапрограмування на етапі компіляції та надав багатий набір уніфікованих словникових типів і паралельних алгоритмів у стандартній бібліотеці. Нижче наведено повний структурований довідник нововведень із сигнатурами, правилами використання, таблицями сумісності, інваріантами виконання та макросами перевірки можливостей.

## 1. Нововведення ядра мови (Core Language Features)

### 1.1. Структуровані прив'язки (Structured Bindings)

Синтаксис дозволяє розпаковувати складені об'єкти безпосередньо у нові змінні-псевдоніми без використання макроподібних викликів `std::tie` та без ручного звернення до полів `.first` чи `.second`:

```cpp
auto [a, b, c] = expression;
const auto& [x, y] = expression;
auto&& [r1, r2] = expression;
```

#### Три протоколи розв'язання компілятором

Компілятор утворює прихований базовий об'єкт `e`, що є результатом обчислення виразу, і прив'язує кожне оголошене ім'я за одним із трьох чітких механізмів:

1. **Масиви фіксованого розміру (`std::is_array_v<E>`):**
   Кількість оголошених змінних у квадратних дужках мусить точно збігатися з кількістю елементів масиву. Кожне ім'я стає lvalue-посиланням на відповідний елемент `e[i]`.
2. **Tuple-подібний протокол (Tuple-like Protocol):**
   Застосовується до типів, для яких оголошено спеціалізації шаблонів розміру та елементів:
   * Наявна валідна спеціалізація `std::tuple_size<E>::value`, де числове значення точно дорівнює кількості імен у прив'язці;
   * Наявні спеціалізації `std::tuple_element<I, E>::type` для кожного індексу `I` від `0` до `N-1`;
   * Доступна функція або метод вилучення `get<I>(e)`. Компілятор шукає метод `e.get<I>()` у тілі класу, а якщо він відсутній — викликає вільну функцію `get<I>(e)` через механізм пошуку, залежного від аргументів (Argument-Dependent Lookup, ADL).
3. **Агрегатні структури з відкритими членами:**
   Застосовується, якщо перші два протоколи не спрацювали, і всі нестатичні поля даних є відкритими (`public`) безпосередньо у структурі `E`. Імена прив'язуються до полів у порядку їхнього фізичного оголошення в коді.

```cpp
// Повна реалізація користувацького Tuple-подібного протоколу:
struct Coordinate2D {
    double latitude;
    double longitude;
};

template <>
struct std::tuple_size<Coordinate2D> : std::integral_constant<std::size_t, 2> {};

template <std::size_t I>
struct std::tuple_element<I, Coordinate2D> {
    using type = double;
};

template <std::size_t I>
decltype(auto) get(const Coordinate2D& c) noexcept {
    if constexpr (I == 0) return c.latitude;
    else if constexpr (I == 1) return c.longitude;
}
```

#### Правила застосування кваліфікаторів та крайові обмеження

Специфікатори `const`, `volatile`, `&`, `&&` застосовуються виключно до прихованого об'єкта `e`, а не до окремих імен:
* При `auto [x, y] = obj;` створюється копія або переміщений екземпляр `e`, тому модифікація `x` не змінює поля `obj`.
* При `auto& [x, y] = obj;` об'єкт `e` стає lvalue-посиланням, тому модифікація `x` напряму оновлює внутрішнє поле об'єкта `obj`.
* При `const auto& [x, y] = obj;` прихований об'єкт прив'язується за константним посиланням, запобігаючи модифікації полів.

**Крайові випадки та обмеження:**
* **Бітові поля (Bit-fields):** прив'язка за посиланням `auto& [a, b]` до структури з бітовими полями є помилкою компіляції, оскільки в архітектурі C++ неможливо отримати пряму адресу або створити посилання на частину байта. Для бітових полів дозволена виключно прив'язка за значенням `auto [a, b]`.
* **Проксі-посилання (`std::vector<bool>`):** спроба розпакування елементів або ітераторів, що повертають проксі-об'єкти, вимагає уважності, оскільки прив'язка `auto&` не може зв'язуватися з тимчасовим проксі-значенням без специфікатора `const` або універсального посилання `auto&&`.

---

### 1.2. Інструкція if constexpr

Інструкція `if constexpr` обчислює булевий константний вираз на етапі компіляції та вилучає синтаксичне дерево неактивної гілки з процесу інстанціювання шаблону.

```cpp
template <typename T>
auto extract_value(T&& container) {
    if constexpr (std::is_pointer_v<std::decay_t<T>>) {
        return *container;
    } else {
        return container.value(); // Інстанціюється лише для непокажчикових типів
    }
}
```

#### Інваріанти та відкладені перевірки

* **Синтаксична цілісність:** код неактивної гілки проходить початковий синтаксичний розбір (parsing), тому в ньому заборонено синтаксичні помилки (пропущені дужки, некоректні ключові слова).
* **Залежні вирази:** виклики методів і операторів, які залежать від параметра шаблону `T`, не інстанціюються. Якщо тип `T = int*` не має методу `.value()`, компілятор не генерує помилку, оскільки ця гілка відкинута.
* **Відкладені твердження static_assert:** прямий виклик `static_assert(false)` у неактивній гілці викликає безумовну помилку компіляції. Для генерації помилки лише при інстанціюванні непідтримуваного типу використовується залежний трейт:

```cpp
template <typename>
inline constexpr bool dependent_false_v = false;

template <typename T>
void dispatch_operation(T val) {
    if constexpr (std::is_integral_v<T>) {
        process_integer(val);
    } else if constexpr (std::is_floating_point_v<T>) {
        process_floating(val);
    } else {
        static_assert(dependent_false_v<T>, "Тип не підтримується для dispatch_operation!");
    }
}
```

---

### 1.3. Виведення аргументів шаблонів класів (CTAD)

Дозволяє інстанціювати шаблони класів без явного перелічення параметрів типів у кутових дужках:

```cpp
std::pair p(10, 3.14);               // std::pair<int, double>
std::lock_guard lock(my_mutex);      // std::lock_guard<std::mutex>
std::vector vec = {1, 2, 3, 4};      // std::vector<int>
```

#### Користувацькі правила виведення (Deduction Guides)

Спеціальний синтаксис для інструктування компілятора щодо правил виведення типу з аргументів конструктора:

```cpp
template <typename T>
class CircularBuffer {
public:
    template <typename Iter>
    CircularBuffer(Iter first, Iter last);
};

// Явне правило виведення для ітераторів:
template <typename Iter>
CircularBuffer(Iter, Iter) -> CircularBuffer<typename std::iterator_traits<Iter>::value_type>;
```

---

### 1.4. Вирази згортки (Fold Expressions)

Вирази згортки дозволяють лаконічно застосовувати бінарні оператори до пакетів параметрів (`Args...`) без створення рекурсивних допоміжних шаблонів.

| Форма згортки | Синтаксис | Еквівалентне математичне розгортання |
| :--- | :--- | :--- |
| **Унарна права (Unary Right)** | `(args op ...)` | `(arg1 op (arg2 op ...(argN-1 op argN)))` |
| **Унарна ліва (Unary Left)** | `(... op args)` | `(((arg1 op arg2) op arg3)... op argN)` |
| **Бінарна права (Binary Right)** | `(args op ... op init)` | `(arg1 op (arg2 op ...(argN op init)))` |
| **Бінарна ліва (Binary Left)** | `(init op ... op args)` | `(((init op arg1) op arg2)... op argN)` |

#### Практичні патерни застосування

```cpp
// 1. Логічна перевірка валідності всіх аргументів
template <typename... Args>
bool all_positive(Args... args) {
    return (... && (args > 0)); // Унарна ліва згортка через оператор &&
}

// 2. Потоковий друк елементів
template <typename... Args>
void print_lines(const Args&... args) {
    ((std::cout << args << '\n'), ...); // Унарна права згортка через кому
}

// 3. Додавання елементів у вектор
template <typename T, typename... Args>
void push_many(std::vector<T>& vec, Args&&... args) {
    (vec.push_back(std::forward<Args>(args)), ...);
}
```

---

### 1.5. Гарантоване вилучення копіювання (Guaranteed Copy Elision)

Стандарт C++17 переосмислив систему категорій значень виразів:
* **prvalue (pure rvalue)** тепер позначає не тимчасовий об'єкт на стеку, а *обчислювальну інструкцію ініціалізації*.
* **Матеріалізація тимчасового об'єкта (Temporary Materialization):** створення фізичного об'єкта в пам'яті відбувається лише тоді, коли prvalue перетворюється на glvalue (прив'язується до посилання або викликається член структури).
* **Повернення за значенням:** вираз `T create() { return T(1, 2); }` виконує конструювання об'єкта безпосередньо у пам'яті, виділеній викликачем. Навіть якщо тип `T` має видалені або недоступні конструктори копіювання та переміщення (`T(T&&) = delete;`), повернення за значенням є повністю легальним.

```cpp
struct ImmovableDeviceHandle {
    explicit ImmovableDeviceHandle(int id);
    ImmovableDeviceHandle(const ImmovableDeviceHandle&) = delete;
    ImmovableDeviceHandle(ImmovableDeviceHandle&&) = delete;
};

ImmovableDeviceHandle open_device(int id) {
    return ImmovableDeviceHandle(id); // Гарантовано без копій у C++17
}

ImmovableDeviceHandle dev = open_device(101); // Пряме створення за місцем
```

---

### 1.6. Inline-змінні (Inline Variables)

Специфікатор `inline` дозволяє оголошувати глобальні та статичні змінні безпосередньо у заголовочних файлах без порушення правила одного визначення (One Definition Rule, ODR):

```cpp
// У заголовочному файлі network_constants.hpp:
inline constexpr std::string_view kDefaultHost = "127.0.0.1";
inline std::atomic<uint32_t> gActiveConnections{0};

struct NetworkSession {
    static inline const std::string session_tag = "PRODUCTION";
};
```

Лінкер об'єднує всі однойменні сутності з різних одиниць трансляції (`.cpp`) в один спільний об'єкт із єдиною адресою в пам'яті. Усі статичні члени класу, оголошені як `constexpr`, у C++17 автоматично вважаються `inline`.

---

### 1.7. Строгий порядок обчислення виразів (P0145R3)

Стандарт усунув небезпечні невизначеності у послідовності обчислення підвиразів, закріпивши такі правила:
* У виразах доступу до членів та виклику функцій `a.b`, `a->b`, `a(b1, b2)` підвираз `a` завжди обчислюється раніше за аргументи `b1, b2`.
* У виразах індексації `a[b]` підвираз `a` обчислюється строго перед `b`.
* У виразах зсуву `a << b` та `a >> b` лівий операнд `a` обчислюється строго перед правим `b`.
* В операторах присвоєння `a = b`, `a += b` правий операнд `b` обчислюється перед лівим операндом `a`.

---

### 1.8. Покращення лямбда-виразів: constexpr та захоплення *this

Стандарт C++17 розширив можливості лямбда-виразів:
* **constexpr лямбди:** якщо оператор виклику лямбда-виразу задовольняє вимогам константних виразів, він стає неявно `constexpr`. Лямбди можна явно позначати як `constexpr auto sum = [](int a, int b) constexpr { return a + b; };` і використовувати в контекстах компіляції.
* **Захоплення `*this` за значенням:** синтаксис `[*this]` копіює поточний об'єкт усередину замикання. Це усуває критичну проблему «висячого покажчика» `this` в асинхронних колбеках, коли базовий об'єкт знищується до моменту виконання відкладеного потоку.

```cpp
struct AsyncWorker {
    int task_id = 42;
    auto schedule_task() {
        // Копіює *this за значенням у замикання:
        return [*this]() {
            std::cout << "Виконання завдання " << task_id << "\n";
        };
    }
};
```

---

### 1.9. Пряма ініціалізація списком для scoped enum

У C++17 дозволено пряму ініціалізацію перелічень зі строгою типізацією (`enum class`) цілими числами базового типу без явного приведення `static_cast`:

```cpp
enum class StatusByte : uint8_t {
    Idle = 0,
    Active = 1
};

StatusByte s{1}; // Легально в C++17 (пряма ініціалізація списком)
// StatusByte err = 1; // Помилка компіляції!
```

---

## 2. Стандартні атрибути (Attributes)

| Атрибут | Область застосування | Нормативна поведінка компілятора |
| :--- | :--- | :--- |
| `[[nodiscard]]` | Функції, типи класів, перелічення `enum` | Генерує обов'язкове діагностичне попередження, якщо значення, повернуте функцією або конструктором типу, позначеного атрибутом, було проігноровано викликачем. |
| `[[maybe_unused]]` | Змінні, параметри функцій, методи, типи, поля даних | Пригнічує попередження компілятора про те, що сутність була оголошена, але не використана в коді (наприклад, у конфігураціях без налагоджувальних асертів). |
| `[[fallthrough]]` | Порожні вирази безпосередньо перед мітками `case` або `default` всередині `switch` | Інформує компілятор та статичні аналізатори про те, що перехід до наступної мітки без `break` є свідомим архітектурним рішенням, а не випадковою помилкою. |

---

## 3. Нові словникові типи стандартної бібліотеки (Vocabulary Types)

### 3.1. std::optional<T> (`<optional>`)

Контейнер для вираження наявності або відсутності значення без динамічного виділення пам'яті в купі.

#### Сигнатури та основні методи

```cpp
template <class T>
class optional {
public:
    constexpr optional() noexcept;
    constexpr optional(nullopt_t) noexcept;
    constexpr optional(const T& value);
    constexpr optional(T&& value);

    constexpr bool has_value() const noexcept;
    constexpr explicit operator bool() const noexcept;

    constexpr T& value() &; // Кидає std::bad_optional_access у разі порожнечі
    constexpr const T& value() const &;

    constexpr T& operator*() & noexcept; // Доступ без перевірки (UB, якщо порожній)
    constexpr const T* operator->() const noexcept;

    template <class U>
    constexpr T value_or(U&& default_value) const&;

    void reset() noexcept;
    template <class... Args>
    T& emplace(Args&&... args);
};
```

* **Інваріанти пам'яті:** розмір дорівнює `sizeof(T) + sizeof(bool)` з урахуванням вирівнювання типів (наприклад, для 8-байтового `double` або вказівника загальний розмір становить 16 байтів). Пам'ять резервується на стеку.
* **Порівняння:** об'єкти `std::optional` підтримують повний набір операторів порівняння (`==`, `!=`, `<`, `<=`, `>`, `>=`). Порожній стан `std::nullopt` вважається строго меншим за будь-яке наявне значення.

---

### 3.2. std::variant<Types...> (`<variant>`)

Типобезпечне розмічене об'єднання (tagged union), що містить рівно один об'єкт зі списку дозволених типів із повною семантикою значень.

#### Операції та доступ

```cpp
#include <variant>

std::variant<int, double, std::string> v = "system"s;

// 1. Перевірка активного типу
bool is_str = std::holds_alternative<std::string>(v);
std::size_t active_idx = v.index(); // Повертає 2

// 2. Отримання значення за типом або індексом
std::string& s = std::get<std::string>(v); // Кидає std::bad_variant_access при невідповідності
std::string& s2 = std::get<2>(v);

// 3. Безпечне отримання через вказівник
if (double* p = std::get_if<double>(&v)) {
    // Вказівник не nullptr, якщо активним є double
}

// 4. Патерн відвідувача через ідіому Overloaded
template <class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };
template <class... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

std::visit(overloaded {
    [](int arg) { std::cout << "int: " << arg << "\n"; },
    [](double arg) { std::cout << "double: " << arg << "\n"; },
    [](const std::string& arg) { std::cout << "string: " << arg << "\n"; }
}, v);
```

* **Стан valueless_by_exception:** якщо під час зміни типу конструктор нового значення кидає виняток, варіант переходить у стан `v.valueless_by_exception() == true`. Спроба викликати `std::get` на такому об'єкті кидає `std::bad_variant_access`.
* **Допоміжний тип `std::monostate`:** використовується як перший тип у списку варіантів, якщо типи-члени не мають конструктора за замовчуванням: `std::variant<std::monostate, NonDefaultConstructible>`.

---

### 3.3. std::any (`<any>`)

Універсальний типобезпечний контейнер для зберігання одного значення довільного копійованого типу з динамічним стиранням типу.

```cpp
#include <any>

std::any a = 42;
a = std::string("dynamically typed payload");

if (a.has_value()) {
    const std::type_info& ti = a.type(); // Інформація RTTI
    if (ti == typeid(std::string)) {
        std::string val = std::any_cast<std::string>(a);
    }
}

// Отримання через покажчик без винятків:
if (std::string* ptr = std::any_cast<std::string>(&a)) {
    std::cout << *ptr << "\n";
}
```

* **Small Object Optimization (SOO):** для невеликих об'єктів (розміром до 16–24 байтів) виділення пам'яті в купі не відбувається; дані зберігаються у внутрішньому буфері `std::any`.
* **Винятки:** виклик `std::any_cast<T>(a)` за значенням або посиланням генерує `std::bad_any_cast`, якщо збережений тип не збігається з `T`.

---

### 3.4. std::string_view (`<string_view>`)

Невласницький погляд на неперервну послідовність символів, що складається з вказівника на початок даних `const CharT*` та розміру `std::size_t`.

```cpp
#include <string_view>

constexpr std::string_view sv = "Compile-time literal slice";
constexpr std::string_view sub = sv.substr(0, 12); // Час виконання O(1), нуль виділень пам'яті

void log_message(std::string_view message) noexcept {
    // Працює з const char*, std::string та std::string_view без копіювання буфера
}
```

* **Часова складність:** взяття підрядка `.substr()`, видалення префікса `.remove_prefix(n)` та суфікса `.remove_suffix(n)` виконуються за константний час `O(1)`.
* **Небезпека висячих посилань:** `std::string_view` не володіє пам'яттю. Якщо базовий рядок `std::string` було знищено або переалоковано, звернення до `std::string_view` призводить до невизначеної поведінки (UB).
* **Контракт завершального нуля:** `std::string_view` не гарантує наявність нульового символу `\0` наприкінці буфера. Передача `sv.data()` у функції C-бібліотеки (`printf("%s")`, `fopen`) без урахування довжини є грубою помилкою безпеки.

---

### 3.5. std::byte (`<cstddef>`)

Спеціалізований тип для представлення нетипізованої сирої пам'яті:

```cpp
namespace std {
    enum class byte : unsigned char {};
}
```

* **Операції:** підтримує виключно побітові операції `&`, `|`, `^`, `~`, `<<`, `>>`.
* **Безпека:** забороняє випадкові арифметичні операції `+`, `-`, захищаючи системний код від плутанини між масивами байтів, числовими значеннями та рядковими символами `char`.

---

## 4. Файлова система: std::filesystem (`<filesystem>`)

Кросплатформна бібліотека для навігації файловою системою, маніпуляцій шляхами, створення каталогів та зчитування атрибутів.

### 4.1. Декомпозиція та нормалізація шляхів

Клас `std::filesystem::path` інкапсулює шляхи у форматах різних операційних систем:
* `.filename()` — повертає останній компонент шляху (ім'я файлу з розширенням).
* `.stem()` — повертає базове ім'я файлу без розширення.
* `.extension()` — повертає суфікс розширення (разом із крапкою).
* `.parent_path()` — повертає шлях до батьківського каталогу.
* `.lexically_normal()` — видаляє зайві роздільники та розкриває відносні сегменти `.` і `..`.
* `.lexically_relative(base)` — обчислює відносний шлях від базової каталогу.

```cpp
#include <filesystem>
namespace fs = std::filesystem;

fs::path p = "/var/log/app.service.log";
fs::path parent = p.parent_path(); // "/var/log"
fs::path filename = p.filename();  // "app.service.log"
fs::path stem = p.stem();          // "app.service"
fs::path ext = p.extension();      // ".log"
```

### 4.2. Операції над файлами та обробка помилок

Бібліотека надає подвійний набір функцій для кожної файлової операції: версію, яка генерує виняток `std::filesystem_error`, та версію, яка приймає вихідний параметр `std::error_code`:

```cpp
std::error_code ec;

// 1. Створення каталогів
fs::create_directories("/tmp/cache/levels/a/b", ec);
if (ec) {
    // Обробка помилки ОС без винятків
}

// 2. Перевірка статусу та розміру
if (fs::exists("/tmp/cache", ec) && fs::is_directory("/tmp/cache", ec)) {
    fs::space_info space = fs::space("/tmp/cache", ec);
    // space.capacity, space.free, space.available
}

// 3. Копіювання та видалення
fs::copy_file("/tmp/source.bin", "/tmp/dest.bin", fs::copy_options::overwrite_existing, ec);
fs::remove_all("/tmp/cache", ec);
```

---

## 5. Паралельні алгоритми STL (`<execution>`, `<algorithm>`, `<numeric>`)

Стандарт C++17 додав перевантаження для понад 60 алгоритмів стандартної бібліотеки, які приймають об'єкт політики виконання (Execution Policy) як перший аргумент.

### Політики виконання (Execution Policies)

| Політика | Тип | Семантика виконання |
| :--- | :--- | :--- |
| `std::execution::seq` | `sequenced_policy` | Послідовне виконання в поточному потоці без розпаралелювання. |
| `std::execution::par` | `parallel_policy` | Паралельне виконання на кількох системних потоках. Алгоритм розбиває діапазон на частини й обробляє їх паралельно. |
| `std::execution::par_unseq` | `parallel_unsequenced_policy` | Паралельне та векторизоване виконання. Дозволяє чергування інструкцій у межах одного потоку (векторизація SIMD). Функтори не повинні використовувати м'ютекси або блокування пам'яті через ризик взаємного блокування всередині одного потоку. |

### Нові числові паралельні алгоритми (`<numeric>`)

```cpp
#include <numeric>
#include <execution>
#include <vector>

std::vector<double> values(10'000'000, 1.5);

// std::reduce: паралельне підсумовування (вимагає асоціативності та комутативності)
double sum = std::reduce(std::execution::par, values.begin(), values.end(), 0.0);

// std::transform_reduce: паралельний MapReduce
std::vector<double> weights(10'000'000, 2.0);
double dot_product = std::transform_reduce(
    std::execution::par_unseq,
    values.begin(), values.end(),
    weights.begin(),
    0.0,
    std::plus<>(),        // Reducer
    std::multiplies<>()   // Transformer
);

// Префіксні суми
std::vector<double> inclusive_out(values.size());
std::inclusive_scan(std::execution::par, values.begin(), values.end(), inclusive_out.begin());

std::vector<double> exclusive_out(values.size());
std::exclusive_scan(std::execution::par, values.begin(), values.end(), exclusive_out.begin(), 0.0);
```

---

## 6. Поліморфні ресурси пам'яті (PMR, `<memory_resource>`)

Підсистема PMR дозволяє відокремити стратегію виділення пам'яті від статичного типу контейнера. Усі контейнери сімейства `std::pmr` використовують єдиний поліморфний алокатор `std::pmr::polymorphic_allocator<T>`, що делегує виклики базовому абстрактному класу `std::pmr::memory_resource`.

### Стандартні ресурси пам'яті

1. **`std::pmr::new_delete_resource()`:** глобальний ресурс за замовчуванням, що делегує виклики глобальним операторам `::operator new` та `::operator delete`.
2. **`std::pmr::null_memory_resource()`:** ресурс, будь-яка спроба виділення пам'яті в якому негайно генерує виняток `std::bad_alloc`. Використовується для гарантування відсутності динамічних алокацій.
3. **`std::pmr::monotonic_buffer_resource`:** швидкий монотонний алокатор (арена), який виділяє пам'ять послідовно зі статичного або стекового буфера без поштучного звільнення. Уся пам'ять звільняється одночасно при знищенні об'єкта ресурсу.
4. **`std::pmr::synchronized_pool_resource` та `std::pmr::unsynchronized_pool_resource`:** пулові алокатори, оптимізовані для частого виділення та звільнення об'єктів невеликого фіксованого розміру з мінімізацією фрагментації пам'яті.

```cpp
#include <memory_resource>
#include <vector>
#include <array>

// Використання монотонної арени на стеку для вкладених контейнерів
std::array<std::byte, 4096> stack_arena;
std::pmr::monotonic_buffer_resource pool(stack_arena.data(), stack_arena.size());

std::pmr::vector<std::pmr::string> words(&pool);
words.emplace_back("high-performance");
words.emplace_back("stack-allocated"); // Пам'ять для рядка та вектора береться зі stack_arena
```

---

## 7. Вдосконалення асоціативних контейнерів (Map & Set Enhancements)

Стандарт C++17 суттєво оптимізував роботу з асоціативними контейнерами `std::map`, `std::unordered_map`, `std::set`, `std::unordered_set`:

### 7.1. Методи try_emplace та insert_or_assign

Метод `.try_emplace()` створює значення за місцем лише тоді, коли ключ відсутній у контейнері, запобігаючи створенню непотрібних тимчасових об'єктів:

```cpp
std::map<std::string, HeavySession> sessions;

// Якщо сесія вже існує, конструктор HeavySession взагалі НЕ викликається:
sessions.try_emplace("session_key", 1024, "auth_token");

// Метод insert_or_assign явно замінює або вставляє значення:
sessions.insert_or_assign("session_key", HeavySession(2048, "new_token"));
```

### 7.2. Вилучення та злиття вузлів (Node Extraction & Splicing)

Метод `.extract()` дозволяє вилучити вузол дерева або геш-таблиці з контейнера без копіювання чи виділення пам'яті, змінити його ключ і перемістити в інший контейнер за константний час `O(1)`:

```cpp
std::map<int, std::string> active_tasks;
std::map<int, std::string> completed_tasks;

// Вилучаємо вузол без деалокації пам'яті:
auto node = active_tasks.extract(101);
if (!node.empty()) {
    node.key() = 202; // Зміна ключа без перестворення елемента
    completed_tasks.insert(std::move(node)); // Вставка без виділення вузла!
}

// Пряме злиття двох асоціативних контейнерів:
completed_tasks.merge(active_tasks);
```

---

## 8. Високопродуктивна конвертація чисел: `<charconv>`

Функції `std::to_chars` та `std::from_chars` забезпечують найшвидшу в C++ конвертацію чисел без виділення пам'яті, без віртуальних викликів та без прив'язки до глобальної локалі `setlocale()`:

```cpp
#include <charconv>
#include <array>

std::array<char, 32> buffer;
int value = 4294967;

// Конвертація числа в рядок
auto [ptr, ec] = std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
if (ec == std::errc()) {
    std::string_view res(buffer.data(), ptr - buffer.data());
}

// Парсинг рядка в число
const char* str = "1048576";
int parsed_val = 0;
auto [parse_ptr, parse_ec] = std::from_chars(str, str + 7, parsed_val);
```

Формати для дійсних чисел керуються переліченням `std::chars_format`:
* `std::chars_format::scientific` — експоненційний вигляд (`1.23e+04`).
* `std::chars_format::fixed` — фіксована крапка (`12300.0`).
* `std::chars_format::hex` — шістнадцятковий плаваючий формат (`0x1.8p+3`).
* `std::chars_format::general` — автоматичний вибір найбільш компактного формату.

---

## 9. Розширення метапрограмування та трейтів типів (`<type_traits>`)

Стандарт C++17 ввів фундаментальні спрощення для метапрограмування на базі шаблонів:

### 9.1. Шаблонні змінні із суфіксом `_v`

Усі стандартні трейти типів отримали зручні шаблонні константи `constexpr bool`, що позбавляють від необхідності писати громіздке `::value`:

```cpp
// До C++17:
bool is_ptr = std::is_pointer<T>::value;

// У C++17:
bool is_ptr = std::is_pointer_v<T>;
bool is_same = std::is_same_v<T, U>;
bool is_const = std::is_const_v<T>;
```

### 9.2. Логічні операції над трейтами

* **`std::conjunction<Traits...>`:** кон'юнкція (логічне І) списку трейтів із підтримкою лінивого короткого замикання (short-circuiting).
* **`std::disjunction<Traits...>`:** диз'юнкція (логічне АБО) списку трейтів.
* **`std::negation<Trait>`:** логічне заперечення трейту.
* **`std::void_t<Types...>`:** допоміжний псевдонім для виявлення валідності складних виразів у SFINAE (визначається як `template <class...> using void_t = void;`).

```cpp
// Перевірка, що всі типи в пакеті є цілочисельними:
template <typename... Args>
inline constexpr bool all_integral_v = std::conjunction_v<std::is_integral<Args>...>;
```

---

## 10. Додаткові утиліти стандартної бібліотеки

* **Синхронізація: `std::scoped_lock` (`<mutex>`):** RAII-замок для атомарного захоплення довільної кількості м'ютексів без ризику виникнення взаємного блокування (Deadlock-free locking).
* **М'ютекс читачів/письменників: `std::shared_mutex` (`<shared_mutex>`):** непідрахований високоефективний м'ютекс для сумісного читання (`std::shared_lock`) та ексклюзивного запису (`std::unique_lock`).
* **Пошукові алгоритми: Боєра-Мура та Боєра-Мура-Горспула (`<functional>`):** швидкі пошукові класи `std::boyer_moore_searcher` та `std::boyer_moore_horspool_searcher` для алгоритму `std::search`.
* **Вибірка елементів: `std::sample` (`<algorithm>`):** стабільна або псевдовипадкова вибірка `n` елементів із діапазону за алгоритмом резервуарної вибірки.
* **Уніфікований виклик: `std::invoke(fn, args...)` (`<functional>`):** узагальнений виклик будь-якого об'єкта, що викликається.
* **Розпакування кортежів: `std::apply` та `std::make_from_tuple` (`<tuple>`).**
* **Математика: `std::clamp`, `std::gcd`, `std::lcm` (`<numeric>`), спеціальні функції в `<cmath>`.**
* **Округлення часу `<chrono>`:** `std::chrono::floor`, `std::chrono::ceil`, `std::chrono::round`, `std::chrono::abs` для часових інтервалів `std::chrono::duration` та точок часу `time_point`.
* **Уніфікований доступ до контейнерів (`<iterator>`):** вільні функції `std::size(c)`, `std::empty(c)`, `std::data(c)` для безпечного звернення до масивів і контейнерів STL.

---

## 11. Вилучені та застарілі можливості

| Сутність | Статус у C++17 | Офіційна заміна в стандарті |
| :--- | :--- | :--- |
| `std::auto_ptr<T>` | **Вилучено (Removed)** | `std::unique_ptr<T>` |
| `std::random_shuffle` | **Вилучено (Removed)** | `std::shuffle` з генераторами `<random>` |
| Ключове слово `register` | **Вилучено (Removed)** | Звичайні локальні змінні (компілятор сам оптимізує регістри) |
| Триграфи (`??=`, `??(`, `??/` тощо) | **Вилучено (Removed)** | Стандартні символи ASCII / UTF-8 |
| Базові класи `std::unary_function`, `std::binary_function` | **Вилучено (Removed)** | Лямбда-вирази, `decltype` та `auto` |
| Оголошення динамічних винятків `throw(X)` | **Вилучено (Removed)** | Специфікатор `noexcept` |
| Оператор інкременту для типу `bool` (`b++`) | **Вилучено (Removed)** | Пряме логічне присвоєння `b = true;` |
| Заголовочний файл `<codecvt>` | **Застарілий (Deprecated)** | Сторонні бібліотеки UTF-8 або ICU / C++20 `std::format` |
| `std::raw_storage_iterator` | **Застарілий (Deprecated)** | Спеціалізовані алгоритми `<memory>` (`std::uninitialized_copy` тощо) |

---

## 12. Макроси перевірки можливостей (Feature Test Macros)

```cpp
#include <version> // C++20, або відповідний заголовок у C++17

#if defined(__cpp_structured_bindings) && __cpp_structured_bindings >= 201606L
    auto [first, second] = get_pair();
#endif

#if defined(__cpp_if_constexpr) && __cpp_if_constexpr >= 201606L
    if constexpr (std::is_integral_v<T>) { ... }
#endif

#if __has_include(<filesystem>)
    #include <filesystem>
    namespace fs = std::filesystem;
#elif __has_include(<experimental/filesystem>)
    #include <experimental/filesystem>
    namespace fs = std::experimental::filesystem;
#endif
```

| Макрос мови | Значення | Опис можливості |
| :--- | :--- | :--- |
| `__cpp_structured_bindings` | `201606L` | Структуровані прив'язки |
| `__cpp_if_constexpr` | `201606L` | Інструкція `if constexpr` |
| `__cpp_deduction_guides` | `201703L` | CTAD та правила виведення типів шаблонів класів |
| `__cpp_fold_expressions` | `201603L` | Вирази згортки для варіативних шаблонів |
| `__cpp_inline_variables` | `201606L` | `inline`-змінні для заголовочних файлів |
| `__cpp_guaranteed_copy_elision` | `201606L` | Гарантоване вилучення копіювання |
| `__cpp_nontype_template_parameter_auto` | `201606L` | `auto` у нетипових параметрах шаблонів |
| `__cpp_capture_star_this` | `201603L` | Захоплення `*this` за значенням у лямбдах |

| Макрос бібліотеки | Значення | Опис компонента STL |
| :--- | :--- | :--- |
| `__cpp_lib_optional` | `201606L` | `std::optional` |
| `__cpp_lib_variant` | `201606L` | `std::variant` |
| `__cpp_lib_any` | `201606L` | `std::any` |
| `__cpp_lib_string_view` | `201606L` | `std::string_view` |
| `__cpp_lib_filesystem` | `201703L` | Бібліотека `std::filesystem` |
| `__cpp_lib_parallel_algorithm` | `201603L` | Політики виконання та паралельні алгоритми |
| `__cpp_lib_byte` | `201603L` | Тип `std::byte` для сирої пам'яті |
| `__cpp_lib_to_chars` | `201611L` | Швидка конвертація `std::to_chars` / `from_chars` |
| `__cpp_lib_scoped_lock` | `201703L` | RAII-замок `std::scoped_lock` |
| `__cpp_lib_memory_resource` | `201603L` | Поліморфні алокатори пам'яті PMR |
| `__cpp_lib_map_try_emplace` | `201411L` | Методи `try_emplace` та `insert_or_assign` |
| `__cpp_lib_node_extract` | `201606L` | Вилучення та переміщення вузлів контейнерів |
