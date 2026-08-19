# Довідник стандартної бібліотеки та макросів C++23

Довідник містить нормативні описи інтерфейсів, сигнатури словникових типів, контрактні вимоги адаптерів контейнерів та макроси тестування можливостей (англ. *Feature Test Macros*), закріплені міжнародним стандартом ISO/IEC 14882:2024 (C++23).

Кожна нова можливість ядра або бібліотеки супроводжується власним макросом у системному заголовку `<version>`, що дозволяє перевіряти підтримку на етапі препроцесора без жорсткої прив'язки до версії чи назви конкретного компілятора.

## Макроси тестування можливостей (Feature-Test Macros)

У таблиці наведено системні макроси ядра мови та стандартної бібліотеки, їхні числові значення у форматі `РРРРММL` та відповідний номер нормативного документа робочої групи WG21. Значення макроса кодує рік і місяць прийняття остаточної ревізії паперу:

| Макрос | Значення C++23 | Документ WG21 | Призначення та семантика |
|---|---|---|---|
| `__cpp_explicit_this_parameter` | `202110L` | P0847R7 | Явний параметр об'єкта (`this Self&& self`, Deducing this) |
| `__cpp_multidimensional_subscript` | `202110L` | P2128R6 | Багатовимірний оператор індексації `operator[](i, j, ...)` |
| `__cpp_auto_cast` | `202110L` | P0849R8 | Вирази явного копіювання prvalue `auto(x)` та `auto{x}` |
| `__cpp_if_consteval` | `202106L` | P1938R3 | Інструкція розгалуження `if consteval` замість `is_constant_evaluated()` |
| `__cpp_size_t_suffix` | `202011L` | P0330R8 | Літеральні суфікси `uz` та `z` для `size_t` та знакового аналога |
| `__cpp_constexpr` | `202211L` | P2647R1 | Дозвіл `static`/`thread_local` змінних у невиконуваних constexpr гілках |
| `__cpp_static_assert` | `202306L` | P2741R3 | Форматовані повідомлення у `static_assert(cond, message)` |
| `__cpp_lib_expected` | `202202L` | P0323R12 | Словниковий тип `std::expected<T, E>` та `std::unexpected<E>` |
| `__cpp_lib_print` | `202209L` | P2093R14 | Функції виводу `std::print` та `std::println` у `<print>` |
| `__cpp_lib_mdspan` | `202207L` | P0009R18 | Багатовимірний неволодіючий вид `std::mdspan` у `<mdspan>` |
| `__cpp_lib_flat_map` | `202207L` | P0429R9 | Неперервний асоціативний адаптер `std::flat_map` |
| `__cpp_lib_flat_set` | `202207L` | P1222R4 | Неперервний асоціативний адаптер `std::flat_set` |
| `__cpp_lib_generator` | `202207L` | P2502R2 | Корутинний лінивий генератор `std::generator<T>` |
| `__cpp_lib_stacktrace` | `202011L` | P0881R7 | Захоплення та інспекція стека викликів `<stacktrace>` |
| `__cpp_lib_monadic_optional` | `202110L` | P0798R8 | Монадичні методи `and_then`, `transform`, `or_else` у `std::optional` |
| `__cpp_lib_move_only_function` | `202110L` | P0288R9 | Обгортка виклику `std::move_only_function` без вимоги копіювання |
| `__cpp_lib_forward_like` | `202207L` | P2445R1 | Утиліта передачі кваліфікаторів `std::forward_like<Owner>(member)` |
| `__cpp_lib_to_underlying` | `202102L` | P1682R3 | Отримання базового цілого значення `std::to_underlying(enum_val)` |
| `__cpp_lib_unreachable` | `202202L` | P0627R6 | Підказка компілятору `std::unreachable()` про недосяжну гілку |
| `__cpp_lib_byteswap` | `202110L` | P1272R4 | Реверс байтів `std::byteswap(val)` для конвертації endianness |
| `__cpp_lib_ranges_zip` | `202110L` | P2321R2 | Адаптери діапазонів `views::zip`, `views::zip_transform`, `views::adjacent` |
| `__cpp_lib_ranges_chunk` | `202202L` | P2441R2 | Адаптер розбиття діапазону на блоки `views::chunk` |
| `__cpp_lib_ranges_slide` | `202202L` | P2442R1 | Адаптер ковзного вікна `views::slide` |
| `__cpp_lib_ranges_stride` | `202207L` | P1899R3 | Адаптер кроку перебору `views::stride` |
| `__cpp_lib_ranges_cartesian_product` | `202207L` | P2374R4 | Декартів добуток послідовностей `views::cartesian_product` |
| `__cpp_lib_ranges_join_with` | `202202L` | P2446R2 | Об'єднання діапазонів з роздільником `views::join_with` |
| `__cpp_lib_ranges_contains` | `202207L` | P2302R4 | Алгоритми `ranges::contains` та `ranges::contains_subrange` |
| `__cpp_lib_ranges_find_last` | `202207L` | P1223R5 | Алгоритми `ranges::find_last`, `find_last_if`, `find_last_if_not` |
| `__cpp_lib_ranges_iota` | `202202L` | P2440R1 | Алгоритм генерації послідовності `ranges::iota` |
| `__cpp_lib_ranges_fold` | `202207L` | P2322R6 | Функціональні згортки `ranges::fold_left`, `ranges::fold_right` |
| `__cpp_lib_ranges_as_rvalue` | `202207L` | P2446R2 | Адаптер приведення елементів до xvalue `views::as_rvalue` |
| `__cpp_lib_ranges_repeat` | `202207L` | P2474R2 | Генератор нескінченного або фіксованого повторення `views::repeat` |
| `__cpp_lib_ranges_enumerate` | `202302L` | P2164R9 | Адаптер індексації елементів `views::enumerate` |
| `__cpp_lib_ranges_as_const` | `202207L` | P2278R4 | Адаптер представлення елементів як константних `views::as_const` |
| `__cpp_lib_spanstream` | `202106L` | P0448R4 | Неалокуючі рядкові потоки `std::spanstream` у `<spanstream>` |
| `__cpp_lib_string_contains` | `202011L` | P1679R2 | Метод перевірки підрядка `basic_string::contains` та `string_view::contains` |

## Нові заголовки стандартної бібліотеки

У стандарті C++23 додано дев'ять обов'язкових заголовкових файлів, кожен із яких розв'язує окрему системну задачу:

1. **`<expected>`** — впроваджує тип-суму `std::expected<T, E>`, допоміжний клас `std::unexpected<E>` та клас винятку `std::bad_expected_access<E>`. Призначений для детермінованої обробки очікуваних збоїв без генерації винятків та динамічних виділень пам'яті.
2. **`<print>`** — містить функції прямого форматованого виводу `std::print`, `std::println`, а також низькорівневі точки входу `std::vprint_unicode` та `std::vprint_nonunicode`. Працює безпосередньо з системними дескрипторами операційної системи.
3. **`<mdspan>`** — надає неволодіючу багатовимірну обгортку `std::mdspan`, структури екстентів `std::extents`, політики проекції координат `std::layout_right`, `std::layout_left`, `std::layout_stride` та аксесори пам'яті.
4. **`<flat_map>`** — реалізує адаптери асоціативних контейнерів `std::flat_map` та `std::flat_multimap`, побудовані на двох паралельних векторах ключів і значень для максимального використання кеш-ліній процесора.
5. **`<flat_set>`** — реалізує адаптери множин `std::flat_set` та `std::flat_multiset` поверх єдиного відсортованого вектора.
6. **`<generator>`** — надає корутинний тип `std::generator<T>`, що реалізує концепт вхідного діапазону `std::ranges::input_range` і дозволяє ліниво продукувати елементи через інструкцію `co_yield`.
7. **`<stacktrace>`** — відкриває доступ до інспекції поточного стека викликів через класи `std::stacktrace` та `std::stacktrace_entry` без використання платформозалежних API (таких як `backtrace` у glibc чи `CaptureStackBackTrace` у Win32).
8. **`<stdfloat>`** — закріплює псевдоніми типів чисел із плаваючою крапкою строгої бінарної ширини за стандартом IEEE 754: `std::float16_t`, `std::float32_t`, `std::float64_t`, `std::float128_t` та тип машинного навчання `std::bfloat16_t`.
9. **`<spanstream>`** — забезпечує потокове форматування введення й виводу (`std::spanstream`, `std::ispanstream`, `std::ospanstream`) поверх користувацького фіксованого буфера пам'яті без динамічних алокацій у купі.

## Інтерфейс та семантика std::expected<T, E>

Словниковий тип `std::expected<T, E>` є типом-сумою (англ. *sum type*), який у будь-який момент часу містить або значення очікуваного типу `T`, або значення неочікуваного типу `E`. Пам'ять під обидва типи розміщується у внутрішньому неіменованому об'єднанні (`union`), що гарантує відсутність додаткових алокацій у динамічній пам'яті.

Розмір об'єкта `sizeof(std::expected<T, E>)` дорівнює максимальному розміру між `sizeof(T)` та `sizeof(E)` плюс розмір булевого дискримінатора та вирівнювання:

```cpp
namespace std {

template <class E>
class unexpected {
public:
    constexpr unexpected(const unexpected&) = default;
    constexpr unexpected(unexpected&&) = default;
    template <class... Args>
    constexpr explicit unexpected(in_place_t, Args&&... args);
    constexpr explicit unexpected(E e);

    constexpr const E& error() const & noexcept;
    constexpr E& error() & noexcept;
    constexpr const E&& error() const && noexcept;
    constexpr E&& error() && noexcept;

    constexpr void swap(unexpected& other) noexcept(is_nothrow_swappable_v<E>);
};

template <class T, class E>
class expected {
public:
    using value_type = T;
    using error_type = E;
    using unexpected_type = unexpected<E>;

    // Конструктори
    constexpr expected();
    constexpr expected(const expected&);
    constexpr expected(expected&&) noexcept(/* ... */);
    template <class U = T>
    constexpr explicit(/* ... */) expected(U&& v);
    template <class G>
    constexpr explicit(/* ... */) expected(const unexpected<G>& e);
    template <class G>
    constexpr explicit(/* ... */) expected(unexpected<G>&& e);

    // Спостереження стану
    constexpr bool has_value() const noexcept;
    constexpr explicit operator bool() const noexcept;

    // Доступ до значення
    constexpr const T& value() const &;
    constexpr T& value() &;
    constexpr const T&& value() const &&;
    constexpr T&& value() &&;

    // Доступ до помилки
    constexpr const E& error() const & noexcept;
    constexpr E& error() & noexcept;
    constexpr const E&& error() const && noexcept;
    constexpr E&& error() && noexcept;

    // Альтернативні значення
    template <class U>
    constexpr T value_or(U&& default_value) const &;
    template <class U>
    constexpr T value_or(U&& default_value) &&;

    // Монадичні операції конвеєра
    template <class F>
    constexpr auto and_then(F&& f) &;
    template <class F>
    constexpr auto and_then(F&& f) const &;
    template <class F>
    constexpr auto and_then(F&& f) &&;
    template <class F>
    constexpr auto and_then(F&& f) const &&;

    template <class F>
    constexpr auto transform(F&& f) &;
    template <class F>
    constexpr auto transform(F&& f) const &;
    template <class F>
    constexpr auto transform(F&& f) &&;
    template <class F>
    constexpr auto transform(F&& f) const &&;

    template <class F>
    constexpr auto or_else(F&& f) &;
    template <class F>
    constexpr auto or_else(F&& f) const &;
    template <class F>
    constexpr auto or_else(F&& f) &&;
    template <class F>
    constexpr auto or_else(F&& f) const &&;

    template <class F>
    constexpr auto transform_error(F&& f) &;
    template <class F>
    constexpr auto transform_error(F&& f) const &;
    template <class F>
    constexpr auto transform_error(F&& f) &&;
    template <class F>
    constexpr auto transform_error(F&& f) const &&;
};

// Спеціалізація для void (коли операція не продукує результату при успіху)
template <class E>
class expected<void, E> {
public:
    using value_type = void;
    using error_type = E;
    using unexpected_type = unexpected<E>;

    constexpr expected() noexcept;
    constexpr void value() const; // генерує bad_expected_access<E>, якщо помилка
    constexpr const E& error() const & noexcept;
    constexpr E& error() & noexcept;
    constexpr const E&& error() const && noexcept;
    constexpr E&& error() && noexcept;

    constexpr bool has_value() const noexcept;
    constexpr explicit operator bool() const noexcept;
};

} // namespace std
```

### Контрактні вимоги та поведінка методів доступу

1. **`value()`:** Якщо об'єкт містить успішне значення, метод повертає пряме посилання на `T` (з відповідною константністю та категорією значення). Якщо ж об'єкт містить помилку `E`, метод генерує виняток `std::bad_expected_access<E>`, що містить копію або посилання на збережений об'єкт помилки.
2. **`operator*` та `operator->`:** Пряме розіменування не виконує жодних перевірок наявності значення. Виклик цих операторів для об'єкта, що містить помилку, є невизначеною поведінкою (Undefined Behavior). Застосовується в критичних до швидкодії ділянках після явної перевірки `if (exp)`.
3. **`error()`:** Повертає посилання на збережену помилку `E`. Виклик для об'єкта, що містить валідне значення, є невизначеною поведінкою.
4. **`value_or(default_val)`:** Якщо об'єкт містить значення, повертає копію або переміщене значення `T`. В іншому разі повертає сконструйоване або приведене значення за замовчуванням `default_val`. Обчислення `default_val` виконується завжди під час передачі аргументу, тому для лінивих обчислень слід використовувати монадичний метод `or_else`.

### Монадичні правила перетворення типів

- **`and_then(F)`:** Приймає функціональний об'єкт `F`, що викликається як `std::invoke(std::forward<F>(f), value())`. Тип результату `F` повинен бути спеціалізацією `std::expected<U, E>` з тим самим типом помилки `E`. Якщо початковий об'єкт містить помилку, функція `F` не викликається, а повертається новий `std::expected<U, E>`, ініціалізований вихідною помилкою.
- **`transform(F)`:** Приймає функціональний об'єкт `F`, що повертає звичайне значення `U` (не `expected`). Метод автоматично конструює `std::expected<U, E>`, загортаючи результат виклику `F(value())`. Якщо початковий об'єкт містить помилку, вона транслюється в результат без виклику `F`.
- **`or_else(F)`:** Викликається лише у випадку збою з аргументом `error()`. Функція `F` повинна повертати `std::expected<T, G>`. Дозволяє змінити тип помилки на `G` або відновити успішне значення `T`.
- **`transform_error(F)`:** Викликається лише у випадку збою. Функція `F` перетворює об'єкт помилки `E` на новий тип помилки `G` (де `G` не є `expected`), автоматично загортаючи його в `std::expected<T, G>`.

## Монадичні розширення std::optional<T>

Для усунення глибокої вкладеності умовних конструкцій `if (opt.has_value())` до класу `std::optional<T>` додано три нормативні монадичні операції. Вони дозволяють з'єднувати виклики функцій у неперервний ланцюг обробки значень:

```cpp
namespace std {

template <class T>
class optional {
public:
    // and_then: викликає f(*this), якщо значення є; f повинна повертати std::optional<U>
    template <class F>
    constexpr auto and_then(F&& f) &;
    template <class F>
    constexpr auto and_then(F&& f) const &;
    template <class F>
    constexpr auto and_then(F&& f) &&;
    template <class F>
    constexpr auto and_then(F&& f) const &&;

    // transform: викликає f(*this), якщо значення є; загортає результат U у std::optional<U>
    template <class F>
    constexpr auto transform(F&& f) &;
    template <class F>
    constexpr auto transform(F&& f) const &;
    template <class F>
    constexpr auto transform(F&& f) &&;
    template <class F>
    constexpr auto transform(F&& f) const &&;

    // or_else: викликає f(), якщо значення відсутнє; f повинна повертати std::optional<T>
    template <class F>
    constexpr optional<T> or_else(F&& f) const &;
    template <class F>
    constexpr optional<T> or_else(F&& f) &&;
};

} // namespace std
```

### Відмінності між and_then, transform та or_else

- **`and_then(F)`:** Застосовується, коли сама функція-трансформатор `F` може завершитися невдачею і повертає `std::optional<U>`. Якщо початковий опціонал порожній, функція `F` взагалі не викликається, а результат ланцюга стає `std::nullopt`.
- **`transform(F)`:** Застосовується, коли функція `F` завжди успішна і повертає звичайне значення `U`. Метод автоматично загортає результат виклику в `std::optional<U>`. Якщо вхідний опціонал порожній, повертається порожній `std::optional<U>`.
- **`or_else(F)`:** Спрацьовує виключно у разі відсутності значення в початковому об'єкті. Дозволяє надати резервне джерело даних або виконати ліниву ініціалізацію іншим опціоналом.

## Інтерфейс std::mdspan та політики проекції координат

Шаблонний клас `std::mdspan` є неволодіючим багатовимірним представленням неперервного масиву байтів або типізованих елементів. На відміну від класичних вкладених масивів C++, `std::mdspan` відокремлює логічну форму тензора від фізичного розміщення в пам'яті.

Внутрішня архітектура `std::mdspan` складається з чотирьох параметрів шаблону:
1. **`ElementType`** — тип елементів масиву (наприклад, `double`, `const float`, `int32_t`).
2. **`Extents`** — спеціалізація шаблону `std::extents`, що описує кількість вимірів (ранг) та їхні фіксовані або динамічні розміри.
3. **`LayoutPolicy`** — політика обчислення зміщення елемента за його багатовимірними координатами `(i, j, k, ...)`.
4. **`AccessorPolicy`** — політика розіменування покажчика (дозволяє створювати види на пам'ять графічних прискорювачів GPU, пам'ять з атомарним доступом або пам'ять із контролем діапазонів).

```cpp
namespace std {

inline constexpr size_t dynamic_extent = numeric_limits<size_t>::max();

template <class IndexType, size_t... Extents>
class extents {
public:
    using index_type = IndexType;
    using size_type = size_t;
    using rank_type = size_t;

    static constexpr rank_type rank() noexcept { return sizeof...(Extents); }
    static constexpr rank_type rank_dynamic() noexcept;

    static constexpr size_t static_extent(rank_type r) noexcept;
    constexpr index_type extent(rank_type r) const noexcept;
};

// Зручні псевдоніми для вимірів фіксованого рангу
template <class IndexType, size_t Rank>
using dextents = /* extents з усіма dynamic_extent */;

// Стандартні політики розкладки
struct layout_right {
    template <class Extents> class mapping; // Рядок за рядком (C-style)
};

struct layout_left {
    template <class Extents> class mapping; // Стовпчик за стовпчиком (Fortran-style)
};

struct layout_stride {
    template <class Extents> class mapping; // Довільний фіксований крок для кожного виміру
};

template <
    class ElementType,
    class Extents,
    class LayoutPolicy = layout_right,
    class AccessorPolicy = default_accessor<ElementType>
>
class mdspan {
public:
    using extents_type = Extents;
    using layout_type = LayoutPolicy;
    using accessor_type = AccessorPolicy;
    using mapping_type = typename layout_type::template mapping<extents_type>;
    using element_type = ElementType;
    using value_type = remove_cv_t<element_type>;
    using index_type = typename extents_type::index_type;
    using size_type = typename extents_type::size_type;
    using rank_type = typename extents_type::rank_type;
    using data_handle_type = typename accessor_type::data_handle_type;
    using reference = typename accessor_type::reference;

    // Конструктори
    constexpr mdspan();
    constexpr mdspan(data_handle_type p, const extents_type& ext);
    template <class... IndexTypes>
    constexpr explicit mdspan(data_handle_type p, IndexTypes... dynamic_exts);
    constexpr mdspan(data_handle_type p, const mapping_type& m);
    constexpr mdspan(data_handle_type p, const mapping_type& m, const accessor_type& a);

    // Багатовимірний оператор індексації C++23
    template <class... IndexTypes>
    constexpr reference operator[](IndexTypes... indices) const noexcept;

    // Інспекція властивостей
    static constexpr rank_type rank() noexcept { return extents_type::rank(); }
    static constexpr rank_type rank_dynamic() noexcept { return extents_type::rank_dynamic(); }
    static constexpr size_t static_extent(rank_type r) noexcept { return extents_type::static_extent(r); }
    constexpr index_type extent(rank_type r) const noexcept { return extents_.extent(r); }
    constexpr size_type size() const noexcept;
    constexpr bool empty() const noexcept;

    constexpr data_handle_type data_handle() const noexcept;
    constexpr const mapping_type& mapping() const noexcept;
    constexpr const accessor_type& accessor() const noexcept;
};

} // namespace std
```

### Математичні формули проекції координат

- **`layout_right` (C-порядок):** Елементи останнього виміру розташовані неперервно в пам'яті. Для тривимірного масиву розміром `(D0, D1, D2)` зміщення розраховується як:
  ```
  Offset(i, j, k) = i · (D1 · D2) + j · D2 + k
  ```
- **`layout_left` (Fortran-порядок):** Елементи першого виміру розташовані неперервно. Застосовується для прямої сумісності з лінійними бібліотеками BLAS/LAPACK:
  ```
  Offset(i, j, k) = i + j · D0 + k · (D0 · D1)
  ```
- **`layout_stride` (Довільний крок):** Кожен вимір має власний множник кроку `Stride[r]`:
  ```
  Offset(i, j, k) = i · Stride[0] + j · Stride[1] + k · Stride[2]
  ```

## Інтерфейс плоских асоціативних контейнерів std::flat_map та std::flat_set

Класи `std::flat_map` та `std::flat_set` є контейнерними адаптерами. На відміну від вузлових дерев пошуку `std::map` (червоно-чорні дерева), плоскі структури зберігають елементи у звичайних неперервних масивах.

Внутрішня організація `std::flat_map` використовує два окремих вектори: один для ключів (`vector<Key>`), другий для значень (`vector<T>`). Це забезпечує максимальну щільність пакування ключів у пам'яті та дозволяє алгоритму бінарного пошуку `std::lower_bound` завантажувати лише масив ключів без засмічення кеш-ліній процесора значеннями:

```cpp
namespace std {

template <
    class Key,
    class T,
    class Compare = less<Key>,
    class KeyContainer = vector<Key>,
    class MappedContainer = vector<T>
>
class flat_map {
public:
    using key_type = Key;
    using mapped_type = T;
    using value_type = pair<key_type, mapped_type>;
    using key_compare = Compare;
    using key_container_type = KeyContainer;
    using mapped_container_type = MappedContainer;
    using size_type = size_t;
    using difference_type = ptrdiff_t;
    using reference = pair<const key_type&, mapped_type&>;
    using const_reference = pair<const key_type&, const mapped_type&>;

    struct containers {
        key_container_type keys;
        mapped_container_type values;
    };

    // Конструктори
    flat_map();
    explicit flat_map(const Compare& comp);
    flat_map(key_container_type keys, mapped_container_type values, const Compare& comp = Compare());

    // Вилучення та заміна базових векторів
    containers extract() &&;
    void replace(key_container_type keys, mapped_container_type values);

    // Доступ до елементів за ключем
    mapped_type& at(const key_type& k);
    const mapped_type& at(const key_type& k) const;
    mapped_type& operator[](const key_type& k);
    mapped_type& operator[](key_type&& k);

    // Операції пошуку O(log N)
    iterator find(const key_type& k);
    const_iterator find(const key_type& k) const;
    bool contains(const key_type& k) const;
    size_type count(const key_type& k) const;

    // Вставка зі збереженням сортування O(N)
    pair<iterator, bool> insert(const value_type& x);
    pair<iterator, bool> insert(value_type&& x);
    template <class... Args>
    pair<iterator, bool> emplace(Args&&... args);

    // Доступ до внутрішніх контейнерів
    const key_container_type& keys() const noexcept;
    const mapped_container_type& values() const noexcept;
};

} // namespace std
```

### Гарантії інвалідації ітераторів та асимптотика

- **Пошук:** Бінарний пошук `find`, `lower_bound`, `contains` виконується за час `O(log N)` порівнянь. Завдяки неперервному зберіганню ключів у `vector<Key>` час пошуку значно менший за `std::map` через відсутність промахів кешу пам'яті (L1/L2 Cache Hits).
- **Вставка:** Операції `insert`, `emplace` вимагають зміщення елементів масиву праворуч від знайденої позиції і виконуються за час `O(N)`.
- **Інвалідація:** Будь-яка операція вставки чи видалення елементів інвалідує всі ітератори та посилання на елементи `flat_map`, оскільки внутрішні вектори можуть виконувати реалокацію пам'яті або зсув масиву.

## Інтерфейс виводу std::print та std::println

Функції форматованого виводу в заголовку `<print>` замінюють оператори потокового виводу `std::cout << ...` та функцію `printf`. Вони виконують типобезпечну перевірку рядка формату під час компіляції та передають сформований UTF-8 буфер безпосередньо в дескриптор системного виводу:

```cpp
namespace std {

// Вивід у стандартний потік stdout
template <class... Args>
void print(format_string<Args...> fmt, Args&&... args);

template <class... Args>
void println(format_string<Args...> fmt, Args&&... args);

void println(); // Виводить один символ нового рядка '\n'

// Вивід у довільний потік C-бібліотеки FILE*
template <class... Args>
void print(FILE* stream, format_string<Args...> fmt, Args&&... args);

template <class... Args>
void println(FILE* stream, format_string<Args...> fmt, Args&&... args);

void println(FILE* stream);

// Низькорівневі системні точки входу без шаблонів
void vprint_unicode(string_view fmt, format_args args);
void vprint_unicode(FILE* stream, string_view fmt, format_args args);

void vprint_nonunicode(string_view fmt, format_args args);
void vprint_nonunicode(FILE* stream, string_view fmt, format_args args);

} // namespace std
```

### Механіка роботи із системними терміналами

- **POSIX-системи:** Функція `std::print` формує буфер форматованого тексту і записує його за один системний виклик `write(fileno(stream), buffer, size)`. Це усуває стан гонитви при багатопотоковому виводі без блокування глобальних м'ютексів.
- **Windows-системи:** Якщо стандартний вивід спрямовано у віртуальний термінал консолі, функція викликає `WriteConsoleW`, автоматично перетворюючи UTF-8 байти у формат UTF-16, що повністю розв'язує проблему спотворення кириличних та спеціальних символів без ручного налаштування системної кодової сторінки `SetConsoleOutputCP(CP_UTF8)`. Якщо вивід перенаправлено у файл або конвеєр (`pipe`), виклик виконується як прямий запис байтів без перекодування.

## Інтерфейс корутинного генератора std::generator

Клас `std::generator<Ref, V, Allocator>` є стандартною обгорткою для синхронних корутин. Він повністю позбавляє розробника необхідності власноруч конструювати структури `promise_type`, керувати кадрами корутини (англ. *coroutine frame*) та відстежувати часи життя тимчасових об'єктів:

```cpp
namespace std {

template <class Ref, class V = void, class Allocator = void>
class generator : public ranges::view_interface<generator<Ref, V, Allocator>> {
public:
    using yielded = conditional_t<is_reference_v<Ref>, Ref, const Ref&>;
    using value_type = conditional_t<is_void_v<V>, remove_cvref_t<Ref>, V>;
    using reference = conditional_t<is_reference_v<Ref>, Ref, value_type>;

    class promise_type {
    public:
        generator get_return_object() noexcept;
        suspend_always initial_suspend() noexcept;
        suspend_always final_suspend() noexcept;

        suspend_always yield_value(yielded val) noexcept;
        auto yield_value(const remove_reference_t<yielded>& val)
            requires is_rvalue_reference_v<yielded>;

        template <class R, class Alloc>
            requires same_as<ranges::range_value_t<R>, value_type>
        auto yield_value(ranges::elements_of<R, Alloc> r) noexcept;

        void return_void() noexcept;
        void unhandled_exception();
    };

    generator(const generator&) = delete;
    generator(generator&& other) noexcept;
    generator& operator=(generator&& other) noexcept;
    ~generator();

    struct iterator {
        using value_type = generator::value_type;
        using difference_type = ptrdiff_t;
        using iterator_concept = input_iterator_tag;

        iterator& operator++();
        void operator++(int);
        reference operator*() const noexcept;
        bool operator==(default_sentinel_t) const noexcept;
    };

    iterator begin();
    default_sentinel_t end() noexcept;
};

} // namespace std
```

### Механізм симетричної передачі (Symmetric Transfer)

При делегуванні генерації підпослідовності через `co_yield std::ranges::elements_of(sub_gen)` стандартний `promise_type` виконує симетричну передачу управління між дескрипторами корутин `std::coroutine_handle`. Це усуває небезпеку переповнення стека (Stack Overflow) при глибоких рекурсивних викликах обходу дерев та графічних графів, оскільки кадри корутин активуються без збільшення апаратного стека процесора.

## Інтерфейс діагностики стека <stacktrace>

Заголовок `<stacktrace>` надає стандартний механізм для програмного отримання поточного ланцюжка викликів функцій без зупинки процесу зовнішнім налагоджувачем:

```cpp
namespace std {

class stacktrace_entry {
public:
    using native_handle_type = /* implementation-defined */;

    constexpr stacktrace_entry() noexcept;
    constexpr native_handle_type native_handle() const noexcept;
    constexpr explicit operator bool() const noexcept;

    string description() const; // Назва функції (з деманглінгом)
    string source_file() const; // Шлях до файлу сирцевого коду
    uint_least32_t source_line() const; // Номер рядка виклику

    friend constexpr bool operator==(const stacktrace_entry&, const stacktrace_entry&) noexcept;
    friend constexpr strong_ordering operator<=>(const stacktrace_entry&, const stacktrace_entry&) noexcept;
};

template <class Allocator = allocator<stacktrace_entry>>
class basic_stacktrace {
public:
    using value_type = stacktrace_entry;
    using const_reference = const value_type&;
    using size_type = size_t;
    using const_iterator = /* implementation-defined */;

    // Фабричні методи захоплення стека
    static basic_stacktrace current(const Allocator& alloc = Allocator()) noexcept;
    static basic_stacktrace current(size_type skip, const Allocator& alloc = Allocator()) noexcept;
    static basic_stacktrace current(size_type skip, size_type max_depth, const Allocator& alloc = Allocator()) noexcept;

    basic_stacktrace() noexcept;
    size_type size() const noexcept;
    bool empty() const noexcept;

    const_reference operator[](size_type frame_no) const;
    const_reference at(size_type frame_no) const;

    const_iterator begin() const noexcept;
    const_iterator end() const noexcept;
};

using stacktrace = basic_stacktrace<allocator<stacktrace_entry>>;

string to_string(const stacktrace& st);
string to_string(const stacktrace_entry& ste);

} // namespace std
```

## Допоміжні системні утиліти C++23

### std::move_only_function

Клас `std::move_only_function` усуває критичний недолік `std::function`: він не вимагає від збереженого замикання (лямбди) бути копійованим. Це дозволяє зберігати у функціональних обгортках об'єкти з семантикою виключного володіння (`std::unique_ptr`, дескриптори сокетів `std::jthread`, `std::promise`):

```cpp
namespace std {

template <class... Signatures>
class move_only_function;

template <class R, class... Args>
class move_only_function<R(Args...)> {
public:
    using result_type = R;

    constexpr move_only_function() noexcept;
    constexpr move_only_function(nullptr_t) noexcept;
    move_only_function(move_only_function&&) noexcept;
    template <class F>
    move_only_function(F&& f);

    move_only_function(const move_only_function&) = delete;
    move_only_function& operator=(const move_only_function&) = delete;
    move_only_function& operator=(move_only_function&&) noexcept;

    explicit operator bool() const noexcept;
    R operator()(Args... args) const;
};

} // namespace std
```

### Числові типи з фіксованою шириною <stdfloat>

Заголовок `<stdfloat>` визначає типи чисел із плаваючою крапкою, бінарний формат яких гарантовано відповідає стандарту IEEE 754:

- **`std::float16_t`** — 16-бітне число половинної точності (1 біт знака, 5 біт порядку, 10 біт мантиси).
- **`std::float32_t`** — 32-бітне число одинарної точності (1 біт знака, 8 біт порядку, 23 біти мантиси).
- **`std::float64_t`** — 64-бітне число подвійної точності (1 біт знака, 11 біт порядку, 52 біти мантиси).
- **`std::float128_t`** — 128-бітне число четвертинної точності (1 біт знака, 15 біт порядку, 112 біт мантиси).
- **`std::bfloat16_t`** — 16-бітний формат для нейромережевих обчислень Brain Floating Point (1 біт знака, 8 біт порядку, 7 біт мантиси, має такий самий динамічний діапазон, як `float32_t`).

### Неалокуючі рядкові потоки <spanstream>

Класи `<spanstream>` здійснюють потокове форматування у фіксований буфер пам'яті:

```cpp
namespace std {

template <class CharT, class Traits = char_traits<CharT>>
class basic_spanstream : public basic_iostream<CharT, Traits> {
public:
    using char_type = CharT;
    using traits_type = Traits;
    using int_type = typename traits_type::int_type;
    using pos_type = typename traits_type::pos_type;
    using off_type = typename traits_type::off_type;

    explicit basic_spanstream(span<CharT> s, ios_base::openmode which = ios_base::in | ios_base::out);
    span<CharT> span() const noexcept;
    void span(span<CharT> s) noexcept;
};

using spanstream = basic_spanstream<char>;
using ispanstream = basic_ispanstream<char>;
using ospanstream = basic_ospanstream<char>;

} // namespace std
```

### std::forward_like

Утиліта передачі кваліфікаторів типу об'єкта-власника на його внутрішнє поле:

```cpp
namespace std {

template <class Owner, class Member>
constexpr auto&& forward_like(Member&& member) noexcept {
    using UnrefOwner = remove_reference_t<Owner>;
    using UnrefMember = remove_reference_t<Member>;

    if constexpr (is_const_v<UnrefOwner>) {
        if constexpr (is_rvalue_reference_v<Owner>) {
            return static_cast<const UnrefMember&&>(member);
        } else {
            return static_cast<const UnrefMember&>(member);
        }
    } else {
        if constexpr (is_rvalue_reference_v<Owner>) {
            return static_cast<UnrefMember&&>(member);
        } else {
            return static_cast<UnrefMember&>(member);
        }
    }
}

} // namespace std
```

### std::to_underlying

Безпечне приведення строго типізованого переліку `enum class` до його базового цілочисельного типу:

```cpp
namespace std {

template <class Enum>
constexpr underlying_type_t<Enum> to_underlying(Enum e) noexcept {
    return static_cast<underlying_type_t<Enum>>(e);
}

} // namespace std
```

### std::unreachable

Повідомлення оптимізатору компілятора про те, що точка входу в програмі ніколи не буде досягнута під час коректного виконання:

```cpp
namespace std {

[[noreturn]] inline void unreachable() {
#if defined(__GNUC__) || defined(__clang__)
    __builtin_unreachable();
#elif defined(_MSC_VER)
    __assume(false);
#endif
}

} // namespace std
```
