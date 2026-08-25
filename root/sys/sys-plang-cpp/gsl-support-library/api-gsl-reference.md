# 📋 Повний довідник інтерфейсів та типів Guidelines Support Library

Бібліотека Guidelines Support Library (GSL) надає стандартизований набір фундаментальних типів, концептів, функціональних обгорток та макросів, розроблених для прямої підтримки правил C++ Core Guidelines. Головна мета бібліотеки — перенести перевірку безпеки оперативної пам'яті, життєвого циклу об'єктів та меж масивів на етап компіляції або детермінованого динамічного контролю без створення додаткових накладних витрат у згенерованому машинному коді.

Цей довідник містить вичерпний опис сигнатур, методів, контрактних інваріантів, виняткових ситуацій, системних вирівнювань та правил взаємодії з компіляторами для всіх компонентів бібліотеки GSL.

---

## 1. Вказівники та інваріанти ненульовості (Pointers & Nullability)

Заголовний модуль: `<gsl/pointers>` (або єдиний включаючий заголовок `<gsl/gsl>`).

Компоненти цієї групи вирішують класичну проблему семантичної неоднозначності сирих вказівників, гарантуючи неможливість збереження або передачі нульової адреси (`nullptr`) безпосередньо на рівні системи типів.

### gsl::not_null<T>
Шаблонна обгортка для вказівникоподібних типів (сирих покажчиків `U*`, розумних вказівників `std::unique_ptr<U>`, `std::shared_ptr<U>`), яка встановлює та підтримує строгий інваріант: внутрішній покажчик гарантовано не дорівнює `nullptr` протягом усього часу існування об'єкта.

```cpp
namespace gsl {
    template <class T>
    class not_null {
    public:
        static_assert(detail::is_pointer_like<T>::value, "T must be a pointer-like type");

        using element_type = typename std::pointer_traits<T>::element_type;

        // Конструктори від валідного покажчика
        constexpr not_null(T u);
        template <class U, class = std::enable_if_t<std::is_convertible<U, T>::value>>
        constexpr not_null(const not_null<U>& other);

        // Заборонені конструктори та оператори присвоєння від nullptr
        constexpr not_null(std::nullptr_t) = delete;
        constexpr not_null& operator=(std::nullptr_t) = delete;

        // Доступ до даних та розіменування
        constexpr element_type& operator*() const noexcept(noexcept(*std::declval<T>()));
        constexpr T operator->() const noexcept;
        constexpr T get() const noexcept;

        // Неявне приведення до базового типу вказівника
        constexpr operator T() const noexcept;

        // Заборона адресної арифметики для запобігання виходу за межі пам'яті (Rule Bounds.1)
        not_null& operator++() = delete;
        not_null& operator--() = delete;
        not_null operator++(int) = delete;
        not_null operator--(int) = delete;
        not_null& operator+=(std::ptrdiff_t) = delete;
        not_null& operator-=(std::ptrdiff_t) = delete;
        void operator[](std::ptrdiff_t) const = delete;
    };

    // Фабрична функція дедукції типу
    template <class T>
    constexpr not_null<T> make_not_null(T&& t);
}
```

#### Детальний аналіз семантики, ABI та оптимізацій:
- **Статичний контроль при конструюванні**: Будь-яка спроба ініціалізувати об'єкт через літерал `nullptr`, макрос `NULL` або цілочисельний нуль `0` призводить до помилки компіляції, оскільки відповідні перевантаження конструкторів позначені специфікатором `= delete`.
- **Динамічний контроль (Runtime Assertion)**: При конструюванні з динамічної змінної сирого покажчика (`T u`) конструктор виконує контрактну перевірку `Expects(u != nullptr)`. Якщо змінна містить нуль, негайно спрацьовує налаштований обробник порушення контрактів (за замовчуванням `std::terminate`).
- **Нульові накладні витрати (Zero-Overhead ABI)**: Клас містить єдине поле типу `T`. Його розмір у пам'яті суворо дорівнює `sizeof(T)` (8 байтів на 64-бітних архітектурах). При виклику функцій параметри `gsl::not_null<T*>` передаються безпосередньо через апаратні регістри загального призначення (наприклад, `RDI`, `RSI`, `RDX` за стандартом System V AMD64 ABI або `RCX`, `RDX` в ABI Microsoft x64). У згенерованому асемблерному коді розіменування `*p` компілюється в пряму інструкцію доступу до пам'яті `mov rax, [rdi]` без додаткових розгалужень та перевірок прапорців.
- **Заборона адресної арифметики**: Перевантаження операторів інкременту (`++`), декременту (`--`), зсуву покажчика (`+=`, `-=`) та індексації (`[]`) повністю видалені. Якщо покажчик вказує на послідовність елементів масиву, правило Core Guidelines Bounds.1 вимагає використання `gsl::span<T>`, а не адресної арифметики над одиночним вказівником.

---

### gsl::strict_not_null<T>
Посилена версія `gsl::not_null<T>`, у якій оператор неявного приведення до базового типу `operator T()` оголошено як `explicit` або повністю видалено з інтерфейсу класу.

Цей тип застосовується в архітектурних шарах із підвищеними вимогами до безпеки, де випадкове неявне перетворення `not_null` назад у сирий неперевірений покажчик розглядається як потенційна загроза втрати контролю над інваріантом. Для отримання внутрішнього покажчика вимагається явний виклик методу `.get()`.

---

### gsl::owner<T>
Спеціалізований аліас типу, призначений для маркування сирих вказівників або системних дескрипторів, які несуть семантичну відповідальність за володіння ресурсом і зобов'язують викликача вивільнити пам'ять за допомогою оператора `delete` або відповідної системної функції.

```cpp
namespace gsl {
    template <class T, class = std::enable_if_t<std::is_pointer<T>::value>>
    using owner = T;
}
```

#### Роль у системі статичного аналізу та правила відстеження:
- З точки зору компілятора мови C++, `gsl::owner<T*>` є звичайним прозорим псевдонімом (`typedef`) для сирого типу `T*`. Він не додає жодних полів, методів чи перевірок у runtime і не впливає на розмір структури чи швидкість виконання.
- З точки зору інструментів статичного аналізу (MSVC C++ Core Checkers, Clang-Tidy), `gsl::owner<T*>` активує модуль відстеження життєвого циклу власності (Ownership Profile):
  - Якщо функція повертає результат оператора `new` або виклику аллокатора, її значення повинно бути позначено як `owner<T*>` (попередження C26400).
  - Змінна типу `owner<T*>` повинна бути або передана іншому власнику, або явно знищена через `delete` до виходу з поточної області видимості (попередження C26401 — запобігання витоку пам'яті).
  - Присвоєння невласницького покажчика змінній `owner<T*>` або спроба переприсвоєння без попереднього вивільнення розглядається як грубе порушення інваріантів (попередження C26409).
  - Цей тип слугує тимчасовим містком під час поетапного рефакторингу застарілого C-подібного коду до сучасних розумних вказівників `std::unique_ptr` та `std::shared_ptr`.

---

## 2. Безпечні неперервні діапазони: gsl::span

Заголовний модуль: `<gsl/span>`

Шаблон `gsl::span<T, Extent>` є невласницьким переглядом (view) суцільної послідовності об'єктів у пам'яті. Він інкапсулює вказівник на перший елемент і кількість елементів, повністю усуваючи вразливості, пов'язані з передачею окремо покажчика та окремо цілочисельного розміру.

```cpp
namespace gsl {
    inline constexpr std::ptrdiff_t dynamic_extent = -1;

    template <class ElementType, std::ptrdiff_t Extent = dynamic_extent>
    class span {
    public:
        using element_type     = ElementType;
        using value_type       = std::remove_cv_t<ElementType>;
        using size_type        = std::ptrdiff_t; // Знаковий тип індексу
        using pointer          = element_type*;
        using const_pointer    = const element_type*;
        using reference        = element_type&;
        using const_reference  = const element_type&;
        using iterator         = /* implementation-defined continuous iterator */;
        using reverse_iterator = std::reverse_iterator<iterator>;

        static constexpr std::ptrdiff_t extent = Extent;

        // Конструктори за замовчуванням та від покажчика з розміром
        constexpr span() noexcept;
        constexpr span(pointer ptr, size_type count);
        constexpr span(pointer firstElem, pointer lastElem);

        // Конструктори від фіксованих масивів мови C
        template <std::size_t N>
        constexpr span(element_type (&arr)[N]) noexcept;

        // Конструктори від стандартних контейнерів (std::vector, std::array)
        template <class Container>
        constexpr span(Container& cont);
        template <class Container>
        constexpr span(const Container& cont);

        // Ітератори суцільного доступу
        constexpr iterator begin() const noexcept;
        constexpr iterator end() const noexcept;
        constexpr reverse_iterator rbegin() const noexcept;
        constexpr reverse_iterator rend() const noexcept;

        // Елементний доступ із обов'язковим контролем меж
        constexpr reference operator[](size_type idx) const;
        constexpr reference front() const;
        constexpr reference back() const;
        constexpr pointer data() const noexcept;

        // Інформація про розмір
        constexpr size_type size() const noexcept;
        constexpr size_type size_bytes() const noexcept;
        [[nodiscard]] constexpr bool empty() const noexcept;

        // Генерація піддіапазонів (Subspans)
        template <std::ptrdiff_t Count>
        constexpr span<element_type, Count> first() const;
        constexpr span<element_type, dynamic_extent> first(size_type count) const;

        template <std::ptrdiff_t Count>
        constexpr span<element_type, Count> last() const;
        constexpr span<element_type, dynamic_extent> last(size_type count) const;

        template <std::ptrdiff_t Offset, std::ptrdiff_t Count = dynamic_extent>
        constexpr auto subspan() const;
        constexpr span<element_type, dynamic_extent> subspan(size_type offset, size_type count = dynamic_extent) const;
    };

    // Допоміжні функції для роботи з сирими байтами
    template <class ElementType, std::ptrdiff_t Extent>
    span<const byte, Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_bytes(span<ElementType, Extent> s) noexcept;

    template <class ElementType, std::ptrdiff_t Extent>
    span<byte, Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_writeable_bytes(span<ElementType, Extent> s) noexcept;
}
```

#### Ключові відмінності gsl::span від стандарту C++20 std::span:
1. **Знаковий тип розміру (`std::ptrdiff_t`)**: У GSL розмір та індекс мають знаковий тип `std::ptrdiff_t`. Це запобігає класичним помилкам переповнення беззнакових чисел при декременті у циклах `for (auto i = s.size() - 1; i >= 0; --i)`, де беззнаковий `size_t` спричиняє небезпечне переповнення до `SIZE_MAX`.
2. **Обов'язкова перевірка меж в операторі `[]`**: На відміну від `std::span::operator[]`, який у стандарті C++20 не вимагає обов'язкового контролю меж (залишаючи це на розсуд розробника через макроси компілятора), `gsl::span::operator[]` завжди перевіряє умову `0 <= idx && idx < size()`. У разі виходу за межі діапазону викликається макрос `Expects()`, що запобігає експлуатації критичних уразливостей виходу за межі буфера.
3. **Статичний та динамічний розмір**: Якщо розмір масиву відомий на етапі компіляції (наприклад, `int arr[16]`), `gsl::span<int, 16>` зберігає лише один покажчик (8 байтів), оптимізуючи розмір структури до нуля додаткових витрат. При `dynamic_extent` об'єкт зберігає покажчик і розмір (16 байтів на 64-бітних системах).
4. **Байтові проекції (as_bytes та as_writeable_bytes)**: Функція `gsl::as_bytes(s)` створює `gsl::span<const gsl::byte>`, що дозволяє переглядати будь-яку тривіально копійовану структуру даних як послідовність незмінних байтів без порушення правил строгого аліасингу (strict aliasing). Модифікація пам'яті через `gsl::as_writeable_bytes(s)` доступна лише для неконстантних вихідних діапазонів.

---

## 3. Сира пам'ять та безпечні рядки C-стилю

Заголовні модулі: `<gsl/byte>`, `<gsl/string_span>`

### gsl::byte
Типобезпечна обгортка для представлення сирих байтів неструктурованої пам'яті.

```cpp
namespace gsl {
    enum class byte : unsigned char {};

    constexpr byte operator&(byte l, byte r) noexcept;
    constexpr byte operator|(byte l, byte r) noexcept;
    constexpr byte operator^(byte l, byte r) noexcept;
    constexpr byte operator~(byte b) noexcept;

    template <class IntegerType>
    constexpr byte operator<<(byte b, IntegerType shift) noexcept;
    template <class IntegerType>
    constexpr byte operator>>(byte b, IntegerType shift) noexcept;

    template <class IntegerType>
    constexpr IntegerType to_integer(byte b) noexcept;
}
```

#### Призначення та правила використання:
- На відміну від типу `char` або `unsigned char`, `gsl::byte` не є символом і не є цілочисельним арифметичним значенням.
- Над типом `gsl::byte` суворо заборонені математичні операції додавання (`+`), віднімання (`-`), множення (`*`) та ділення (`/`).
- Дозволено виключно порозрядні логічні маски (`&`, `|`, `^`, `~`) та бітові зсуви (`<<`, `>>`), що гарантує надійний захист від випадкових арифметичних спотворень бінарних буферів під час мережевої або апаратної взаємодії.

### Псевдоніми рядків Z-String
У застарілих інтерфейсах C сирий покажчик `char*` міг означати як нуль-термінований рядок, так і вказівник на одиночний символ або масив фіксованого розміру. Бібліотека GSL запроваджує набір явних псевдонімів для однозначної ідентифікації C-рядків:

```cpp
namespace gsl {
    using zstring   = char*;
    using czstring  = const char*;
    using wzstring  = wchar_t*;
    using cwzstring = const wchar_t*;
    using u8zstring = char8_t*;
    using cu8zstring= const char8_t*;
}
```

Використання `gsl::czstring` однозначно декларує в сигнатурі функції очікування коректного C-рядка з кінцевим нуль-символом `\0`. Це дозволяє статичним аналізаторам перевіряти наявність термінатора у рядкових літералах перед передачею в системні виклики POSIX або Windows API, виявляючи потенційні читання за межами пам'яті.

---

## 4. Безпечні звужуючі перетворення: gsl::narrow та gsl::narrow_cast

Заголовний модуль: `<gsl/narrow>`

Мова C++ дозволяє неявне або явне за допомогою `static_cast` звуження типів даних (наприклад, з `int64_t` у `int32_t`, з `int` у `uint8_t`, або з `double` у `int`). Це спричиняє непомітне обтинання старших розрядів та спотворення знаку, що є джерелом критичних вразливостей переповнення буфера.

```cpp
namespace gsl {
    struct narrowing_error : public std::exception {
        const char* what() const noexcept override {
            return "gsl::narrowing_error: target type cannot hold source value";
        }
    };

    template <class Target, class Source>
    constexpr Target narrow(Source u);

    template <class Target, class Source>
    constexpr Target narrow_cast(Source&& u) noexcept;
}
```

### Порівняльний аналіз функцій перетворення:

1. **`gsl::narrow<Target>(val)`**:
   - Здійснює приведення значення `val` до цільового типу `Target`.
   - Виконує зворотне приведення отриманого результату до початкового типу `Source` і порівнює з оригіналом: `static_cast<Source>(target_val) == val`.
   - Перевіряє збереження знаку величини (щоб уникнути ситуацій, коли від'ємне число перетворюється на велике додатне беззнакове значення або навпаки).
   - Якщо значення спотворено або обрізано, негайно викидає виняток `gsl::narrowing_error`.
   - Застосовується під час десеріалізації зовнішніх даних, розборі мережевих протоколів та взаємодії з неперевіреним введенням від користувача.

2. **`gsl::narrow_cast<Target>(val)`**:
   - Є прямим семантичним еквівалентом `static_cast<Target>(val)` без жодних додаткових перевірок у runtime.
   - Використовується виключно для явного документування наміру програміста та придушення попереджень статичного аналізатора (Core Guideline ES.46), коли коректність діапазону гарантується попередніми логічними перевірками або математичними інваріантами.

---

## 5. Захист областей видимості: gsl::finally та gsl::final_action

Заголовний модуль: `<gsl/util>`

Реалізує ідіому Scope Guard (охоронець області видимості), забезпечуючи виконання завершального блоку коду при виході з поточної функції або блоку за будь-яких умов: нормального завершення, дострокового `return`, `break`, `goto` або аварійного розгортання стеку через виняток `throw`.

```cpp
namespace gsl {
    template <class F>
    class final_action {
    public:
        static_assert(!std::is_reference<F>::value && !std::is_const<F>::value,
                      "F should be a non-const, non-reference callable object");

        explicit final_action(F f) noexcept : clean_action_(std::move(f)), active_(true) {}
        ~final_action() noexcept {
            if (active_) clean_action_();
        }

        // Переміщення дозволено, копіювання суворо заборонено
        final_action(final_action&& other) noexcept;
        final_action(const final_action&) = delete;
        final_action& operator=(const final_action&) = delete;
        final_action& operator=(final_action&&) = delete;

        // Деактивація дії (наприклад, при успішному завершенні транзакції)
        void dismiss() noexcept { active_ = false; }

    private:
        F clean_action_;
        bool active_;
    };

    template <class F>
    [[nodiscard]] final_action<std::decay_t<F>> finally(F&& f) noexcept;
}
```

#### Механізм функціонування, винятки та оптимізація:
- Функція `gsl::finally` повертає об'єкт `final_action`, позначений атрибутом `[[nodiscard]]`. Якщо розробник забуде зберегти результат у змінну (наприклад, напише `gsl::finally([...]);`), компілятор згенерує попередження, оскільки безіменний тимчасовий об'єкт буде знищено на тому ж рядку коду.
- Деструктор `~final_action()` позначено специфікатором `noexcept`. Будь-який виняток всередині дії очищення перехоплюється або призводить до виклику `std::terminate`, щоб гарантувати стабільність розгортання стеку (Stack Unwinding).
- Метод `.dismiss()` дозволяє скасувати виконання зареєстрованого лямбда-виразу. Це корисно при реалізації ідіоми транзакційності: якщо операція пройшла успішно, відкат скасовується.

---

## 6. Декларативні контракти: Expects та Ensures

Заголовний модуль: `<gsl/assert>`

Макроси `Expects` та `Ensures` надають компактну та виразну форму для запису преумов (preconditions) та постумов (postconditions) функцій безпосередньо у коді.

```cpp
// Перевірка вхідних умов функції (Preconditions)
Expects(pointer != nullptr);
Expects(size > 0);

// Перевірка гарантій результату функції (Postconditions)
Ensures(result >= 0);
```

### Конфігурація глобальної поведінки при збої контрактів:

Поведінка макросів під час порушення умови налаштовується прапорцями препроцесора під час збірки проєкту:

1. **`GSL_TERMINATE_ON_CONTRACT_VIOLATION` (режим за замовчуванням)**:
   - При порушенні умови макрос друкує повідомлення про помилку у стандартний потік діагностики та викликає `std::terminate()`.
   - Рекомендований для production-серверів та систем реального часу, де продовження роботи зі зламаним інваріантом загрожує пошкодженням пам'яті.

2. **`GSL_THROW_ON_CONTRACT_VIOLATION`**:
   - При виявленні хибної умови генерує спеціальний виняток `gsl::fail_fast`.
   - Застосовується в модульних тестах для верифікації того, що функції коректно відхиляють невалідні вхідні аргументи.

3. **`GSL_UNENFORCED_ON_CONTRACT_VIOLATION`**:
   - Повністю вимикає генерацію коду перевірки (перетворюється на порожню інструкцію).
   - Застосовується виключно в ультракритичних циклах чисельного моделювання, де навіть одна перевірка умови сповільнює роботу процесора.

---

## 7. Відповідність компонентів GSL діагностичним правилам статичного аналізу

Використання типів GSL дозволяє автоматично придушувати або задовольняти діагностичні правила модулів статичного аналізу MSVC C++ Core Check та LLVM Clang-Tidy:

- **Правило I.12 / F.60 (Не передавати неперевірені вказівники)**:
  - MSVC попередження: `C26429` (Покажчик ніколи не перевіряється на null, оголосіть як `not_null`), `C26430` (Символ не перевірений на null перед розіменуванням).
  - Рішення GSL: використання `gsl::not_null<T*>`.

- **Правило I.11 / C.31 / R.3 (Явне володіння ресурсами)**:
  - MSVC попередження: `C26400` (Ініціалізація невласницького покажчика результатом виділення пам'яті), `C26401` (Видалення невласницького покажчика через `delete`), `C26409` (Уникайте явних викликів `new`/`delete`).
  - Clang-Tidy правило: `cppcoreguidelines-owning-memory`.
  - Рішення GSL: використання `gsl::owner<T*>`.

- **Правило Bounds.1 / I.13 (Заборона сирої арифметики вказівників)**:
  - MSVC попередження: `C26481` (Не використовуйте арифметику вказівників, застосовуйте `span`), `C26485` (Масив неявно розпадається у покажчик).
  - Clang-Tidy правило: `cppcoreguidelines-pro-bounds-pointer-arithmetic`.
  - Рішення GSL: заміна пар `(T*, size)` на `gsl::span<T>`.

- **Правило ES.46 (Уникати неявних звужуючих перетворень)**:
  - MSVC попередження: `C26472` (Не використовуйте `static_cast` для звуження числових типів).
  - Clang-Tidy правило: `cppcoreguidelines-narrowing-conversions`.
  - Рішення GSL: застосування `gsl::narrow` або явного `gsl::narrow_cast`.

---

## 8. Керування попередженнями лінтерів: макроси придушення

У складних legacy-інтерфейсах або при роботі з низькорівневими драйверами ядра розробнику іноді необхідно локально відключити попередження аналізатора. Бібліотека GSL підтримує стандартизований синтаксис придушення діагностик:

```cpp
// Придушення для MSVC C++ Core Check
[[gsl::suppress(bounds.1)]]
void legacy_hardware_access(int* raw_io_port) {
    // Дозволено тимчасове використання адресної арифметики для регістрів MMIO
    *(raw_io_port + 0x10) = 0xFF;
}

// Придушення для Clang-Tidy
void parse_legacy_buffer(char* buf) // NOLINT(cppcoreguidelines-pro-bounds-pointer-arithmetic)
{
    buf[4] = '\0';
}
```

Такий підхід забезпечує абсолютну прозорість коду: кожне відхилення від правил C++ Core Guidelines документується безпосередньо в місці виникнення, що спрощує подальший аудит безпеки.

---

## 9. Взаємодія з динамічними санітайзерами (ASan, UBSan)

Окрім статичного аналізу на етапі компіляції, використання абстракцій GSL органічно доповнює динамічні інструменти виявлення дефектів пам'яті:
- **AddressSanitizer (ASan)**: Контрольні перевірки `gsl::span` перехоплюють помилки виходу за межі діапазону в runtime ще до того, як процесор виконає некоректний доступ до тіньової пам'яті (shadow memory), надаючи точні та структуровані повідомлення про помилку у стеку викликів.
- **UndefinedBehaviorSanitizer (UBSan)**: Застосування `gsl::narrow` повністю запобігає появі невизначеної поведінки при знаковому цілочисельному переповненні, перетворюючи потенційний UB на контрольований виняток мови C++.

---

## 10. Інтеграція GSL у системи автоматизованої збірки (CMake та менеджери пакетів)

Бібліотека Microsoft GSL доступна через усі сучасні менеджери пакетів та системи конфігурації збірки:

### Підключення через CMake (Target-based Integration):
При використанні CMake версії 3.14+ рекомендується підключати GSL як інтерфейсну ціль через `FetchContent` або системний пакет:

```cmake
# Варіант 1: Пошук встановленого пакета через vcpkg або системний менеджер
find_package(Microsoft.GSL CONFIG REQUIRED)
target_link_libraries(my_project PRIVATE Microsoft.GSL::GSL)

# Варіант 2: Автоматичне завантаження через FetchContent
include(FetchContent)
FetchContent_Declare(
    GSL
    GIT_REPOSITORY https://github.com/microsoft/GSL.git
    GIT_TAG        v4.0.0
)
FetchContent_MakeAvailable(GSL)
target_link_libraries(my_project PRIVATE Microsoft.GSL::GSL)
```

### Підключення через менеджери пакетів Conan та Vcpkg:
- **vcpkg**: `vcpkg install ms-gsl` (підтримує як повний репозиторій Microsoft GSL, так і портативний `gsl-lite`).
- **Conan**: `ms-gsl/4.0.0` у файлі `conanfile.txt` або `conanfile.py`.

Завдяки суто заголовній структурі (header-only) бібліотека не вимагає лінкування скомпільованих двійкових об'єктів `.so` або `.dll`, що забезпечує ідеальну портативність між різними архітектурами процесорів (x86, ARM, RISC-V) та операційними системами.
