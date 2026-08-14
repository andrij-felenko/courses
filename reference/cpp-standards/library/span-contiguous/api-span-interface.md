# 📋 Довідник інтерфейсу std::span та концептів суміжної пам'яті

Класовий шаблон `std::span<Element, Extent>` з заголовочного файла `<span>` надає безволодісний погляд (англ. *non-owning view*) на неперервну послідовність об'єктів у пам'яті. Цей документ містить повний специфікаційний довідник типів, конструкторів, методів, нечленських функцій та суміжних концептів стандарту C++20/C++23.

## 1. Сигнатура шаблону та параметри

```cpp
namespace std {
    inline constexpr std::size_t dynamic_extent = std::numeric_limits<std::size_t>::max();

    template <typename ElementType, std::size_t Extent = std::dynamic_extent>
    class span;
}
```

### Параметри шаблону:
- `ElementType` — тип елементів, на які посилається зріз. Може бути константним (наприклад, `const int`) або модифікованим (`int`). Дозволяються лише повні типи об'єктів (не `void`, не функції, не абстрактні класи з незавершеними визначеннями).
- `Extent` — статична кількість елементів у зрізі. Значення за замовчуванням — `std::dynamic_extent`, що означає визначення довжини під час виконання програми.

Параметризований вибір `Extent` визначає структуру внутрішніх полів класу та оптимізації компілятора. Якщо `Extent == std::dynamic_extent`, об'єкт зберігає вказівник на дані та динамічний розмір. Якщо ж `Extent` є конкретним числом, об'єкт зберігає лише вказівник, а розмір обчислюється на стадії компіляції.

## 2. Вкладені типи та константи

Усередині класу `std::span` визначено такі псевдоніми типів та статичні константи, що забезпечують повну сумісність із концептами контейнерів та ітераторів STL:

| Вкладений тип / константа | Визначення / Тип | Опис |
| :--- | :--- | :--- |
| `element_type` | `ElementType` | Вихідний тип елемента з урахуванням `const` |
| `value_type` | `std::remove_cv_t<ElementType>` | Тип елемента без кваліфікаторів `const` та `volatile` |
| `size_type` | `std::size_t` | Беззнаковий тип для індексації та розміру |
| `difference_type` | `std::ptrdiff_t` | Знаковий тип для різниці вказівників |
| `pointer` | `ElementType*` | Вказівник на елемент пам'яті |
| `const_pointer` | `const ElementType*` | Константний вказівник на елемент пам'яті |
| `reference` | `ElementType&` | Посилання на елемент |
| `const_reference` | `const ElementType&` | Константне посилання на елемент |
| `iterator` | *implementation-defined* | Двонаправлений суцільний ітератор (`contiguous_iterator`) |
| `reverse_iterator` | `std::reverse_iterator<iterator>` | Зворотний ітератор |
| `extent` (константа) | `inline constexpr size_type extent` | Дорівнює `Extent` (параметру шаблону) |

Варто звернути увагу на відмінність між `element_type` та `value_type`. Якщо створення `std::span<const double>` дає `element_type` рівним `const double`, то `value_type` звільняється від кваліфікатора константності і дорівнює `double`. Це необхідно для сумісності з алгоритмами STL, які створюють локальні тимчасові змінні типу `value_type` під час копіювання чи обміну елементів.

## 3. Детальний аналіз конструкторів та умов SFINAE

`std::span` надає набір конструкторів, що охоплюють створення зрізів із будь-яких джерел суцільних даних. Кожен конструктор має чітко визначені умови SFINAE (`std::enable_if` або `requires`), які запобігають некоректному зв'язуванню типів.

```cpp
// 1. Конструктор за замовчуванням (тільки якщо Extent == 0 або dynamic_extent)
constexpr span() noexcept;

// 2. З двох ітераторів (first, count або first, last)
template <typename It>
constexpr explicit(Extent != std::dynamic_extent)
span(It first, size_type count);

template <typename It, typename End>
constexpr explicit(Extent != std::dynamic_extent)
span(It first, End last);

// 3. З C-масиву
template <std::size_t N>
constexpr span(element_type (&arr)[N]) noexcept;

// 4. З std::array
template <typename T, std::size_t N>
constexpr span(std::array<T, N>& arr) noexcept;

template <typename T, std::size_t N>
constexpr span(const std::array<T, N>& arr) noexcept;

// 5. З контейнерів (std::vector, std::string тощо) або довільних ranges
template <typename Rng>
constexpr explicit(Extent != std::dynamic_extent)
span(Rng&& range);

// 6. Конструктор конверсії з іншого span (наприклад, з модифікованого у const)
template <typename OtherElementType, std::size_t OtherExtent>
constexpr explicit(Extent != std::dynamic_extent && OtherExtent == std::dynamic_extent)
span(const span<OtherElementType, OtherExtent>& other) noexcept;
```

### Семантичні деталі конструкторів:

- **Конструктор за замовчуванням**: Створює порожній зріз із `data() == nullptr` та `size() == 0`. Цей конструктор бере участь у вирішенні перевантажень лише тоді, коли `Extent == 0` або `Extent == std::dynamic_extent`. Спроба викликати конструктор за замовчуванням для `std::span<int, 5>` призведе до помилки компіляції під час аналізу умов ініціалізації.
- **Конструктор з двох ітераторів**: Вимагає, щоб тип `It` задовольняв концепт `std::contiguous_iterator`, а `End` задовольняв `std::sized_sentinel_for<It>`. Якщо `Extent != std::dynamic_extent`, конструктор позначається як `explicit`, щоб запобігти неявним небезпечним конверсіям розмірів.
- **Конструктор з C-масиву та std::array**: Для статичних масивів розмірність `N` виводиться автоматично. Конструктор доступний лише якщо `Extent == std::dynamic_extent` або `Extent == N`, а тип елементів масиву сумісний за кваліфікаторами з `ElementType`.
- **Конструктор з довільного range (C++20/C++23)**: Дозволяє ініціалізувати `std::span` з будь-якого об'єкта, що задовольняє концепт `std::ranges::contiguous_range` та `std::ranges::sized_range`. Конструктор перевіряє, що вказівник `std::ranges::data(range)` сумісний із `ElementType*`.
- **Конструктор конверсії типів**: Дозволяє неявне перетворення модифікованого зрізу `std::span<int>` у константний зріз `std::span<const int>`. Натомість зворотне перетворення з константного у модифікований заборонено на рівні системи типів. Також заборонено перетворення між несумісними за розміром вказівниками (наприклад, `std::span<int*>` не перетворюється у `std::span<const int*>`, що запобігає порушенню правил константності через подвійні вказівники).

### Правила автоматичного виведення типів шаблону (Deduction Guides)

Завдяки спеціальним інструкціям виведення типів (англ. *deduction guides*) розробнику не потрібно вказувати параметри шаблону при ініціалізації `std::span` з локальних об'єктів:

```cpp
int C_array[10] = {0};
std::span s_array{C_array}; // Автоматично виводить std::span<int, 10>

std::vector<float> vec = {1.0f, 2.0f, 3.0f};
std::span s_vec{vec}; // Автоматично виводить std::span<float, std::dynamic_extent>

const std::array<char, 4> st_arr = {'a', 'b', 'c', 'd'};
std::span s_st{st_arr}; // Автоматично виводить std::span<const char, 4>
```

Автоматичне виведення для контейнерів типу `std::vector` завжди обирає `std::dynamic_extent`, оскільки розмір вектора може змінюватися під час виконання програми. Натомість для C-масивів та `std::array` обирається статичний `Extent`, що оптимізує розмір самого `std::span` до 8 байтів.

## 4. Операції доступу до елементів та спостереження

Методи доступу до даних надають прямий доступ до елементів масиву з мінімальними накладними витратами. Вони спроектовані з розрахунком на інлайнінг (англ. *inlining*) компілятором у пряму арифметику вказівників.

```cpp
// Повертає посилання на i-й елемент (без перевірки меж у release)
constexpr reference operator[](size_type idx) const;

// Повертає посилання на перший та останній елемент
constexpr reference front() const;
constexpr reference back() const;

// Повертає вказівник на початок масиву у пам'яті
constexpr pointer data() const noexcept;

// Кількість елементів у зрізі
constexpr size_type size() const noexcept;

// Загальний розмір масиву у байтах (size() * sizeof(element_type))
constexpr size_type size_bytes() const noexcept;

// Перевірка чи порожній зріз (size() == 0)
[[nodiscard]] constexpr bool empty() const noexcept;
```

### Деталі поведінки методів фронтального та кінцевого доступу:

- Метод `front()` повертає `*data()`. Якщо зріз порожній (`empty() == true`), виклик `front()` призводить до розіменування вказівника `nullptr` або недопустимої адреси, що є невизначеною поведінкою (UB).
- Метод `back()` повертає `*(data() + (size() - 1))`. Аналогічно вимагає, щоб `empty() == false`.
- Метод `size_bytes()` обчислює загальний обсяг пам'яті у байтах за формулою `size() * sizeof(element_type)`. Для статичного `Extent` значення `size_bytes()` є константою виразу `constexpr`.

### Філософія відсутності методу at()

Важливо підкреслити, що клас `std::span` свідомо **не містить** методу `at(size_type idx)`, який генерує виняток `std::out_of_range` при виході за межі. Це свідоме рішення комітету з стандартизації WG21, яке базується на трьох аргументах:

1. **Нульові накладні витрати (Zero-overhead principle)**: `std::span` спроектовано як низькорівневу заміни сирим вказівникам. Неявна генерування кодів винятків та відгалужень перевірок додає зайві машинні інструкції у гарячі цикли обробки даних.
2. **Перевірка меж у режимі налагодження**: Більшість реалізацій стандартної бібліотеки (GCC libstdc++, Clang libc++, MSVC STL) надають прапорці асертів налагодження (наприклад, `-D_GLIBCXX_ASSERTIONS`). При їх увімкненні оператор `operator[]` автоматично перевіряє умову `idx < size()` і перериває виконання програми при порушенні межі.
3. **Явний контроль у коді розробника**: Якщо бізнес-логіка вимагає перевірки меж з генерацією винятків, розробник має виконувати явну перевірку `if (idx >= span.size()) throw ...` або використовувати виклики `span.subspan()`.

## 5. Методи створення зрізів (Subspans)

`std::span` надає методи для вирізання піддіапазонів. Кожна з функцій існує у двох варіантах: зі статичним розміром (параметри шаблону) та динамічним розміром (аргументи функції).

```cpp
// 1. Перші N елементів
template <std::size_t Count>
constexpr span<element_type, Count> first() const;

constexpr span<element_type, std::dynamic_extent> first(size_type count) const;

// 2. Останні N елементів
template <std::size_t Count>
constexpr span<element_type, Count> last() const;

constexpr span<element_type, std::dynamic_extent> last(size_type count) const;

// 3. Піддіапазон починаючи з Pos розміром Count
template <std::size_t Offset, std::size_t Count = std::dynamic_extent>
constexpr auto subspan() const;

constexpr span<element_type, std::dynamic_extent> 
subspan(size_type offset, size_type count = std::dynamic_extent) const;
```

### Специфікація обчислення типів повернення для subspan():

При використанні шаблонної версії `subspan<Offset, Count>()` тип повернутого `std::span` обчислюється на етапі компіляції за наступними правилами:

- Якщо `Count != std::dynamic_extent`, повертається `std::span<element_type, Count>`.
- Якщо `Count == std::dynamic_extent`, але вихідний `Extent != std::dynamic_extent`, повертається статичний зріз `std::span<element_type, Extent - Offset>`.
- Якщо вихідний `Extent == std::dynamic_extent` і `Count == std::dynamic_extent`, повертається динамічний зріз `std::span<element_type, std::dynamic_extent>`.

Це дозволяє компілятору зберігати інформацію про статичний розмір навіть після серії послідовних зрізів буфера, що гарантує збереження 8-байтового макету пам'яті без динамічного лічильника довжини.

## 6. Безпечна байтова переінтерпретація: as_bytes та as_writable_bytes

Для низькорівневої обробки байтів замість небезпечних приведень `reinterpret_cast<const char*>` стандарт C++20 надає дві вільностоячі функції у просторі назв `std`:

```cpp
namespace std {
    template <typename ElementType, std::size_t Extent>
    span<const std::byte, 
         Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_bytes(span<ElementType, Extent> s) noexcept;

    template <typename ElementType, std::size_t Extent>
    requires (!std::is_const_v<ElementType>)
    span<std::byte, 
         Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_writable_bytes(span<ElementType, Extent> s) noexcept;
}
```

### Фізичний механізм роботи:

- `std::as_bytes(s)` приймає довільний `std::span<ElementType, Extent>` і повертає `std::span<const std::byte, NewExtent>`. Його призначення — надати безпечний перегляд сирих байтів об'єкта лише для читання (наприклад, для обчислення хешу або запису в сокет).
- `std::as_writable_bytes(s)` вимагає, щоб вихідний `ElementType` не був константним. Повернений зріз `std::span<std::byte, NewExtent>` дозволяє модифікувати байти об'єкта (наприклад, зчитувати дані безпосередньо з мережевого адаптера або з файлового дескриптора через `read()`).
- В обидвох випадках повернений зріз зберігає той самий вказівник `data()`, але його `size()` стає у `sizeof(ElementType)` разів більшим.

## 7. Концепти суцільної пам'яті C++20

`std::span` тісно пов'язаний із системою концептів діапазонів (Ranges Concepts) C++20.

### Концепт std::contiguous_iterator
```cpp
template <typename It>
concept contiguous_iterator = std::random_access_iterator<It> &&
    std::derived_from<typename std::iterator_traits<It>::iterator_category, 
                      std::contiguous_iterator_tag> &&
    requires(const It& i) {
        { std::to_address(i) } -> std::same_as<std::add_pointer_t<std::iter_reference_t<It>>>;
    };
```
Ітератор є `contiguous_iterator`, якщо елементи послідовності розміщені в пам'яті фізично суцільно, і адреса елемента обчислюється як `std::to_address(it + n) == std::to_address(it) + n`.

### Концепт std::ranges::contiguous_range
```cpp
template <typename R>
concept contiguous_range = std::ranges::random_access_range<R> &&
    std::contiguous_iterator<std::ranges::iterator_t<R>> &&
    requires(R& r) {
        { std::ranges::data(r) } -> std::same_as<std::add_pointer_t<std::ranges::range_reference_t<R>>>;
    };
```

### Концепт std::ranges::borrowed_range

Спеціалізація змінної-шаблону `std::ranges::enable_borrowed_range` вказує алгоритмам діапазонів, що ітератори даного типу залишаються валидними навіть після знищення самого об'єкта-діапазону:

```cpp
template <typename ElementType, std::size_t Extent>
inline constexpr bool std::ranges::enable_borrowed_range<std::span<ElementType, Extent>> = true;
```

Завдяки цьому `std::span` можна безпечно передавати у конвеєри діапазонів (англ. *ranges pipelines*), повертаючи ітератори у зовнішні функції без ризику блокування компілятором. Будь-який тип `R`, що задовольняє `std::ranges::contiguous_range` (наприклад, `std::vector`, `std::array`, `std::string_view`, `std::span`), може бути безпосередньо переданий у конструктор `std::span`.

## 8. Ітератори та підтримка зворотного обходу

`std::span` надає методи `begin()`, `end()`, `rbegin()`, `rend()`, `cbegin()`, `cend()`, `crbegin()`, `crend()`.

Ітератори, що повертаються методом `begin()`, мають категорію `std::contiguous_iterator_tag`. Їхня арифметика повністю еквівалентна арифметиці сирих вказівників: `it + n` переводиться компілятором у додавання `n * sizeof(ElementType)` до адреси.

Зворотні ітератори `rbegin()` реалізовані через шаблонну обгортку `std::reverse_iterator<iterator>`. Вони дозволяють обходити суцільний буфер від кінця до початку у зворотних циклах `for (auto it = span.rbegin(); it != span.rend(); ++it)`.
