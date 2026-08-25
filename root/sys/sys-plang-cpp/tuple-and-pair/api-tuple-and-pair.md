# 📋 Довідник API: std::pair та std::tuple

Цей довідник містить повну специфікацію публічних інтерфейсів, шаблонних класів, функцій-фабрик, метафункцій інтроспекції та допоміжних алгоритмів заголовочних файлів `<utility>` та `<tuple>` стандарту C++. Документ охоплює контракти конструкторів, гарантії `noexcept`, вимоги до типів та механізми взаємодії зі структурованими зв'язуваннями C++17/C++20.

## 1. Структура заголовків та оголошення типів

Контейнери `std::pair` та `std::tuple` поставляються у двох заголовочних файлах стандартної бібліотеки C++:
- `<utility>`: містить оголошення класу `std::pair`, функцій-фабрик `std::make_pair`, спеціального тегу `std::piecewise_construct` та пов'язані з ними утиліти переміщення об'єктів.
- `<tuple>`: містить оголошення класу `std::tuple`, функцій `std::make_tuple`, `std::tie`, `std::forward_as_tuple`, `std::tuple_cat`, `std::apply`, `std::make_from_tuple`, а також фундаментальні метафункції інтроспекції типів на етапі компіляції.

### Оголошення шаблонних класів

```cpp
// Заголовок <utility>
namespace std {
    template <typename T1, typename T2>
    struct pair;
}

// Заголовок <tuple>
namespace std {
    template <typename... Types>
    class tuple;
}
```

Вибір розділення заголовків зумовлений історичними причинами: `std::pair` є легковагою структурою, необхідною для базових алгоритмів STL та контейнера `std::map`, тому її визначення винесене у легкий заголовок `<utility>`. Клас `std::tuple` вимагає підтримки вариативних шаблонів і складних метафункцій інтроспекції, які зібрані у заголовочному файлі `<tuple>`.

## 2. Специфікація інтерфейсу std::pair<T1, T2>

Клас `std::pair` є прямою гетерогенною связкою двох значень довільних типів `T1` та `T2`. Він задовольняє вимогам концептів `CopyConstructible`, `MoveConstructible`, `Swappable` та `EqualityComparable`, якщо цим вимогам відповідають обидва збережені типи `T1` та `T2`.

### Публічні поля класу

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| `first` | `T1` | Перше збережене значення у парі. |
| `second` | `T2` | Друге збережене значення у парі. |

Поля `first` та `second` оголошені як публічні члени структури. Це забезпечує безпосередній доступ до пам'яті полів за зміщенням без виклику функцій-методиів.

### Конструктори та оператори присвоєння

```cpp
// 1. Конструктор за замовчуванням (умовно explicit)
constexpr explicit(/* див. умови */) pair();

// 2. Конструктор з елементів (умовно explicit)
constexpr explicit(/* див. умови */) pair(const T1& x, const T2& y);

// 3. Шаблонний конструктор з ідеальним передаванням (C++11)
template <typename U1 = T1, typename U2 = T2>
constexpr explicit(/* див. умови */) pair(U1&& x, U2&& y);

// 4. Перетворювальний конструктор копіювання з іншої пари
template <typename U1, typename U2>
constexpr explicit(/* див. умови */) pair(const pair<U1, U2>& p);

// 5. Перетворювальний конструктор переміщення з іншої пари
template <typename U1, typename U2>
constexpr explicit(/* див. умови */) pair(pair<U1, U2>&& p);

// 6. Посекційний конструктор (piecewise construction)
template <typename... Args1, typename... Args2>
constexpr pair(piecewise_construct_t,
               tuple<Args1...> first_args,
               tuple<Args2...> second_args);
```

#### Порожній конструктор за замовчуванням

Порожній конструктор `pair()` є доступним лише тоді, коли обидва типи `T1` та `T2` є конструйованими за замовчуванням (`std::is_default_constructible_v`). Він виконує значенняву ініціалізацію (value-initialization) полів `first()` та `second()`. Це означає, що скалярні типи (наприклад, `int`, `double`, вказівники) ініціалізуються нулями, а не залишаються зі сміттям пам'яті.

#### Правила умовної явності (conditional explicit)

Конструктор `pair` є неявним (`implicit`) лише тоді, коли всі відповідні елементи джерела неявно перетворюються на нові типи (`std::is_convertible_v<U1, T1> && std::is_convertible_v<U2, T2>`). Якщо хоча б один тип вимагає явного примусу (`explicit`), конструктор пари стає `explicit`.

Це застерігає розробника від випадкового виклику небажаних конверсій. Наприклад, якщо тип `T1` має конструктор `explicit T1(int)`, спроба написати `std::pair<T1, int> p = {10, 20};` викличе помилку компіляції, але явний запис `std::pair<T1, int> p(10, 20);` буде успішно прийнятий.

#### Посекційне конструювання (Piecewise Construction)

Конструктор з тегом `std::piecewise_construct` використовується для конструювання полів `first` та `second` безпосередньо за місцем (in-place) шляхом розпакування параметрів із двох наданих `std::tuple`:

```cpp
#include <utility>
#include <tuple>
#include <string>
#include <vector>

// Передавання аргументів у конструктори складних типів усередині пари
std::pair<std::string, std::vector<int>> p(
    std::piecewise_construct,
    std::forward_as_tuple(5, 'a'),       // Конструює string("aaaaa")
    std::forward_as_tuple(10, 42)        // Конструює vector з 10 елементами 42
);
```

Цей конструктор є незамінним під час роботи з типами, які не підтримують копіювання або переміщення, або чиє конструювання вимагає передачі багатьох аргументів у внутрішні поля.

## 3. Специфікація інтерфейсу std::tuple<Types...>

Класу `std::tuple` реалізує кортеж із довільною кількістю елементів `Types...`. Він є фундаментальним інструментом метапрограмування для агрегації типів.

### Конструктори та операції створення

```cpp
// 1. Конструктор за замовчуванням
constexpr explicit(/* див. умови */) tuple();

// 2. Конструктор з константних посилань
constexpr explicit(/* див. умови */) tuple(const Types&... args);

// 3. Шаблонний конструктор з ідеальним передаванням (універсальні посилання)
template <typename... UTypes>
constexpr explicit(/* див. умови */) tuple(UTypes&&... args);

// 4. Перетворювальний конструктор з іншого tuple
template <typename... UTypes>
constexpr explicit(/* див. умови */) tuple(const tuple<UTypes...>& u);

template <typename... UTypes>
constexpr explicit(/* див. умови */) tuple(tuple<UTypes...>&& u);

// 5. Конструктор конвертації з std::pair (лише для tuple з 2 елементів)
template <typename U1, typename U2>
constexpr explicit(/* див. умови */) tuple(const pair<U1, U2>& p);

template <typename U1, typename U2>
constexpr explicit(/* див. умови */) tuple(pair<U1, U2>&& p);
```

#### Аналіз універсальних конструкторів з умовною тривіальністю

Якщо кожен збережений тип у складі `Types...` є тривіально копійованим (`std::is_trivially_copyable_v`), компілятор автоматично генерує для `std::tuple` тривіальні спецчлени (конструктор копіювання, деструктор, оператор присвоєння). Це дозволяє передавати такі кортежі через регістри процесора відповідно до вимог системного ABI.

Якщо ж хоча б один тип у `Types...` має користувацький деструктор чи конструктор переміщення, `std::tuple` стає нетривіальним і викликає відповідні деструктори та конструктори елементів у порядку їх оголошення (від 0-го індексу до N-1).

### Модифікація та обмін (std::swap)

```cpp
// Елементний обмін двох кортежів
constexpr void swap(tuple& rhs) noexcept(/* див. умови */);
```

Метод `swap` та вільна функція `std::swap` для `std::tuple` виконують елементний обмін викликом некваліфікованого `swap(get<i>(*this), get<i>(rhs))` для кожного індексу `i`.

Використання некваліфікованого виклику `swap` разом із попереднім включенням `using std::swap;` активує пошук, залежний от аргументів (Argument-Dependent Lookup, ADL). Завдяки цьому, якщо один із типів кортежу надає високооптимізований користувацький `swap`, компілятор обере саме його замість дефолтного копіювання через тимчасовий об'єкт.

Гарантія `noexcept` для `swap` обчислюється як сукупне логічне І для всіх елементів: `(std::is_nothrow_swappable_v<Types> && ...)`.

## 4. Фабричні функції створення кортежів та посилань

Для полегшення створення кортежів без мануального вказання шаблонних типів стандартна бібліотека надає ряд фабричних функцій.

### std::make_pair та std::make_tuple

```cpp
template <typename T1, typename T2>
constexpr pair<unwrap_ref_decay_t<T1>, unwrap_ref_decay_t<T2>>
make_pair(T1&& x, T2&& y);

template <typename... Types>
constexpr tuple<unwrap_ref_decay_t<Types>...>
make_tuple(Types&&... args);
```

#### Механізм роботи unwrap_ref_decay_t

Метафункція `std::unwrap_ref_decay_t<T>` виконує дві послідовні трансформації:
1. Спочатку застосовується `std::decay_t<T>`, яка перетворює масиви у вказівники (`int[5]` -> `int*`), функції у вказівники на функції, а також знімає top-level `const` та `volatile` кваліфікатори.
2. Далі, якщо отриманий тип є обгорткою посилання `std::reference_wrapper<X>`, метафункція розпаковує її до типу посилання `X&`.

Завдяки цьому виклики `std::make_tuple` дають наступні типи:
- `std::make_tuple(5, 3.14)` -> створює `std::tuple<int, double>`.
- `int x = 0; std::make_tuple(std::ref(x))` -> створює `std::tuple<int&>`.

### std::tie

```cpp
template <typename... Types>
constexpr tuple<Types&...> tie(Types&... args) noexcept;
```

Функція `std::tie` приймає lvalue-посилання на змінні та конструює `std::tuple<Types&...>`. Всі посилання усередині кортежу є зв'язаними з переданими змінними. При присвоєнні іншого кортежу в результат `std::tie` відбувається елементне копіювання значень у зв'язані змінні.

#### Сторожовий елемент std::ignore

`std::ignore` — це глобальний об'єкт неописаного приватного типу з перевантаженим оператором присвоєння `template <typename T> const ignore_type& operator=(const T&) const`. Він дозволяє пропускати непотрібні повернені значення при розпакуванні через `std::tie`:

```cpp
int code;
// Другий елемент повернутого кортежу буде мовчки проігноровано
std::tie(code, std::ignore) = parse_response();
```

### std::forward_as_tuple

```cpp
template <typename... Types>
constexpr tuple<Types&&...> forward_as_tuple(Types&&... args) noexcept;
```

Функція `std::forward_as_tuple` створює `std::tuple`, що містить rvalue-посилання або lvalue-посилання залежно від категорії значень переданих аргументів.

#### Аналіз безпеки та часу життя посилань (Lifetime Hazards)

`std::forward_as_tuple` є інструментом прямого переспрямування і не продовжує час життя тимчасових об'єктів (rvalues). Розглянемо детально різницю у збереженні:

```cpp
// 1. Пряма передача у виклик (БЕЗПЕЧНО):
// Тимчасовий об'єкт std::string("data") живе до кінця повного виразу (full-expression)
process_data(std::forward_as_tuple(1, std::string("data")));

// 2. Збереження у локальну змінну (НЕБЕЗПЕЧНО! Невизначена поведінка UB):
auto t = std::forward_as_tuple(1, std::string("data"));
// Тимчасовий std::string знищується наприкінці цього рядка.
// t[1] перетворюється на висяче посилання (dangling reference)!
```

Використовувати `std::forward_as_tuple` дозволено виключно для негайної передачі аргументів у підпорядковані функції у тому ж самому виразі.

## 5. Доступ до елементів та метафункції інтроспекції

Стандартна бібліотека надає систему доступу до елементів кортежів через статично перевіряємий інтерфейс `std::get`.

### Функції доступу std::get

#### 1. Доступ за індексом (Index-based access)

```cpp
// Для std::pair (індекси 0 та 1)
template <size_t I, typename T1, typename T2>
constexpr tuple_element_t<I, pair<T1, T2>>&
get(pair<T1, T2>& p) noexcept;

// Для std::tuple (індекс I в межах [0, sizeof...(Types)))
template <size_t I, typename... Types>
constexpr tuple_element_t<I, tuple<Types...>>&
get(tuple<Types...>& t) noexcept;
```

Функція `std::get<I>` перевантажена для чотирьох категорій константності та значень: `tuple&`, `const tuple&`, `tuple&&` та `const tuple&&`. Це гарантує, що при виклику `std::get<I>(std::move(t))` повернуте значення буде rvalue-посиланням, дозволяючи перемістити ресурс із кортежу.

Якщо індекс `I >= sizeof...(Types)`, виклик спричиняє помилку компіляції (static_assert усередині реалізації шаблону).

#### 2. Доступ за типом (Type-based access, C++14)

```cpp
template <typename T, typename... Types>
constexpr T& get(tuple<Types...>& t) noexcept;
```

Дозволяє отримувати елемент за назвою його типу. Якщо тип `T` зустрічається у списку `Types...` більше одного разу, або якщо тип `T` відсутній у кортежі, компілятор видає помилку про неможливість вибору шаблону.

### Метафункції інтроспекції етапу компіляції

#### std::tuple_size

Визначає кількість елементів у кортежі, парі чи масиві під час компіляції:

```cpp
template <typename T> struct tuple_size;

// Допоміжне значення у C++17
template <typename T>
inline constexpr size_t tuple_size_v = tuple_size<T>::value;
```

Метафункція `std::tuple_size` має спеціалізації для `std::pair`, `std::tuple`, `std::array`, а також часткові спеціалізації для `const T`, `volatile T` та `const volatile T`.

#### std::tuple_element

Визначає тип елемента за його індексом `I`:

```cpp
template <size_t I, typename T> struct tuple_element;

// Допоміжний псевдонім типу у C++14
template <size_t I, typename T>
using tuple_element_t = typename tuple_element<I, T>::type;
```

За аналогією з `tuple_size`, `tuple_element` зберігає кваліфікатори `const`/`volatile` вихідного типу `T`.

## 6. Алгоритми над кортежами

### std::tuple_cat (Конкатенація кортежів)

```cpp
template <typename... Tuples>
constexpr tuple</* сплющений список типів */>
tuple_cat(Tuples&&... tpls);
```

Приймає довільну кількість кортежів і повертає новий `std::tuple`, у якому всі елементи вхідних кортежів об'єднані в один плаский список. Категорії значень полів зберігаються.

### std::apply (C++17)

```cpp
template <typename F, typename Tuple>
constexpr decltype(auto) apply(F&& f, Tuple&& t);
```

Розпаковує елементи кортежу `t` та викликає з ними функцію або лямбду `f` через `std::invoke`. Повертане значення має тип `decltype(auto)`, що дозволяє зберігати повернення посилань із цільової функції.

### std::make_from_tuple (C++17)

```cpp
template <typename T, typename Tuple>
constexpr T make_from_tuple(Tuple&& t);
```

Створює об'єкт типу `T`, передаючи елементи кортежу `t` в його конструктор `T(std::get<Is>(std::forward<Tuple>(t))...)`.

## 7. Оператори порівняння та підтримка C++20

`std::pair` та `std::tuple` підтримують повний набір операторів порівняння. Порівняння виконується лексикографічно — від першого елемента до останнього.

```cpp
// C++11–C++17: оператори ==, !=, <, <=, >, >=
template <typename... TTypes, typename... UTypes>
constexpr bool operator==(const tuple<TTypes...>& t, const tuple<UTypes...>& u);

template <typename... TTypes, typename... UTypes>
constexpr bool operator<(const tuple<TTypes...>& t, const tuple<UTypes...>& u);

// C++20: оператор трьохстороннього порівняння (<=>)
template <typename... TTypes, typename... UTypes>
constexpr auto operator<=>(const tuple<TTypes...>& t, const tuple<UTypes...>& u);
```

Оператор `<=>` у C++20 повертає спільну категорію порівняння `std::common_comparison_category_t`, яка може бути `std::strong_ordering`, `std::weak_ordering` або `std::partial_ordering` залежно від властивостей елементів.

## 8. Таблиця висунутих вимог та гарантій

| Операція / Метод | Часова складність | Гарантія винятків | Вимоги до типів елементів |
| :--- | :--- | :--- | :--- |
| `std::get<I>(t)` | `O(1)` (компіляція) | `noexcept` | Немає (чистий доступ до пам'яті) |
| `std::make_tuple(args...)` | `O(N)` розпакування | Strong | Повинні підтримувати Move/Copy |
| `std::tuple_cat(t1, t2)` | `O(N + M)` елементів | Strong | Повинні підтримувати Move/Copy |
| `std::apply(fn, t)` | `O(1)` виклик | Визначена викликом `fn` | Придатні до `std::invoke` |
| `swap(t1, t2)` | `O(N)` за індексами | `noexcept` якщо елементи `noexcept` | `std::is_nothrow_swappable` |
