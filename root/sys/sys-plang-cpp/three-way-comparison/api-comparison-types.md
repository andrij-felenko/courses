# 📋 Інтерфейс і типи заголовка <compare>

Заголовок `<compare>` стандартної бібліотеки C++20 надає повний набір типів категорій порівняння, допоміжних предикатів, метафункцій для виведення спільної категорії та об'єктів налаштування для алгоритмів узагальненого програмування.

## Макроси перевірки можливостей (Feature Test Macros)

Наявність підтримки оператора `<=>` у компіляторі та стандартній бібліотеці контролюється двома стандартними макросами:

| Макрос | Мінімальне значення | Опис |
| :--- | :--- | :--- |
| `__cpp_impl_three_way_comparison` | `201907L` | Підтримка мовного оператора `<=>`, синтезу переписаних кандидатів та почленного `= default` компілятором. |
| `__cpp_lib_three_way_comparison` | `201907L` | Наявність типів категорій у просторі імен `std`, допоміжних функцій та алгоритмів у заголовку `<compare>`. |

Ці макроси дозволяють писати переносний код, який перевіряє готовність компілятора та стандартної бібліотеки до роботи з тричленним порівнянням, що особливо важливо під час поступової міграції кодової бази з C++17 на C++20.

```cpp
#include <compare>
```

---

## Фундаментальні типи категорій порівняння

Усі три типи категорій є легкозважними типами-значеннями (value types) із тривіальним копіюванням, знищенням і передаванням через регістри процесора. У типових реалізаціях компіляторів (GCC libstdc++, Clang libc++, MSVC STL) розмір кожного об'єкта категорії становить рівно один байт (`sizeof == 1`), а внутрішній стан зберігається у вигляді одного знакового 8-бітного цілого числа (`int8_t`).

### 1. std::strong_ordering (Сильний / Повний порядок)

Тип `std::strong_ordering` описує математичне відношення повного лінійного строгого порядку (англ. *total order*). Він застосовується до типів, де два значення є або строго меншими одне за одне, або повністю еквівалентними та взаємозамінними.

#### Математичні аксіоми сильного порядку

Сильний порядок вимагає виконання чотирьох обов'язкових математичних властивостей:
1. **Повна зв'язність (Total Connectedness):** для будь-яких двох значень `a` та `b` завжди істинне рівно одне з трьох тверджень: `a < b`, `a == b` або `a > b`. Не існує значень, які неможливо розмістити на одній прямій.
2. **Транзитивність (Transitivity):** якщо `a < b` і `b < c`, то обов'язково `a < c`; аналогічно для рівності: якщо `a == b` і `b == c`, то `a == c`.
3. **Антисиметричність (Antisymmetry):** якщо `a <= b` і `b <= a`, то `a == b`.
4. **Взаємозамінність (Substitutability, або принцип Лейбніца):** якщо `a == b`, то для будь-якої спостережної детермінованої функції `f` значення `f(a) == f(b)`. Об'єкти з погляду зовнішнього спостерігача є абсолютно нерозрізненними за всіма спостережуваними властивостями.

#### Оголошення та інтерфейс

```cpp
class strong_ordering {
    // Внутрішній стан (зазвичай int8_t: -1 для less, 0 для equal, 1 для greater)
    signed char value;

    // Закритий конструктор для ініціалізації констант
    constexpr explicit strong_ordering(signed char v) noexcept : value(v) {}

public:
    // Статичні константи можливих результатів
    static const strong_ordering less;
    static const strong_ordering equal;
    static const strong_ordering equivalent;
    static const strong_ordering greater;

    // Неявні оператори приведення до слабших категорій
    constexpr operator weak_ordering() const noexcept;
    constexpr operator partial_ordering() const noexcept;

    // Оператори порівняння з числовим нулем
    friend constexpr bool operator==(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator!=(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator< (strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator<=(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator> (strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator>=(strong_ordering v, /*unspecified-literal-zero*/) noexcept;

    // Перевернуті оператори (0 == v, 0 < v тощо)
    friend constexpr bool operator==(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator!=(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator< (/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator<=(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator> (/*unspecified-literal-zero*/, strong_ordering v) noexcept;
    friend constexpr bool operator>=(/*unspecified-literal-zero*/, strong_ordering v) noexcept;

    // Тричленне порівняння категорій між собою
    friend constexpr strong_ordering operator<=>(strong_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr strong_ordering operator<=>(/*unspecified-literal-zero*/, strong_ordering v) noexcept;
};
```

| Значення-константа | Семантичний зміст | Порівняння з нулем |
| :--- | :--- | :--- |
| `std::strong_ordering::less` | Перший операнд строго менший за другий | `v < 0` дає `true` |
| `std::strong_ordering::equal` | Операнди рівні й повністю взаємозамінні | `v == 0` дає `true` |
| `std::strong_ordering::equivalent` | Синонім константи `equal` для уніфікації узагальненого коду | `v == 0` дає `true` |
| `std::strong_ordering::greater` | Перший операнд строго більший за другий | `v > 0` дає `true` |

#### Механізм обмеження порівняння лише з нулем

Стандарт навмисно забороняє порівнювати результат `operator<=>` з довільними числами (наприклад, `(a <=> b) == 1` або `(a <=> b) < -5`). Для цього у формальних сигнатурах операторів тип другого аргументу описується як `/*unspecified-literal-zero*/`. На практиці бібліотеки реалізують це через параметр покажчикового типу на неповну внутрішню структуру `__unspecified_zero_type*` або через параметр типу з приватним конструктором, який може бути створений винятково з цілочисельного нульового літерала (`0` або `nullptr`). Якщо розробник спробує написати `(a <=> b) == 1`, компілятор згенерує помилку відсутності відповідного перевантаження.

---

### 2. std::weak_ordering (Слабкий порядок)

Тип `std::weak_ordering` описує відношення **слабкого порядку** (англ. *weak order*). Головна відмінність від сильного порядку полягає у відмові від вимоги повної взаємозамінності: об'єкти можуть бути еквівалентними за критерієм сортування, але різнитися за своїм фізичним станом чи іншими спостережуваними характеристиками.

#### Властивості слабкого порядку

1. **Еквівалентність замість тотожності:** якщо `(a <=> b) == 0`, це означає, що елементи займають однакову позицію у впорядкованому ряду. Проте існує функція `f`, для якої `f(a) != f(b)`.
2. **Транзитивність еквівалентності:** якщо `a` еквівалентне `b`, а `b` еквівалентне `c`, то `a` обов'язково еквівалентне `c`.
3. **Строга сумісність із порядком:** якщо `a` еквівалентне `b`, то для будь-якого `c` нерівність `a < c` істинна тоді й лише тоді, коли істинна `b < c`.

#### Оголошення та інтерфейс

```cpp
class weak_ordering {
    signed char value;
    constexpr explicit weak_ordering(signed char v) noexcept : value(v) {}

public:
    static const weak_ordering less;
    static const weak_ordering equivalent;
    static const weak_ordering greater;

    // Неявне приведення до часткового порядку
    constexpr operator partial_ordering() const noexcept;

    // Порівняння з числовим нулем
    friend constexpr bool operator==(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator!=(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator< (weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator<=(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator> (weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator>=(weak_ordering v, /*unspecified-literal-zero*/) noexcept;

    friend constexpr bool operator==(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator!=(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator< (/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator<=(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator> (/*unspecified-literal-zero*/, weak_ordering v) noexcept;
    friend constexpr bool operator>=(/*unspecified-literal-zero*/, weak_ordering v) noexcept;

    friend constexpr weak_ordering operator<=>(weak_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr weak_ordering operator<=>(/*unspecified-literal-zero*/, weak_ordering v) noexcept;
};
```

| Значення-константа | Семантичний зміст | Порівняння з нулем |
| :--- | :--- | :--- |
| `std::weak_ordering::less` | Перший операнд стоїть раніше за другий | `v < 0` дає `true` |
| `std::weak_ordering::equivalent` | Операнди еквівалентні за критерієм порядку | `v == 0` дає `true` |
| `std::weak_ordering::greater` | Перший операнд стоїть пізніше за другий | `v > 0` дає `true` |

У класі `std::weak_ordering` навмисно відсутня константа з назвою `equal` — замість неї надається винятково `equivalent`, що на рівні назв типів підкреслює відсутність гарантії тотожності.

---

### 3. std::partial_ordering (Частковий порядок)

Тип `std::partial_ordering` описує відношення **часткового порядку** (англ. *partial order*). У цій категорії з'являється четвертий можливий стан відношення — **незрівнюваність** (англ. *incomparability* або `unordered`), коли для пари елементів неможливо встановити, хто з них більший, менший чи еквівалентний.

#### Властивості часткового порядку

1. **Наявність незрівнюваних пар:** існують такі значення `a` та `b`, для яких вирази `a < b`, `a == b` та `a > b` одночасно повертають `false`.
2. **Транзитивність порядку:** якщо `a < b` і `b < c`, то `a < c`. Проте якщо `a` незрівнюване з `b`, це нічого не каже про порівнюваність `a` з `c`.
3. **Рефлексивність рівності порушена:** для незрівнюваних значень вираз `a == a` повертає `false` (класичний приклад — значення `NaN` у стандарті обчислень IEEE 754).

#### Оголошення та інтерфейс

```cpp
class partial_ordering {
    // Внутрішній стан (зазвичай: -1 для less, 0 для equivalent, 1 для greater, 2 для unordered)
    signed char value;
    constexpr explicit partial_ordering(signed char v) noexcept : value(v) {}

public:
    static const partial_ordering less;
    static const partial_ordering equivalent;
    static const partial_ordering greater;
    static const partial_ordering unordered;

    // Порівняння з числовим нулем
    friend constexpr bool operator==(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator!=(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator< (partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator<=(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator> (partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr bool operator>=(partial_ordering v, /*unspecified-literal-zero*/) noexcept;

    friend constexpr bool operator==(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator!=(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator< (/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator<=(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator> (/*unspecified-literal-zero*/, partial_ordering v) noexcept;
    friend constexpr bool operator>=(/*unspecified-literal-zero*/, partial_ordering v) noexcept;

    friend constexpr partial_ordering operator<=>(partial_ordering v, /*unspecified-literal-zero*/) noexcept;
    friend constexpr partial_ordering operator<=>(/*unspecified-literal-zero*/, partial_ordering v) noexcept;
};
```

#### Таблиця істинності операцій для partial_ordering

Поведінка перевірок для `partial_ordering` має критичні відмінності під час обробки стану `unordered`:

| Стан об'єкта `v` | `v == 0` | `v != 0` | `v < 0` | `v <= 0` | `v > 0` | `v >= 0` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `less` | `false` | `true` | **`true`** | **`true`** | `false` | `false` |
| `equivalent` | **`true`** | `false` | `false` | **`true`** | `false` | **`true`** |
| `greater` | `false` | `true` | `false` | `false` | **`true`** | **`true`** |
| **`unordered`** | `false` | **`true`** | `false` | `false` | `false` | `false` |

> ⚠️ Зверніть увагу: для `unordered` усі операції відношення (`==`, `<`, `<=`, `>`, `>=`) повертають `false`. Лише перевірка на нерівність `!= 0` повертає `true`.

---

## Іменовані допоміжні предикати

Для того щоб уникнути порівняння результату `<=>` з нулем у прикладному коді та зробити наміри програміста явними, стандартний заголовок `<compare>` містить шість вбудованих предикатних функцій:

```cpp
namespace std {
    constexpr bool is_eq  (partial_ordering cmp) noexcept { return cmp == 0; }
    constexpr bool is_neq (partial_ordering cmp) noexcept { return cmp != 0; }
    constexpr bool is_lt  (partial_ordering cmp) noexcept { return cmp < 0; }
    constexpr bool is_lteq(partial_ordering cmp) noexcept { return cmp <= 0; }
    constexpr bool is_gt  (partial_ordering cmp) noexcept { return cmp > 0; }
    constexpr bool is_gteq(partial_ordering cmp) noexcept { return cmp >= 0; }
}
```

Оскільки `std::strong_ordering` та `std::weak_ordering` неявно приводяться до `std::partial_ordering`, ці функції є універсальними та працюють з аргументами будь-якої з трьох категорій порівняння.

```cpp
auto order = (user_a <=> user_b);

if (std::is_lt(order)) {
    // user_a передує user_b
} else if (std::is_eq(order)) {
    // user_a та user_b еквівалентні
}
```

Використання іменованих предикатів робить код читабельнішим в узагальнених шаблонах, де тип результату порівняння невідомий заздалегідь, та усуває візуальне засмічення коду нулями.

---

## Метафункції виведення спільних категорій

### 1. std::common_comparison_category

Шаблонний трейт, який визначає найсильнішу категорію порівняння, сумісну з усіма типами зі списку `Ts...`:

```cpp
template <class... Ts>
struct common_comparison_category {
    using type = /*визначений-тип-категорії*/;
};

template <class... Ts>
using common_comparison_category_t = typename common_comparison_category<Ts...>::type;
```

#### Правила обчислення спільної категорії

Виведення спільної категорії підпорядковується правилам решітки приведення типів:
1. Якщо список `Ts...` порожній: результат дорівнює `std::strong_ordering`.
2. Якщо хоча б один тип у `Ts...` не є категорією порівняння: результат дорівнює `void`.
3. Якщо хоча б один тип дорівнює `std::partial_ordering`: результат дорівнює `std::partial_ordering`.
4. Якщо в списку присутній `std::weak_ordering`, а решта — `std::strong_ordering`: результат дорівнює `std::weak_ordering`.
5. Якщо всі типи є `std::strong_ordering`: результат дорівнює `std::strong_ordering`.

Цей трейт лежить в основі роботи компілятора при автоматичному виведенні типу для функції `auto operator<=>(const T&) const = default;`.

### 2. std::compare_three_way_result

Визначає тип, який повертає оператор `<=>` для двох переданих типів `T` та `U` з урахуванням константності та категорій значень:

```cpp
template <class T, class U = T>
struct compare_three_way_result;

template <class T, class U = T>
using compare_three_way_result_t = typename compare_three_way_result<T, U>::type;
```

Якщо для виразів `std::declval<const T&>() <=> std::declval<const U&>()` оператор тричленного порівняння не визначений або є неоднозначним, структура не містить вкладеного псевдоніма `type`, що робить її безпечною для використання в механізмах SFINAE та концептах.

---

## Об'єкти налаштування та алгоритми

### 1. std::compare_three_way (Функціональний об'єкт)

Універсальний функціональний об'єкт із заголовка `<compare>`, призначений для використання як компаратор за замовчуванням у діапазонах та стандартних алгоритмах:

```cpp
struct compare_three_way {
    template <class T, class U>
        requires requires(T&& t, U&& u) {
            static_cast<T&&>(t) <=> static_cast<U&&>(u);
        }
    constexpr auto operator()(T&& t, U&& u) const
        noexcept(noexcept(static_cast<T&&>(t) <=> static_cast<U&&>(u)))
        -> decltype(static_cast<T&&>(t) <=> static_cast<U&&>(u))
    {
        return static_cast<T&&>(t) <=> static_cast<U&&>(u);
    }

    using is_transparent = /*unspecified*/;
};
```

Наявність псевдоніма `is_transparent` дозволяє використовувати `std::compare_three_way` у прозорих асоціативних контейнерах (`std::set`, `std::map`) для гетерогенного пошуку без створення проміжних тимчасових об'єктів.

### 2. Порівняння покажчиків і масивів

Вбудований у мову оператор `<=>` для сирих покажчиків забезпечує строгий сильний порядок (`std::strong_ordering`) лише тоді, коли обидва покажчики вказують на елементи одного й того самого масиву або поля одного об'єкта. Якщо покажчики належать різним незалежним змінним у пам'яті, вбудований оператор порядку дає невизначене відношення (unspecified result за стандартом C++).

Натомість бібліотечний об'єкт `std::compare_three_way` гарантує **глобальний повний порядок** адрес у пам'яті для будь-яких покажчиків одного типу, аналогічно до класичного `std::less<T*>`. Це робить його безпечним для побудови індексів та дерев пошуку над адресами довільних об'єктів.

### 3. Алгоритми строгого впорядкування з синтезом результату

Для гарантування безпечного сортування та коректної роботи з типами, які мають нестандартну поведінку (як-от числа з плаваючою комою) або типи, створені до C++20, стандарт надає дві групи об'єктів налаштування:

#### Прямі функції порядку (Order Customization Point Objects)

- **`std::strong_order(a, b)`:** повертає `std::strong_ordering`. Для типів `float` та `double` забезпечує тотальний порядок згідно зі стандартом IEEE 754-2008 (TotalOrder format):
  `-NaN < -Infinity < -нормалізовані < -0.0 < +0.0 < +нормалізовані < +Infinity < +NaN`.
  Це усуває проблему сортування контейнерів із `NaN`, де стандартний оператор `<` призводив до порушення умов Strict Weak Ordering і падіння алгоритму `std::sort`.
- **`std::weak_order(a, b)`:** повертає `std::weak_ordering`, викликаючи ADL-перевантаження або неявно приводячи результат `std::strong_order`.
- **`std::partial_order(a, b)`:** повертає `std::partial_ordering`, враховуючи природні часткові порядки (зокрема `NaN <=> x == unordered`).

#### Функції зворотного захисту (Fallback Functions)

Коли необхідно порівняти екземпляри застарілих типів (наприклад, сторонніх структур із C++11/C++14, які не мають оператора `<=>`, але мають `operator==` та `operator<`), застосовуються функції зворотного захисту:

```cpp
namespace std {
    inline constexpr /*unspecified*/ compare_strong_order_fallback = /*...*/;
    inline constexpr /*unspecified*/ compare_weak_order_fallback = /*...*/;
    inline constexpr /*unspecified*/ compare_partial_order_fallback = /*...*/;
}
```

Алгоритм роботи `std::compare_strong_order_fallback(a, b)` виконує такі послідовні кроки:
1. Якщо вираз `std::strong_order(a, b)` є коректним — повертає його результат.
2. Якщо вираз `a <=> b` є коректним і повертає тип, що приводиться до `std::strong_ordering` — повертає результат `a <=> b`.
3. Інакше, якщо визначені оператори `a == b` та `a < b`, синтезує сильний порядок вручну:
   ```cpp
   a == b ? std::strong_ordering::equal :
   (a < b ? std::strong_ordering::less : std::strong_ordering::greater)
   ```
4. Якщо жодна з умов не виконана — виклик призводить до помилки компіляції.

Аналогічно працюють `compare_weak_order_fallback` (використовуючи `weak_order`, `<=>` або синтез через `==` та `<`) та `compare_partial_order_fallback` (використовуючи `partial_order`, `<=>` або синтез через `==`, `<` та зворотний `<`).

### 4. std::lexicographical_compare_three_way

Розташований у заголовку `<algorithm>`. Здійснює тричленне порівняння двох послідовностей:

```cpp
template <class InputIt1, class InputIt2, class Cmp>
constexpr auto lexicographical_compare_three_way(
    InputIt1 first1, InputIt1 last1,
    InputIt2 first2, InputIt2 last2,
    Cmp comp) -> decltype(comp(*first1, *first2));
```

Алгоритм послідовно проходить обидва діапазони:
- Для кожної пари елементів викликає компаратор `comp(*first1, *first2)`.
- Якщо результат відмінний від нуля (`cmp != 0`), алгоритм негайно повертає цей результат.
- Якщо один із діапазонів закінчився, а всі попередні елементи були еквівалентними, алгоритм повертає результат порівняння залишкових довжин діапазонів через сильний порядок: `(last1 - first1) <=> (last2 - first2)`.

Якщо параметр `comp` не передано, за замовчуванням використовується `std::compare_three_way{}`.

---

## Форми оголошення operator<=> у користувацьких типах

Під час проектування власних класів у C++20 розробник обирає одну з трьох форм оголошення оператора тричленного порівняння:

### 1. Дружня прихована функція (Hidden Friend)

Рекомендована стандартом ідіома для більшості класів:

```cpp
class Fraction {
    int num;
    int den;
public:
    friend constexpr auto operator<=>(const Fraction&, const Fraction&) = default;
};
```

Переваги прихованого друга:
- Обидва операнди проходять однакове розв'язання перевантажень без преференцій для лівого аргументу.
- Функція не бере участі в загальному пошуку імен (Unqualified Lookup), що зменшує навантаження на таблиці символів компілятора та запобігає конфліктам імен.
- Забезпечується природна симетрія при неявних перетвореннях типів для лівого та правого аргументів.

### 2. Функція-член класу (Member Function)

```cpp
class Vector3D {
    double x, y, z;
public:
    constexpr auto operator<=>(const Vector3D&) const = default;
};
```

Ця форма є коротшою і природно виражає поведінку незмінного константного методу. Компілятор C++20 автоматично синтезує перевернутих кандидатів для викликів, тому симетрія порівнянь зберігається навіть для функцій-членів.

### 3. Автоматично видалений оператор (= delete)

Якщо клас містить поля, типи яких не підтримують оператор тричленного порівняння і не надають пар `==` та `<`, оголошення `operator<=> = default` не призводить до помилки компіляції одразу. Замість цього компілятор позначає оператор як **видалений** (`= delete`). Спроба викликати `<=>` для такого класу згенерує чітке діагностичне повідомлення про використання видаленої функції із зазначенням конкретного проблемного поля.

---

## Специфікація винятків (noexcept) у порівняннях

Для ефективної роботи стандартних контейнерів оператори порівняння повинні бути позначені специфікатором `noexcept`.

Під час генерації оператора через `= default` компілятор автоматично обчислює умовний `noexcept`:
- `operator<=> = default` позначається як `noexcept`, якщо виклики `<=>` для всіх базових класів та нестатичних полів є `noexcept`.
- Якщо хоча б одне поле класу має оператор порівняння, здатний кидати винятки (наприклад, сторонній тип із динамічним виділенням пам'яті всередині оператора), згенерований оператор не отримає позначки `noexcept`.

У ручних реалізаціях рекомендується явно вказувати `noexcept`, що дозволяє оптимізаторам генерувати компактніший машинний код без кодових таблиць розкрутки стека (Exception Tables).

---

## Поведінка стандартних контейнерів і типів-обгорток

Усі стандартні типи бібліотеки C++20 оновлено для надання оператора `<=>`:

1. **Кортежі та пари (`std::tuple`, `std::pair`):**
   Повертають `std::common_comparison_category_t` від результатів порівняння всіх своїх полів. Якщо пара містить `int` і `double`, її оператор `<=>` повертає `std::partial_ordering`.
2. **Опціональні значення (`std::optional<T>`):**
   Порожній об'єкт `std::nullopt` вважається строго меншим за будь-який об'єкт, що містить значення (`*opt`). Якщо обидва об'єкти заповнені, результат дорівнює `*a <=> *b`. Тип результату — `std::compare_three_way_result_t<T>`.
3. **Послідовні контейнери (`std::vector<T>`, `std::array<T, N>`, `std::string`):**
   Виконують лексикографічне порівняння елементів через `std::lexicographical_compare_three_way`. Категорія результату збігається з категорією порівняння самого типу елемента `T`.
4. **Варіанти (`std::variant<Ts...>`):**
   Об'єкт `std::valueless_by_exception` вважається найменшим за будь-яке валідне значення. Якщо індекси активних альтернатив відрізняються (`index() != o.index()`), результат дорівнює `index() <=> o.index()`. Якщо індекси збігаються, викликається оператор `<=>` для активного типу в середині варіанта.

---

## Асемблерне розгортання та оптимізація компіляторів

Оператор `<=>` проектувався з урахуванням безшовної трансляції в інструкції сучасних процесорів:
- **Цілочисельне порівняння (x86-64):** інструкція `cmp reg1, reg2` встановлює апаратні прапорці `ZF` (Zero Flag), `SF` (Sign Flag) та `OF` (Overflow Flag). Компілятори (GCC та Clang) транслюють вираз `(a <=> b) < 0` у безгалузеву послідовність інструкцій `cmp` + `setl`, повністю уникаючи інструкцій умовного переходу `jmp` та запобігаючи штрафам промаху передбачувача переходів (Branch Misprediction Penalty).
- **Порівняння чисел із плаваючою комою:** інструкція `ucomisd xmm0, xmm1` безпосередньо встановлює прапорець нечислового значення `PF` (Parity Flag) у разі виявлення `NaN`, що дозволяє компілятору генерувати мінімальний код перевірки категорії `partial_ordering::unordered` без виклику важких бібліотечних функцій.

---

## Стандартні концепти порівняння C++20

Заголовок `<compare>` містить концепти для формальної специфікації вимог до параметрів шаблонів:

```cpp
template <class T, class Cat = std::partial_ordering>
concept three_way_comparable =
    requires(const std::remove_reference_t<T>& a,
             const std::remove_reference_t<T>& b) {
        { a <=> b } -> /*compares-as*/<Cat>;
    };

template <class T, class U, class Cat = std::partial_ordering>
concept three_way_comparable_with =
    std::three_way_comparable<T, Cat> &&
    std::three_way_comparable<U, Cat> &&
    requires(const std::remove_reference_t<T>& t,
             const std::remove_reference_t<U>& u) {
        { t <=> u } -> /*compares-as*/<Cat>;
        { u <=> t } -> /*compares-as*/<Cat>;
    };
```

Допоміжний експозиційний концепт `/*compares-as*/<Cat>` перевіряє, що тип результату оператора `<=>` може бути неявно перетворений на очікувану категорію `Cat`, забороняючи повернення невідповідних типів (наприклад, повернення `partial_ordering` там, де концепт вимагає `strong_ordering`).
