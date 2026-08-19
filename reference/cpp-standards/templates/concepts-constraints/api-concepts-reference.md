# 📋 Стандартні концепти бібліотеки <concepts>

Заголовний файл `<concepts>` стандарту C++20 містить фундаментальну систему стандартних концептів мови. Вони формалізують вимоги до типів даних, операцій життєвого циклу, арифметики, операторів порівняння та функціональних об'єктів, на яких побудовано всю сучасну стандартну бібліотеку — зокрема нові підсистеми алгоритмів, ітераторів та діапазонів (Ranges).

Усі концепти оголошені у просторі імен `std` і обчислюються виключно на етапі компіляції як константні булеві предикати. На відміну від застарілих метафункцій SFINAE, стандартні концепти беруть участь у частковому впорядкуванні перевантажень (subsumption) та забезпечують миттєву діагностику помилок безпосередньо в точці виклику шаблону.

---

## 1. Базові мовні концепти (Core Language Concepts)

Ця група концептів формалізує фундаментальні відношення між типами мови C++, перевіряє можливість неявних і явних перетворень, а також накладає обмеження на вбудовані властивості системи типів.

```cpp
#include <concepts>
```

### Відношення спорідненості та перетворення типів

#### Концепт повної ідентичності типів: `std::same_as`

Концепт `std::same_as<T, U>` вимагає абсолютної тотожності типів `T` та `U`. На відміну від звичайної перевірки метафункцією `std::is_same_v<T, U>`, визначення концепту в стандарті є строго симетричним:

```cpp
template<typename T, typename U>
concept same_as = std::is_same_v<T, U> && std::is_same_v<U, T>;
```

Така двостороння кон'юнкція є обов'язковою для коректної роботи компіляторного алгоритму нормалізації та поглинання обмежень (subsumption). Якщо перевантаження функції `f(T)` обмежене виразом `std::same_as<T, int>`, а інше перевантаження використовує `std::same_as<int, T>`, компілятор розкладає обидва вирази на еквівалентні атомарні обмеження `std::is_same_v<T, int>` та `std::is_same_v<int, T>`. Завдяки цьому компілятор розпізнає симетрію і не генерує помилку неоднозначності виклику.

Концепт враховує всі кваліфікатори типу: `const int` не є тотожним `int`, а посилання `int&` не є тотожним значенню `int`. Якщо алгоритм вимагає сумісності без урахування константності або посилань, перед перевіркою застосовують `std::remove_cvref_t<T>`.

#### Концепт відношення спадкування: `std::derived_from`

Концепт `std::derived_from<Derived, Base>` перевіряє, чи є тип `Derived` нащадком класу `Base`. Стандарт C++20 висуває до цього відношення дві суворі вимоги:

```cpp
template<typename Derived, typename Base>
concept derived_from = 
    std::is_base_of_v<Base, Derived> &&
    std::is_convertible_v<const volatile Derived*, const volatile Base*>;
```

Перша частина предикату (`std::is_base_of_v`) перевіряє факт наявності базового класу на рівні компілятора. Проте цього недостатньо: `std::is_base_of_v` повертає `true` навіть тоді, коли успадкування є приватним (`private`), захищеним (`protected`) або неоднозначним (множинне успадкування без віртуальної бази). Тому друга частина предикату перевіряє можливість неявного приведення вказівника на похідний клас до вказівника на базовий клас. Це гарантує, що клієнтський код зможе викликати публічні методи базового класу через посилання або вказівник на `Derived`.

#### Концепт приведення типів: `std::convertible_to`

Концепт `std::convertible_to<From, To>` вимагає, щоб вираз типу `From` міг бути перетворений на тип `To` як неявно (наприклад, при передачі аргументу у функцію або поверненні значення), так і явно через `static_cast`.

```cpp
template<typename From, typename To>
concept convertible_to = 
    std::is_convertible_v<From, To> &&
    requires(std::add_rvalue_reference_t<From> (&f)()) {
        static_cast<To>(f());
    };
```

Ця подвійна перевірка запобігає класичним пасткам C++98, коли тип формально мав неявне приведення, але явне конструювання або перетворення тимчасового об'єкта було заборонене чи викликало неоднозначність через наявність конструкторів `explicit`.

#### Концепти спільного типу та спільного посилання: `std::common_with` та `std::common_reference_with`

В узагальнених алгоритмах часто виникає потреба визначити тип, до якого можна безпечно звести два різні типи `T` та `U` (наприклад, при порівнянні чисел різних розрядностей чи об'єднанні результатів тернарного оператора `cond ? a : b`).

- `std::common_with<T, U>` — вимагає існування спільного типу значення `std::common_type_t<T, U>`, до якого обидва типи можуть бути явно та неявно приведені зі збереженням еквівалентності значень.
- `std::common_reference_with<T, U>` — глибший концепт, який перевіряє існування спільного типу посилання `std::common_reference_t<T, U>`. Це необхідно для роботи проксі-ітераторів (наприклад, `std::vector<bool>::reference` або кортежних ітераторів Zip), де тип посилання не є звичайним `T&`.

```cpp
template<typename T, typename U>
requires std::common_with<T, U>
auto compute_max(const T& a, const U& b) -> std::common_type_t<T, U> {
    return (a > b) ? a : b;
}
```

---

### Арифметичні концепти та класифікація чисел

Арифметичні концепти стандарту C++20 усувають необхідність писати складні конструкції SFINAE з використанням `std::is_integral` та `std::is_floating_point`.

```cpp
template<typename T>
concept integral = std::is_integral_v<T>;

template<typename T>
concept signed_integral = std::integral<T> && std::is_signed_v<T>;

template<typename T>
concept unsigned_integral = std::integral<T> && !std::is_signed_v<T>;

template<typename T>
concept floating_point = std::is_floating_point_v<T>;
```

#### Особливості та нюанси арифметичних концептів

1. **Тип `bool`**: стандарт C++ класифікує `bool` як цілочисловий тип, тому вираз `std::integral<bool>` повертає `true`. Проте тип `bool` не підтримує інкременти та має спеціальну поведінку при неявних приведеннях, тому в користувацьких концептах числових операцій для нього часто додають виключення `!std::same_as<std::remove_cv_t<T>, bool>`.
2. **Тип `char`**: залежно від архітектури та налаштувань компілятора (прапорець `-funsigned-char`) базовий тип `char` може бути знаковим або беззнаковим. Концепт `std::signed_integral<char>` поверне `true` лише на платформах, де `char` реалізовано як знаковий тип. Водночас `std::integral<char>` є істинним завжди.
3. **Типи `enum` та `enum class`**: перелічувані типи не задовольняють концепт `std::integral`, навіть якщо мають явно вказаний базовий цілочисловий тип (`enum class Status : uint32_t`). Це запобігає випадковому застосуванню арифметичних алгоритмів до сутностей, що представляють стани або прапорці.
4. **Типи з плаваючою комою**: концепт `std::floating_point<T>` задовольняють лише фундаментальні типи `float`, `double`, `long double` та додаткові розширені типи з плаваючою комою C++23 (`std::float16_t`, `std::float32_t`, `std::float64_t`, `std::float128_t`, `std::bfloat16_t`). Користувацькі класи великих чисел (BigFloat) не задовольняють цей концепт автоматично, якщо для них не додано відповідну спеціалізацію рис типів.

---

### Концепти присвоєння та обміну значеннями

Операції зміни стану є критичними для сортування, перестановки елементів та керування пам'яттю.

```cpp
template<typename LHS, typename RHS>
concept assignable_from = 
    std::is_lvalue_reference_v<LHS> &&
    std::common_reference_with<
        const std::remove_reference_t<LHS>&,
        const std::remove_reference_t<RHS>&> &&
    requires(LHS lhs, RHS&& rhs) {
        { lhs = static_cast<RHS&&>(rhs) } -> std::same_as<LHS>;
    };

template<typename T>
concept swappable = 
    requires(T& a, T& b) {
        ranges::swap(a, b);
    };

template<typename T, typename U>
concept swappable_with = 
    std::common_reference_with<T, U> &&
    requires(T&& t, U&& u) {
        ranges::swap(static_cast<T&&>(t), static_cast<T&&>(t));
        ranges::swap(static_cast<U&&>(u), static_cast<U&&>(u));
        ranges::swap(static_cast<T&&>(t), static_cast<U&&>(u));
        ranges::swap(static_cast<U&&>(u), static_cast<T&&>(t));
    };
```

Головна відмінність `std::swappable` полягає у використанні точок кастомізації (CPO) простору імен `std::ranges::swap`. Цей механізм спочатку шукає користувацьку функцію `swap` в асоційованому просторі імен через аргументно-залежний пошук (ADL), а якщо її немає — безпечно викликає `std::swap` за умови, що тип є переміщуваним.

---

## 2. Концепти життєвого циклу та створення об'єктів

Життєвий цикл об'єктів у C++ визначається правилами створення в пам'яті, ініціалізації, копіювання, переміщення та виклику деструктора. Стандарт C++20 формалізує ці кроки у вигляді суворої послідовності концептів.

```cpp
// 1. Безпечне знищення об'єкта
template<typename T>
concept destructible = std::is_nothrow_destructible_v<T>;

// 2. Створення об'єкта з аргументами
template<typename T, typename... Args>
concept constructible_from = 
    std::destructible<T> && 
    std::is_constructible_v<T, Args...>;

// 3. Ініціалізація за замовчуванням
template<typename T>
concept default_initializable = 
    std::constructible_from<T> &&
    requires {
        T{};
        ::new (static_cast<void*>(nullptr)) T;
    } &&
    requires {
        T();
    };

// 4. Конструювання переміщенням
template<typename T>
concept move_constructible = 
    std::constructible_from<T, T> && 
    std::convertible_to<T, T>;

// 5. Конструювання копіюванням
template<typename T>
concept copy_constructible = 
    std::move_constructible<T> &&
    std::constructible_from<T, T&> && std::convertible_to<T&, T> &&
    std::constructible_from<T, const T&> && std::convertible_to<const T&, T> &&
    std::constructible_from<T, const T> && std::convertible_to<const T, T>;
```

### Чому destructible вимагає noexcept

Концепт `std::destructible` базується на `std::is_nothrow_destructible_v<T>`. У мові C++ деструктори за замовчуванням є `noexcept(true)`. Якщо розробник створює клас із деструктором, який потенційно може викинути виняток (`noexcept(false)`), такий тип не задовольняє концепт `std::destructible`.

Це фундаментальне архітектурне рішення комітету ISO: якщо тип не гарантує безпечного знищення без винятків, його не можна використовувати в стандартних контейнерах, передавати за значенням чи розміщувати в динамічній пам'яті, оскільки це унеможливлює забезпечення базової гарантії безпеки винятків (Basic Exception Safety Guarantee).

### Тонкощі концепту default_initializable

Концепт `std::default_initializable` вимагає значно більше, ніж просто наявність конструктора за замовчуванням. Він перевіряє три окремі форми ініціалізації:
1. Ініціалізацію за замовчуванням: `T a;` (неініціалізовані значення для фундаментальних типів).
2. Ініціалізацію значенням: `T a{};` та `auto b = T();` (обнулення пам'яті для фундаментальних типів).
3. Пряме розміщення через placement new: `::new (ptr) T;`.

Це унеможливлює ситуації, коли клас має конструктор за замовчуванням, позначений як `explicit`, який не може бути викликаний у контексті копіювальної ініціалізації типу `T a = {};`.

---

## 3. Об'єктні концепти та семантика значень

Об'єктні концепти стандарту C++20 узагальнюють поняття типу, що володіє повноцінною семантикою значень (англ. *value semantics*). Вони побудовані у вигляді строгої ієрархічної драбини від переміщуваного об'єкта до регулярного типу за Олександром Степановим.

```
std::movable
    ▲
    │ (додає можливість копіювання)
std::copyable
    ▲
    │ (додає ініціалізацію за замовчуванням)
std::semiregular
    ▲
    │ (додає оператор рівності ==)
std::regular
```

### Формальні визначення об'єктної ієрархії

```cpp
// 1. Переміщуваний тип: можна перемістити конструктором та оператором присвоєння
template<typename T>
concept movable = 
    std::is_object_v<T> &&
    std::move_constructible<T> &&
    std::assignable_from<T&, T> &&
    std::swappable<T>;

// 2. Копійовний тип: можна дублювати в пам'яті без руйнування оригіналу
template<typename T>
concept copyable = 
    std::copy_constructible<T> &&
    std::movable<T> &&
    std::assignable_from<T&, T&> &&
    std::assignable_from<T&, const T&> &&
    std::assignable_from<T&, const T>;

// 3. Напіврегулярний тип: копійовний тип з можливістю створення за замовчуванням
template<typename T>
concept semiregular = 
    std::copyable<T> && 
    std::default_initializable<T>;

// 4. Регулярний тип: напіврегулярний тип із математичною рівністю значень
template<typename T>
concept regular = 
    std::semiregular<T> && 
    std::equality_comparable<T>;
```

### Філософія та значення концепту std::regular

Концепт `std::regular` є наріжним каменем узагальненого програмування. У книзі *Elements of Programming* Олександр Степанов та Пол МакДжонс визначили регулярний тип як тип, що поводиться у пам'яті програми так само природно, надійно та прозоро, як вбудований апаратний тип `int`.

Регулярний тип гарантує виконання таких інваріантів:
1. **Ізоляція значень (Value Independence)**: копіювання об'єкта `T b = a;` створює повністю незалежну сутність. Будь-які подальші зміни стану `b` не можуть змінити стан `a`.
2. **Коректність рівності після копіювання**: після виконання копіювання `T b = a;` вираз `a == b` завжди повертає `true`.
3. **Еквівалентність замінності**: якщо `a == b`, то застосування будь-якої детермінованої константної операції `f(a)` та `f(b)` повинно давати однаковий результат.
4. **Валідність стану після переміщення**: об'єкт, з якого було переміщено дані (`T c = std::move(a);`), залишається у валідному стані, його можна безпечно знищити або повторно присвоїти йому нове значення.

Практично всі контейнери стандартної бібліотеки (`std::vector<T>`, `std::string`, `std::list<T>`, `std::map<K, V>`) є регулярними типами за умови, що типи їхніх елементів є регулярними.

---

## 4. Концепти порівняння (Comparison Concepts)

Концепти порівняння формалізують вимоги до бінарних операторів відношення (`==`, `!=`, `<`, `<=`, `>`, `>=`) та нового тристороннього оператора космічного корабля (`<=>`), введеного у C++20.

```cpp
// 1. Перевірка на рівність для одного типу
template<typename T>
concept equality_comparable = 
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a == b } -> std::convertible_to<bool>;
        { a != b } -> std::convertible_to<bool>;
    };

// 2. Двостороннє перехресне порівняння на рівність для двох різних типів
template<typename T, typename U>
concept equality_comparable_with = 
    std::equality_comparable<T> &&
    std::equality_comparable<U> &&
    std::common_reference_with<
        const std::remove_reference_t<T>&,
        const std::remove_reference_t<U>&> &&
    std::equality_comparable<
        std::common_reference_t<
            const std::remove_reference_t<T>&,
            const std::remove_reference_t<U>&>> &&
    requires(const std::remove_reference_t<T>& t,
             const std::remove_reference_t<U>& u) {
        { t == u } -> std::convertible_to<bool>;
        { t != u } -> std::convertible_to<bool>;
        { u == t } -> std::convertible_to<bool>;
        { u != t } -> std::convertible_to<bool>;
    };

// 3. Строгий повний порядок (Total Ordering)
template<typename T>
concept totally_ordered = 
    std::equality_comparable<T> &&
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a < b }  -> std::convertible_to<bool>;
        { a > b }  -> std::convertible_to<bool>;
        { a <= b } -> std::convertible_to<bool>;
        { a >= b } -> std::convertible_to<bool>;
    };

// 4. Тристороннє порівняння через spaceship operator (<=>)
template<typename T, typename Cat = std::partial_ordering>
concept three_way_comparable = 
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a <=> b } -> std::convertible_to<Cat>;
    };
```

### Семантичні аксіоми концепту totally_ordered

Синтаксичної наявності оператора `operator<` недостатньо для коректної роботи алгоритмів пошуку та сортування. Концепт `std::totally_ordered` вимагає дотримання чотирьох математичних аксіом строгого повного порядку:
1. **Іррефлексивність**: для будь-якого `a` вираз `a < a` є хибним (`false`).
2. **Асиметрія**: якщо `a < b` є істинним, то `b < a` є хибним.
3. **Транзитивність**: якщо `a < b` та `b < c`, то `a < c`.
4. **Повнота трихотомії**: для будь-яких двох значень `a` та `b` рівно одне з трьох тверджень є істинним: `a < b`, `b < a` або `a == b`.

#### Крайовий випадок: числа з плаваючою комою та NaN

Типи `float` та `double` синтаксично повністю задовольняють вимоги концепту `std::totally_ordered`, оскільки для них визначені всі шість операторів порівняння. Проте наявність значення «не-число» (`NaN` — Not a Number) порушує аксіому трихотомії: вирази `NaN < x`, `x < NaN` та `NaN == x` одночасно повертають `false`. Тому стандарт C++20 у концепті `std::three_way_comparable` класифікує порівняння чисел із плаваючою комою як частковий порядок (`std::partial_ordering`), тоді як цілі числа мають строгий порядок (`std::strong_ordering`).

#### Категорії порівняння у C++20

Стандарт визначає три фундаментальні категорії результату тристороннього порівняння:
- `std::strong_ordering` — абсолютна рівність і строгий порядок (для цілих чисел, символів та покажчиків): якщо `a <=> b == 0`, то `a` та `b` є повністю взаємозамінними у будь-якому контексті.
- `std::weak_ordering` — еквівалентність без повної тотожності (наприклад, порівняння рядків без урахування регістру: `"hello"` та `"HELLO"` еквівалентні за довжиною та символами, але не ідентичні за байтовим складом).
- `std::partial_ordering` — частковий порядок, де деякі значення взагалі неможливо порівняти (числа з плаваючою комою через наявність `NaN`).

---

## 5. Концепти функціональних об'єктів та виклику (Callable Concepts)

Узагальнені алгоритми стандартної бібліотеки приймають функції зворотного виклику (callbacks), компаратори, проєкції та предикати. Група концептів виклику дозволяє точно зафіксувати вимоги до сигнатури функції та типу поверненого результату.

```cpp
// 1. Загальний концепт викликабельного об'єкта
template<typename F, typename... Args>
concept invocable = 
    requires(F&& f, Args&&... args) {
        std::invoke(std::forward<F>(f), std::forward<Args>(args)...);
    };

// 2. Регулярний викликабельний об'єкт (детермінована функція без побічних ефектів)
template<typename F, typename... Args>
concept regular_invocable = 
    std::invocable<F, Args...>;

// 3. Булевий предикат
template<typename F, typename... Args>
concept predicate = 
    std::regular_invocable<F, Args...> &&
    requires(F&& f, Args&&... args) {
        { std::invoke(std::forward<F>(f), std::forward<Args>(args)...) } 
            -> std::convertible_to<bool>;
    };

// 4. Бінарне відношення
template<typename R, typename T, typename U>
concept relation = 
    std::predicate<R, T, T> &&
    std::predicate<R, U, U> &&
    std::predicate<R, T, U> &&
    std::predicate<R, U, T>;

// 5. Відношення еквівалентності
template<typename R, typename T, typename U>
concept equivalence_relation = 
    std::relation<R, T, U>;

// 6. Строгий слабкий порядок (Strict Weak Ordering — вимога для std::ranges::sort)
template<typename R, typename T, typename U>
concept strict_weak_order = 
    std::relation<R, T, U>;
```

### Синтаксична тотожність проти семантичного контракту

Визначення концептів `std::invocable` та `std::regular_invocable` у коді виглядають абсолютно однаково. Обидва перевіряють, чи можна передати аргументи `Args...` у функціональний об'єкт `F` за допомогою `std::invoke` (що підтримує звичайні функції, покажчики на функції, лямбда-вирази, функтори та покажчики на методи й поля класів).

Проте між ними діє важлива семантична різниця:
- `std::invocable` дозволяє виклику модифікувати стан самого об'єкта функції або залежати від зовнішнього змінюваного стану (наприклад, лямбда з захопленням посилання, генератор псевдовипадкових чисел `std::mt19937` чи функція з внутрішнім лічильником викликів).
- `std::regular_invocable` є семантичним контрактом чистої функції: вона не повинна змінювати стан вхідних аргументів і для однакових аргументів зобов'язана повертати однаковий результат незалежно від кількості викликів.

Алгоритми стандартної бібліотеки, які можуть викликати функцію довільну кількість разів або паралельно у кількох потоках (наприклад, `std::ranges::transform` або алгоритми бібліотеки `<execution>`), вимагають концепту `std::regular_invocable`.

---

## 6. Зв'язок із концептами ітераторів та діапазонів (Ranges)

Концепти бібліотеки `<concepts>` є прямим фундаментом для системи концептів ітераторів у заголовному файлі `<iterator>` та діапазонів у `<ranges>`.

```cpp
#include <iterator>
#include <ranges>

// Ієрархія концептів ітераторів C++20:
// std::input_or_output_iterator
//   ▲
//   ├── std::output_iterator<T>
//   └── std::input_iterator
//         ▲
//         └── std::forward_iterator
//               ▲
//               └── std::bidirectional_iterator
//                     ▲
//                     └── std::random_access_iterator
//                           ▲
//                           └── std::contiguous_iterator
```

### Як базові концепти формують вимоги до ітераторів

1. **`std::forward_iterator`** вимагає від ітератора задоволення концепту `std::copyable` та `std::equality_comparable`, що дозволяє здійснювати багаторазовий прохід по послідовності зі збереженням позиції.
2. **`std::bidirectional_iterator`** додає операції декременту `--it` та `it--`.
3. **`std::random_access_iterator`** додає вимогу `std::totally_ordered` для ітераторів, арифметику довільного зміщення `it + n`, різницю ітераторів `it2 - it1` та оператор індексації `it[n]`.
4. **`std::contiguous_iterator`** накладає найсуворіше апаратне обмеження: елементи послідовності повинні лежати в пам'яті фізично неперервно (як у сирому масиві `T[]`, `std::vector<T>`, `std::array<T, N>` або `std::string_view`), так що вираз `std::to_address(it + n)` дорівнює `std::to_address(it) + n`.

### Концепти діапазонів (Ranges)

Діапазон у C++20 формалізується як сукупність ітератора початку та обмежувача (sentinel):
- `std::ranges::range<R>` — вимагає наявності `std::ranges::begin(r)` та `std::ranges::end(r)`.
- `std::ranges::sized_range<R>` — вимагає обчислення розміру діапазону за константний час `O(1)` через `std::ranges::size(r)`.
- `std::ranges::view<R>` — вимагає, щоб операції копіювання та переміщення діапазону виконувалися за час `O(1)` незалежно від кількості елементів (семантика ледачого перегляду без володіння даними).

---

## 7. Практичні правила застосування та безпеки

### Правило 1: Уникайте надмірної типізації через std::same_as

Частою помилкою є використання `std::same_as<T, int>` там, де насправді мається на увазі `std::integral<T>` або `std::convertible_to<T, int>`. Надмірне звуження інтерфейсу забороняє передавати сумісні типи (наприклад, `short`, `unsigned int` або користувацькі числові класи), зводячи нанівець переваги узагальненого програмування.

### Правило 2: Правильна перевірка посилань у constructible_from

При написанні фабричних методів або контейнерів із семантикою `emplace` необхідно передавати типи аргументів із кваліфікаторами посилань:

```cpp
// НЕПРАВИЛЬНО: вимагає можливості створити rvalue-копію
template<typename T, typename... Args>
requires std::constructible_from<T, Args...>
T create_object(Args&&... args);

// ПРАВИЛЬНО: враховує категорії значень переданих аргументів
template<typename T, typename... Args>
requires std::constructible_from<T, Args&&...>
T create_object(Args&&... args) {
    return T(std::forward<Args>(args)...);
}
```

### Правило 3: Використання концептів як захисних бар'єрів API

Розміщення стандартних концептів на межі відкритого інтерфейсу модулів та бібліотек перетворює будь-яку помилку неправильного використання коду на локалізоване дворядкове повідомлення компілятора в точці виклику, повністю блокуючи генерацію каскадних помилок інстанціювання з внутрішніх файлів реалізації.
