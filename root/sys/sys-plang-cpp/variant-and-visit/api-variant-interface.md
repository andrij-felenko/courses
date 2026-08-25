# 📋 Повний довідник інтерфейсу std::variant та std::visit

Довідник містить повну специфікацію публічного інтерфейсу сигнатур, методів, вільних функцій, допоміжних метафункцій та винятків заголовочного файла `<variant>` стандартів C++17/20/23. Опис призначено для швидкого пошуку точних сигнатур, гарантій виняткобезпеки, правил виведення типів та вирівнювання пам'яті під час роботи з типом-сумою `std::variant`.

## 1. Основний шаблон класу std::variant

Шаблон класу `std::variant` являє собою статично типізований тип-суму (discriminated union) із гарантією розміщення вмісту безпосередньо всередині буфера пам'яті самого об'єкта.

```cpp
namespace std {
    template <typename... Types>
    class variant;
}
```

### Формальні обмеження на список альтернативних типів Types...:
1. **Заборона void:** Кожен тип `T_i` у списку альтернатив мусить бути не-`void` типом. Використання типів `void` прямо заборонено стандартом мови. Для представлення порожнього стану використовується спеціальний тип `std::monostate`.
2. **Заборона посилань та масивів невідомого розміру:** Заборонено безпосереднє використання типів посилань (`T&`, `const T&`, `T&&`), а також масивів невідомого розміру (`T[]`). Для збереження посилань розробник повинен використовувати обгортки `std::reference_wrapper<T>` або вказівники.
3. **Повторювані типи у списку:** Специфікація дозволяє наявність однакових типів у списку альтернатив (наприклад, `std::variant<int, int, std::string>`). У цьому випадку звернення до альтернатив за типом викликає помилку компіляції через неоднозначність вибору; доступ здійснюється виключно за цілочисельним індексом.
4. **Тривіальна руйнівність:** Шаблон класу гарантує тривіальну руйнівність (trivial destructibility), якщо кожен альтернативний тип `T_i` володіє тривіальним деструктором. У такому випадку деструктор варіанта не виконує жодних додаткових перевірок під час завершення життєвого циклу.

## 2. Конструктори та оператори присвоєння

Опис механізмів виклику конструкторів, правилах SFINAE-виведення типів та гарантій виняткобезпеки:

### Конструктор за замовчуванням
```cpp
constexpr variant() noexcept(...);
```
Ініціалізує першу альтернативу `T_1` за допомогою її конструктора за замовчуванням. Конструктор позначено як `noexcept`, якщо вираз `std::is_nothrow_default_constructible_v<T_1>` дорівнює `true`. Виклик даного конструктора заборонено компілятором (SFINAE / constraints disabled), якщо тип `T_1` не має конструктора за замовчуванням.

### Конструктор копіювання
```cpp
constexpr variant(const variant& rhs);
```
Визначає поточний індекс `rhs.index()`, після чого виконує копіювання активної альтернативи за допомогою її конструктора копіювання. Якщо `rhs.valueless_by_exception()` дорівнює `true`, новий варіант також створюється у стані `valueless`. Конструктор є тривіальним, якщо всі альтернативні типи підтримують тривіальне копіювання.

### Конструктор переміщення
```cpp
constexpr variant(variant&& rhs) noexcept(...);
```
Визначає поточний індекс `rhs.index()` та переміщує активну альтернативу `rhs` у внутрішній буфер нового об'єкта. Позначається `noexcept`, якщо кожен тип `T_i` у списку альтернатив має `noexcept` конструктор переміщення.

### Конструктор ініціалізації значенням (Converting Constructor)
```cpp
template <typename T>
constexpr variant(T&& t) noexcept(...);
```
За допомогою складних правил розв'язання перевантажень (Overload Resolution) компілятор вибирає єдину альтернативу `T_j`, для якої вираз `T_j x[] = {std::forward<T>(t)};` є коректним. Якщо існує кілька однакових типів або декілька альтернатив дозволяють неявне перетворення з однаковим пріоритетом, виклик завершується помилкою компіляції через неоднозначність.

### Конструювання за типом або індексом за місцем (In-Place Construction)
```cpp
template <typename T, typename... Args>
constexpr explicit variant(in_place_type_t<T>, Args&&... args);

template <size_t I, typename... Args>
constexpr explicit variant(in_place_index_t<I>, Args&&... args);
```
Прямо викликає конструктор відповідного типу `T` або альтернативи за індексом `I` у внутрішньому буфері варіанта із передачею параметрів `std::forward<Args>(args)...`. Унеможливлює виконання будь-яких тимчасових копіювань чи переміщень об'єкта.

### Деструктор
```cpp
~variant();
```
Перевіряє поточний індекс дискримінатора. Якщо варіант перебуває у валідному стані (`index() != variant_npos`), викликає деструктор `~T_i()` для поточного активного об'єкта. Якщо варіант є `valueless_by_exception()`, деструктор не виконує жодних дій.

### Оператори присвоєння
```cpp
variant& operator=(const variant& rhs);
variant& operator=(variant&& rhs) noexcept(...);
```
Якщо по поточні індекси `index()` та `rhs.index()` збігаються, виконується оператор присвоєння для активного типу. Якщо індекси різні, об'єкт спочатку знищує поточний вміст, а потім створює новий об'єкт через копіювання або переміщення. При виникненні винятку у процесі конструювання об'єкт переходить у стан `valueless_by_exception()`.

## 3. Методи елемента класу

### index
```cpp
constexpr size_t index() const noexcept;
```
Повертає цілочисельний індекс `0..N-1` поточного активного типу у списку `Types...`. Якщо об'єкт втратив значення внаслідок виклику винятку під час операції присвоєння, метод повертає константу `std::variant_npos`.

### valueless_by_exception
```cpp
constexpr bool valueless_by_exception() const noexcept;
```
Повертає `true`, якщо об'єкт перебуває в невалідному стані. Це відбувається виключно тоді, коли під час виконання операції присвоєння нової альтернативи деструктор попереднього об'єкта вже знищив старий вміст, а конструктор нового об'єкта кинув виняток.

### emplace
```cpp
template <typename T, typename... Args>
constexpr T& emplace(Args&&... args);

template <size_t I, typename... Args>
constexpr variant_alternative_t<I, variant>& emplace(Args&&... args);
```
Знищує поточну альтернативу (якщо вона була ініціалізована) та створює нову альтернативу типу `T` або за індексом `I` безпосередньо у внутрішньому буфері пам'яті об'єкта. Повертає модифіковуване посилання на щойно створений об'єкт. Якщо конструктор нового типу кидає виняток, об'єкт переходить у стан `valueless_by_exception()`.

### swap
```cpp
constexpr void swap(variant& rhs) noexcept(...);
```
Обмінює вміст двох варіантів. Механіка обміну розрізняє наступні ситуації:
- Якщо індекси двох варіантів збігаються (`index() == rhs.index()`), викликається `using std::swap; swap(get<I>(*this), get<I>(rhs))`.
- Якщо індекси різні, вміст обмінюється через тимчасову переміщувальну копію з використанням `std::move`.
- Якщо один із варіантів є `valueless_by_exception()`, значення переношується у невалідний варіант, а перший об'єкт стає `valueless`.

## 4. Вільні функції доступу (Non-member Accessors)

### std::holds_alternative
```cpp
template <typename T, typename... Types>
constexpr bool holds_alternative(const variant<Types...>& v) noexcept;
```
Повертає `true` тоді й лише тоді, коли `v.index()` збігається з індексом типу `T` у списку `Types...`. Якщо тип `T` не входить до списку `Types...` або зустрічається там декілька разів, виклик призводить до помилки компіляції під час аналізу типів.

### std::get
```cpp
template <typename T, typename... Types>
constexpr T& get(variant<Types...>& v);

template <typename T, typename... Types>
constexpr const T& get(const variant<Types...>& v);

template <typename T, typename... Types>
constexpr T&& get(variant<Types...>&& v);

template <size_t I, typename... Types>
constexpr variant_alternative_t<I, variant<Types...>>& get(variant<Types...>& v);

template <size_t I, typename... Types>
constexpr const variant_alternative_t<I, variant<Types...>>& get(const variant<Types...>& v);
```
Здійснює прямий доступ до значення за типом або індексом. Повертає посилання на активну альтернативу. Якщо індекс запитуваного типу не збігається з `v.index()`, або якщо варіант перебуває у стані `valueless_by_exception()`, функція викидає виняток `std::bad_variant_access`.

### std::get_if
```cpp
template <typename T, typename... Types>
constexpr add_pointer_t<T> get_if(variant<Types...>* pv) noexcept;

template <typename T, typename... Types>
constexpr add_pointer_t<const T> get_if(const variant<Types...>* pv) noexcept;

template <size_t I, typename... Types>
constexpr add_pointer_t<variant_alternative_t<I, variant<Types...>>>
get_if(variant<Types...>* pv) noexcept;
```
Безвинятковий аналог `std::get`. Приймає вказівник на `variant`. Якщо вказівник `pv` не дорівнює `nullptr` і `pv->index()` відповідає запропонованому типу `T` або індексу `I`, повертає вказівник на внутрішній об'єкт. У протилежному випадку повертає `nullptr`. Функція позначена як `noexcept` і гарантує відсутність будь-яких винятків під час виконання.

## 5. Допоміжні класи та метафункції

```cpp
// Отримання кількості альтернатив у варіанті на етапі компіляції
template <typename T> struct variant_size;

template <typename... Types>
struct variant_size<variant<Types...>> : std::integral_constant<size_t, sizeof...(Types)> {};

template <typename T>
inline constexpr size_t variant_size_v = variant_size<T>::value;

// Отримання типу альтернативи за її індексом I
template <size_t I, typename T> struct variant_alternative;

template <size_t I, typename T>
using variant_alternative_t = typename variant_alternative<I, T>::type;

// Константа порожнього або невалідного стану
inline constexpr size_t variant_npos = -1;
```

Метафункція `std::variant_alternative_t<I, VariantType>` дозволяє отримувати точний тип `I`-ї альтернативи під час компіляції у шаблонних алгоритмах та утилітах метапрограмування.

## 6. Клас std::monostate та оператори порівняння

Клас `std::monostate` слугує явним маркером порожнього стану у варіантах, перша альтернатива яких не підтримує конструктор за замовчуванням.

```cpp
namespace std {
    struct monostate {};

    constexpr bool operator==(monostate, monostate) noexcept { return true; }
    constexpr bool operator!=(monostate, monostate) noexcept { return false; }
    constexpr bool operator<(monostate, monostate) noexcept { return false; }
    constexpr bool operator>(monostate, monostate) noexcept { return false; }
    constexpr bool operator<=(monostate, monostate) noexcept { return true; }
    constexpr bool operator>=(monostate, monostate) noexcept { return true; }
    constexpr strong_ordering operator<=>(monostate, monostate) noexcept {
        return strong_ordering::equal;
    }
}
```

### Логіка виконання операторів порівняння двох варіантів:
При виконанні `v1 == v2` алгоритм діє наступним чином:
1. Якщо `v1.index() != v2.index()`, повертає `false`.
2. Якщо `v1.valueless_by_exception()`, повертає `true` лише за умови, що `v2.valueless_by_exception()` також дорівнює `true`.
3. Якщо індекси збігаються і варіанти валідні, делегує порівняння активним альтернативам: `std::get<I>(v1) == std::get<I>(v2)`.

При виконанні оператора лексикографічного порівняння `v1 < v2` варіант з меншим індексом `v1.index() < v2.index()` вважається меншим. Стан `valueless_by_exception()` вважається меншим за будь-який валідний індекс `0..N-1`.

## 7. Функція мульти-диспетчеризації std::visit

Функція `std::visit` виконує статичну або динамічну диспетчеризацію виклику перевантаженого об'єкта `Visitor` для поточних активних типів одного або кількох варіантів.

```cpp
// C++17 / C++20: Автоматичне виведення типу повернення
template <typename Visitor, typename... Variants>
constexpr decltype(auto) visit(Visitor&& vis, Variants&&... vars);

// C++23: Явне вказання типу повернення R
template <typename R, typename Visitor, typename... Variants>
constexpr R visit(Visitor&& vis, Variants&&... vars);
```

### Правила та вимоги до реалізації Visitor:
- Функціональний об'єкт `vis` повинен мати оператор виклику `operator()`, який є валідним для будь-якої комбінації активних типів, що можуть міститися у `vars...`.
- У C++17/20 всі можливі гілки виклику `vis(get<I_1>(v_1), get<I_2>(v_2), ...)` мусять повертати однакові типи або типи, що зводяться до єдиного спільного типу (Common Type). Повернення несумісних типів викликає помилку компіляції під час аналізу шаблонних виразів.
- У C++23 сигнатура `std::visit<R>` дозволяє явно вказати цільовий тип повернення `R`. Результат кожної гілки неявно приводиться до `R`, що знімає вимогу суворого збігу типів повернення у лямбда-виразах.
- Якщо хоча б один із переданих варіантів `v_k` перебуває у стані `valueless_by_exception()`, функція `std::visit` відразу викидає виняток `std::bad_variant_access`.

## 8. Клас винятків std::bad_variant_access

```cpp
namespace std {
    class bad_variant_access : public std::exception {
    public:
        bad_variant_access() noexcept;
        virtual const char* what() const noexcept override;
    };
}
```

Виняток `std::bad_variant_access` походить від `std::exception`. Метод `what()` повертає реалізаційно-залежний рядок із описом помилки невалідного доступу до варіанта.

## 9. Геометрія пам'яті та вимоги до системного вирівнювання

Компілятор будує структуру `std::variant` у пам'яті із дотриманням наступних вимог до розміру та вирівнювання:

```cpp
// Розмір буфера об'єкта у пам'яті
sizeof(std::variant<Types...>) >= max(sizeof(Types)...) + sizeof(discriminator_type);

// Кордон вирівнювання об'єкта
alignof(std::variant<Types...>) == max(alignof(Types)...);
```

Дискримінатор `discriminator_type` обирається реалізацією стандартної бібліотеки як найменший цілочисельний беззнаковий тип (`uint8_t`, `uint16_t` або `size_t`), спроможний вмістити кількість альтернатив `N` плюс стан `valueless`. Для зменшення загального розміру об'єкта компілятор може пакувати дискримінатор у порожні байти вирівнювання (padding bytes) між альтернативами.
