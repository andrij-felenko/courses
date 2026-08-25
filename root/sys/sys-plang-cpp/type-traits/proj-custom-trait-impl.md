# ⚙️ Практика: створення власних type traits та метафункцій

Створення власних метафункцій потрібне тоді, коли стандартного заголовочного файла `<type_traits>` недостатньо для інтроспекції специфічних характеристик користувацьких типів. У практичній розробці узагальнених бібліотек, фреймворків серіалізації, мережевих протоколів або високопродуктивних систем обробки даних постійно виникає потреба опитувати не просто класичний категоріальний тип, а інтерфейсну поведінку та синтаксичну спроможність об'єктів.

До типових завдань метаінженерії належать:
- перевірка наявності в класі специфічного методу (наприклад, `.serialize()` або `.to_json()`);
- перевірка підтримки синтаксису виклику зовнішньої функції в певному просторі імен (наприклад, `std::to_string(x)` або `swap(a, b)`);
- перевірка ітерабельності об'єкта (наявність `std::begin(x)` та `std::end(x)`);
- створення власних комбінованих предикатів типів для валідації концептуальних обмежень;
- безпечний витяг внутрішніх вкладених типів `using value_type` із довільного контейнера без ризику викликати помилку збірки, якщо такого типу не існує.

Нижче розглянуто чотири фундаментальні техніки побудови власних трейтів у мові C++: класичну часткову спеціалізацію шаблонів, ідіому `std::void_t` (C++17), перевірку ітерабельності та універсальну метафункцію виявлення відношень `is_detected` (Detection Idiom).

## Техніка 1. Часткова спеціалізація для розпізнавання шаблонів

Найпростіший варіант власного трейту — перевірити, чи є тип `T` конкретною спеціалізацією певного шаблону класу (наприклад, `std::vector<U, Alloc>` або `std::optional<U>`). Для цього застосовують двокрокову паттерн-модель: первинний шаблон задає негативну відповідь за замовчуванням через успадкування від `std::false_type`, а часткова спеціалізація перехоплює потрібну структуру і повертає `std::true_type`.

```cpp
#include <iostream>
#include <type_traits>
#include <vector>
#include <string>

// 1. Первинний шаблон: за замовчуванням будь-який тип — це не std::vector
template<typename T>
struct is_std_vector : std::false_type {};

// 2. Часткова спеціалізація для будь-якого std::vector<T, Alloc>
template<typename T, typename Alloc>
struct is_std_vector<std::vector<T, Alloc>> : std::true_type {};

// 3. Змінна-допомагач (C++17 variable template)
template<typename T>
inline constexpr bool is_std_vector_v = is_std_vector<T>::value;

int main() {
    std::cout << std::boolalpha;
    std::cout << "int є vector: " << is_std_vector_v<int> << "\n"; // false
    std::cout << "std::vector<double> є vector: " 
              << is_std_vector_v<std::vector<double>> << "\n"; // true
}
```

Цей підхід ідеально працює для точного зіставлення за шаблоном структури, але він є безсилим, коли треба перевірити не конкретний імплантований шаблон, а загальну **синтаксичну поведінку** чи **інтерфейсні властивості** типу.

## Техніка 2. Ідіома std::void_t та SFINAE для опитування членів класу

Звільнення розробників від написання десятків рядків громіздкого макетного коду SFINAE відбулося завдяки простій, але геніальній метафункції `std::void_t` (офіційно включеній у стандарт C++17).

Допоміжний шаблон `std::void_t<Ts...>` завжди перетворює будь-які передані йому аргументи-типи у звичайний тип `void`. Проте вся магія відбувається під час аналізу виразів усередині списку аргументів `std::void_t`. Якщо під час підстановки типів у виразах виникає помилка (наприклад, спроба звернутися до відсутнього методу чи поля), правило SFINAE мовчки скасовує часткову спеціалізацію без генерації помилки компіляції, і компілятор повертається до первинного шаблону.

Розглянемо створення власного метапредиката `has_serialize`, який перевіряє, чи має клас `T` метод `std::string serialize() const`:

```cpp
#include <iostream>
#include <type_traits>
#include <string>

// Первинний шаблон із додатковим параметром-заповнювачем (по замовчуванню void)
template<typename T, typename = void>
struct has_serialize : std::false_type {};

// Часткова спеціалізація за допомогою std::void_t та std::declval
template<typename T>
struct has_serialize<T, std::void_t<
    decltype(std::declval<const T&>().serialize())
>> : std::is_same<
    decltype(std::declval<const T&>().serialize()), 
    std::string
> {};

template<typename T>
inline constexpr bool has_serialize_v = has_serialize<T>::value;

// Тестові типи для перевірки
struct GoodClass {
    std::string serialize() const { return "data"; }
};

struct BadReturnClass {
    int serialize() const { return 42; } // Метод є, але тип повернення не std::string
};

struct NoMethodClass {};

int main() {
    std::cout << std::boolalpha;
    std::cout << "GoodClass: " << has_serialize_v<GoodClass> << "\n";            // true
    std::cout << "BadReturnClass: " << has_serialize_v<BadReturnClass> << "\n";  // false
    std::cout << "NoMethodClass: " << has_serialize_v<NoMethodClass> << "\n";    // false
}
```

### Анатомія метафункції `std::declval<T>()` та приховані пастки

Під час опитування методів або синтаксичних виразів усередині оператора `decltype` неможливо створити екземпляр класу через конструктор `T()`, оскільки тип `T` може не мати конструктора за замовчуванням, мати запривачений конструктор або взагалі бути абстрактним класом із чисто віртуальними функціями.

Для розв'язання цієї проблеми використовують метафункцію `std::declval<T>()`. Вона додає rvalue-посилання до типу `T` (`T&&`) і дозволяє «викликати» методи так, ніби об'єкт дійсно існує, не створюючи жодного екземпляра в пам'яті під час виконання програми.

> ⚠️ **Підступна пастка reference collapsing у `std::declval`:**
> Якщо записати `decltype(std::declval<T>().serialize())`, а параметр `T` виявиться типом посилання `GoodClass&`, за правилами згортання посилань `std::declval<T>()` поверне `GoodClass&`. Якщо при цьому ми спробуємо написати `std::declval<const T>()`, кваліфікатор `const` відпаде від посилання! Щоб гарантувати сувору константність опитуваного об'єкта, треба явно знімати посилання перед накладанням `const`: `std::declval<const std::remove_reference_t<T>&>()`.

## Техніка 3. Інтроспекція ітерабельних контейнерів (is_iterable)

Ще одна поширена задача — перевірити, чи підтримує тип `T` range-based `for`-цикл, тобто чи існують для нього виклики `std::begin(x)` та `std::end(x)`.

```cpp
#include <iostream>
#include <type_traits>
#include <vector>
#include <iterator>

template<typename T, typename = void>
struct is_iterable : std::false_type {};

template<typename T>
struct is_iterable<T, std::void_t<
    decltype(std::begin(std::declval<T&>())),
    decltype(std::end(std::declval<T&>()))
>> : std::true_type {};

template<typename T>
inline constexpr bool is_iterable_v = is_iterable<T>::value;

int main() {
    std::cout << std::boolalpha;
    std::cout << "vector є iterable: " << is_iterable_v<std::vector<int>> << "\n"; // true
    std::cout << "int[5] є iterable: " << is_iterable_v<int[5]> << "\n";           // true
    std::cout << "double є iterable: " << is_iterable_v<double> << "\n";           // false
}
```

Цей трейт чудово розпізнає як контейнери STL, так і сирі C-масиви `int[5]`, бо для масивів у заголовочному файлі `<iterator>` перевантажено функції `std::begin` та `std::end`.

## Техніка 4. Виявлення властивостей за допомогою Detection Idiom (`is_detected`)

Незважаючи на високу ергономіку `std::void_t`, створення окремого шаблону структури з частковою спеціалізацією для кожного нового інтерфейсного виразу вимагає дублювання однакового макетного коду. У бібліотеці Library Fundamentals TS v2 Вальтер Браун запропонував **Detection Idiom** (ідіому виявлення), яка дозволяє перевіряти довільні синтаксичні вирази в один рядок коду.

Основою ідіоми є тип `nonesuch` (який неможливо сконструювати чи знищити) та шаблонний детектор:

```cpp
#include <iostream>
#include <type_traits>
#include <vector>

namespace custom {

// Спеціальний тип для позначення невдалої підстановки в інтроспекції
struct nonesuch {
    ~nonesuch() = delete;
    nonesuch(nonesuch const&) = delete;
    void operator=(nonesuch const&) = delete;
};

namespace detail {
template <template <class...> class Op, class AlwaysVoid, class... Args>
struct detector : std::false_type {
    using type = nonesuch;
};

template <template <class...> class Op, class... Args>
struct detector<Op, std::void_t<Op<Args...>>, Args...> : std::true_type {
    using type = Op<Args...>;
};
} // namespace detail

// 1. Метапредикат: чи валідний вираз Op<Args...>?
template <template <class...> class Op, class... Args>
using is_detected = typename detail::detector<Op, void, Args...>::value_type;

template <template <class...> class Op, class... Args>
inline constexpr bool is_detected_v = is_detected<Op, Args...>::value;

// 2. Безпечний витяг типу: повертає Op<Args...> або nonesuch у разі помилки
template <template <class...> class Op, class... Args>
using detected_t = typename detail::detector<Op, void, Args...>::type;

} // namespace custom

// --- Застосування Detection Idiom ---

// Шаблон операції: перевірка наявності вкладеного типу value_type
template<typename T>
using value_type_t = typename T::value_type;

// Шаблон операції: перевірка оператора індексації [size_t]
template<typename T>
using index_operator_t = decltype(std::declval<T>()[std::declval<size_t>()]);

int main() {
    std::cout << std::boolalpha;

    // Перевірка наявності вкладеного typeset value_type
    std::cout << "vector має value_type: " 
              << custom::is_detected_v<value_type_t, std::vector<int>> << "\n"; // true
    std::cout << "int має value_type: " 
              << custom::is_detected_v<value_type_t, int> << "\n";              // false

    // Перевірка наявності оператора []
    std::cout << "vector має operator[]: " 
              << custom::is_detected_v<index_operator_t, std::vector<int>> << "\n"; // true
}
```

## Зведення застережень та типових помилок метаінженерії

Під час написання власних трейтів розробники найчастіше припускаються трьох фундаментальних помилок:

1. **Робота з неповними типами (Incomplete Types):** Перевірка метафункціями типу, оголошеного лише попередньо через `struct MyStruct;`, викликає неокреслену поведінку (UB) або важкі помилки збірки для більшості предикатів (зокрема `is_polymorphic`, `is_base_of`). Компілятор повинен бачити повне визначення класу, щоб проаналізувати його таблицю віртуальних функцій та поля.
2. **Спеціалізація трейтів у просторі імен `std::` заборонена:** Згідно зі стандартом C++ (§16.4.5.31), розробникам суворо заборонено додавати власний код або спеціалізувати шаблони у просторі імен `std::`, за винятком `std::hash` та `std::numeric_limits` для власних типів. Написання спеціалізації `std::is_integral<MyBigInt>` — це пряме UB. Власні трейти мають завжди жити у власних просторах імен проєкту.
3. **Нехтування кваліфікаторами посилань:** Написання перевірки для `T` без урахування того, що `T` може бути `const T&` або `T&&`, є найпоширенішим джерелом багів у метапрограмуванні. Для очищення вхідних типів завжди використовуйте `std::decay_t<T>` або `std::remove_cvref_t<T>` перед аналізом їхніх характеристик.
