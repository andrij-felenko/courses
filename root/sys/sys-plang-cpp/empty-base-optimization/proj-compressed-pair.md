# ⚙️ Реалізація compressed_pair: EBO проти [[no_unique_address]]

Контейнери та розумні покажчики стандартної бібліотеки C++ регулярно зберігають допоміжні службові сутності: алокатори динамічної пам'яті, функції вилучення (*deleters*), предикати впорядкування або геш-функції. Якщо такий службовий об'єкт не має власного внутрішнього стану, наївне збереження його як звичайного поля структури призводить до подвоєння обсягу пам'яті через правила апаратного вирівнювання. Шаблон `compressed_pair` розв'язує цю задачу: він ущільнює пару значень до мінімально можливого фізичного розміру, використовуючи техніку Empty Base Optimization (EBO) у стандартах C++11/C++17 або атрибут `[[no_unique_address]]` у C++20.

---

### Аналіз фізичної проблеми: чому наївне збереження марнує пам'ять

Щоб зрозуміти необхідність стиснення, простежимо поведінку наївного розумного покажчика. Розумний покажчик повинен зберігати дві речі: сиру адресу керованого динамічного ресурсу (`T*`) та екземпляр класу вилучення (`Deleter`), який відповідає за коректне повернення пам'яті в операційну систему або користувацький пул.

```cpp
#include <iostream>
#include <memory>
#include <cstddef>

template <typename T, typename Deleter = std::default_delete<T>>
class naive_unique_ptr {
    T* ptr_{nullptr};
    Deleter deleter_{};

public:
    explicit naive_unique_ptr(T* p = nullptr, Deleter d = Deleter{})
        : ptr_{p}, deleter_{d} {}

    ~naive_unique_ptr() {
        if (ptr_) {
            deleter_(ptr_);
        }
    }

    T* get() const noexcept { return ptr_; }
};
```

Погляньмо на те, як компілятор розташовує поля цього класу в оперативній пам'яті на сучасній 64-бітній архітектурі (x86-64 або AArch64). Сирий покажчик `ptr_` має розмір 8 байтів і вимагає вирівнювання за адресою, кратною 8 байтам. 

Клас `std::default_delete<T>` (або будь-який інший типовий безстанний делітер) не містить жодного поля даних. Відповідно до базового правила мови C++, розмір будь-якого повного об'єкта не може дорівнювати нулю (`sizeof(Deleter) >= 1`), тому компілятор виділяє для поля `deleter_` рівно 1 байт.

```cpp
struct CustomEmptyDeleter {
    void operator()(int* p) const noexcept {
        delete p;
    }
};

static_assert(sizeof(int*) == 8);
static_assert(sizeof(CustomEmptyDeleter) == 1);
static_assert(sizeof(naive_unique_ptr<int, CustomEmptyDeleter>) == 16);
```

Хоча корисний розмір становить 9 байтів (8 байтів покажчика плюс 1 байт фіктивного стану делітера), сумарний розмір структури `naive_unique_ptr` становить не 9, а 16 байтів.

Причина полягає у правилі доповнення структури (*tail padding*). Оскільки найбільшим полем структури є 8-байтовий покажчик, загальне вирівнювання всієї структури становить 8 байтів. Щоб при створенні послідовного масиву `naive_unique_ptr arr[10]` кожен наступний елемент масиву починався за адресою, кратною 8, компілятор зобов'язаний додати 7 байтів порожнього заповнення після поля `deleter_`.

У результаті витрати пам'яті зростають на 100%. Якщо програма оперує деревом, графом або вектором із мільйона дрібних вузлів, кожен з яких зберігає такий покажчик, накладні витрати на фіктивні байти сягають кількох мегабайтів. Крім того, подвоєний розмір об'єкта вдвічі знижує щільність упакування даних у кеш-лініях процесора (L1/L2 cache), спричиняючи частіші промахи кешу (*cache misses*) та суттєве падіння загальної швидкодії системи.

---

### Архітектура узагальненого рішення `compressed_pair`

Для подолання цієї неефективності розробляється абстракція `compressed_pair<T1, T2>`. Вона функціонально повторює інтерфейс стандартної пари `std::pair`, але гарантує компактну розкладку в пам'яті.

Інженерні вимоги до проектування `compressed_pair`:
1. **Мінімальний фізичний розмір**: якщо один із типів є порожнім класом без стану, загальний розмір пари має дорівнювати розміру іншого типу (`sizeof(compressed_pair<int*, Empty>) == sizeof(int*) == 8`).
2. **Універсальність типів**: пара повинна коректно працювати як з порожніми типами, так і зі звичайними типами зі станом (`int`, `double`, `std::string`), покажчиками, посиланнями та `final`-класами.
3. **Ідеальне передавання аргументів (*perfect forwarding*)**: конструктори пари мають приймати довільні типи аргументів і передавати їх у конструктори вкладених елементів без зайвих копіювань чи переміщень.
4. **Коректність категорій значень (*value category correctness*)**: методи доступу до елементів мають повертати lvalue-посилання або const lvalue-посилання відповідно до константності екземпляра пари.
5. **Підтримка умовної експліцитності (*conditional explicit*)**: конструктори не повинні дозволяти неявні небезпечні звужувальні перетворення, якщо відповідні конструктори елементів пари є явними (*explicit*).
6. **Підтримка шматочкового конструювання (*piecewise construction*)**: можливість ініціалізувати елементи пари кортежами аргументів через тег `std::piecewise_construct` без створення проміжних тимчасових об'єктів.
7. **Інтеграція зі структурованим зв'язуванням (*structured bindings*)**: спеціалізація `std::tuple_size` та `std::tuple_element` для підтримки розпакування синтаксисом `auto [a, b] = pair`.
8. **Використання `std::addressof`**: захист від можливого користувацького перевантаження унарного оператора взяття адреси `operator&`.

Розглянемо дві принципові реалізації: класичний варіант через спадкування (C++11/C++17) та сучасний варіант через атрибути мови (C++20).

---

### Реалізація 1: Класичний EBO через умовне спадкування (C++11 / C++17)

У стандартах до C++20 єдиним легальним способом змусити компілятор виділити під об'єкт 0 байтів у пам'яті було перетворення цього типу на базовий клас іншого типу. 

Проте ми не можемо просто оголосити `class compressed_pair : private T1, private T2`, оскільки:
- типи `T1` або `T2` можуть бути фундаментальними типами (`int`, `double`), покажчиками або класами з модифікатором `final`, від яких спадкуватися заборонено;
- типи `T1` та `T2` можуть виявитися однаковими (наприклад, `compressed_pair<Empty, Empty>`), що призведе до забороненого подвійного спадкування від одного базового типу;
- типи можуть мати реальний стан, для якого спадкування є надлишковим.

Щоб розв'язати ці проблеми, побудуємо дворівневу архітектуру з використанням метапрограмування на шаблонах:

```cpp
#include <type_traits>
#include <utility>
#include <tuple>
#include <memory>
#include <cstddef>

namespace legacy {

// Метафункція: перевіряє, чи можна застосувати EBO до конкретного типу
template <typename T>
constexpr bool can_apply_ebo_v = std::is_empty_v<T> && !std::is_final_v<T>;

// Базовий шаблон елемента пари з дискримінатором індексу
template <typename T, size_t Index, bool CanEbo = can_apply_ebo_v<T>>
class compressed_pair_element;

// Спеціалізація 1: Звичайне збереження в полі.
// Застосовується, якщо тип містить дані, є скаляром або позначений як final.
template <typename T, size_t Index>
class compressed_pair_element<T, Index, false> {
    T value_{};

public:
    compressed_pair_element() = default;

    template <typename U>
    explicit constexpr compressed_pair_element(U&& val)
        : value_(std::forward<U>(val)) {}

    template <typename... Args, size_t... Indices>
    constexpr compressed_pair_element(std::piecewise_construct_t,
                                      std::tuple<Args...> args,
                                      std::index_sequence<Indices...>)
        : value_(std::get<Indices>(std::move(args))...) {}

    constexpr T& get() noexcept { return value_; }
    constexpr const T& get() const noexcept { return value_; }
};

// Спеціалізація 2: Оптимізація порожньої бази через приватне спадкування.
// Застосовується виключно для порожніх класів, які дозволяють спадкування.
template <typename T, size_t Index>
class compressed_pair_element<T, Index, true> : private T {
public:
    compressed_pair_element() = default;

    template <typename U>
    explicit constexpr compressed_pair_element(U&& val)
        : T(std::forward<U>(val)) {}

    template <typename... Args, size_t... Indices>
    constexpr compressed_pair_element(std::piecewise_construct_t,
                                      std::tuple<Args...> args,
                                      std::index_sequence<Indices...>)
        : T(std::get<Indices>(std::move(args))...) {}

    constexpr T& get() noexcept { return *this; }
    constexpr const T& get() const noexcept { return *this; }
};

// Головний контейнерний клас стисненої пари
template <typename T1, typename T2>
class compressed_pair : private compressed_pair_element<T1, 0>,
                        private compressed_pair_element<T2, 1> {
    using FirstBase = compressed_pair_element<T1, 0>;
    using SecondBase = compressed_pair_element<T2, 1>;

public:
    compressed_pair() = default;

    template <typename U1, typename U2>
    constexpr compressed_pair(U1&& first_arg, U2&& second_arg)
        : FirstBase(std::forward<U1>(first_arg)),
          SecondBase(std::forward<U2>(second_arg)) {}

    template <typename... Args1, typename... Args2>
    constexpr compressed_pair(std::piecewise_construct_t pw,
                              std::tuple<Args1...> first_args,
                              std::tuple<Args2...> second_args)
        : FirstBase(pw, std::move(first_args), std::index_sequence_for<Args1...>{}),
          SecondBase(pw, std::move(second_args), std::index_sequence_for<Args2...>{}) {}

    constexpr T1& first() noexcept { return FirstBase::get(); }
    constexpr const T1& first() const noexcept { return FirstBase::get(); }

    constexpr T2& second() noexcept { return SecondBase::get(); }
    constexpr const T2& second() const noexcept { return SecondBase::get(); }
};

} // namespace legacy
```

Розберімо ключові інженерні деталі цієї реалізації:

1. **Роль параметра `Index`**: числовий параметр `Index` виступає унікальним тегом типу. Якщо користувач створить `compressed_pair<Empty, Empty>`, де обидва типи однакові, базовими класами стануть `compressed_pair_element<Empty, 0, true>` та `compressed_pair_element<Empty, 1, true>`. Оскільки для компілятора це два різні типи, множинне спадкування відбувається без колізій і неоднозначностей.
2. **Перевірка `!std::is_final_v<T>`**: якби ми перевіряли лише `std::is_empty_v<T>`, спроба створення пари з `final`-типом викликала б помилку під час спроби успадкування у спеціалізації `true`. Метафункція спрямовує `final`-класи у спеціалізацію зі звичайним полем, запобігаючи помилкам збирання ціною збереження додаткового байта.
3. **Метод `get()` у порожній спеціалізації**: приведення `*this` до посилання на базовий тип `T&` є абсолютно безкоштовною операцією компіляції. Компілятор просто розглядає адресу об'єкта як адресу типу `T`.
4. **Конструктор шматочкового конструювання**: розгортання кортежів через `std::index_sequence` дозволяє передавати параметри безпосередньо в конструктори внутрішніх типів. Це необхідно для типів, які не мають конструктора копіювання чи переміщення.

---

### Реалізація 2: Сучасний підхід із `[[no_unique_address]]` (C++20)

Стандарт C++20 принципово змінив спосіб проектування таких структур, додавши атрибут `[[no_unique_address]]`. Він повідомляє компілятору, що поле не потребує окремої фізичної адреси в пам'яті, якщо його тип є порожнім. Це дозволяє повернутися до класичної та інтуїтивно зрозумілої композиції без жодного спадкування.

Врахуємо двійкову специфіку середовища Microsoft Visual Studio (MSVC) через кросплатформний макрос:

```cpp
#if defined(_MSC_VER) && !defined(__clang__)
    #define COURSES_NO_UNIQUE_ADDRESS [[msvc::no_unique_address]]
#else
    #define COURSES_NO_UNIQUE_ADDRESS [[no_unique_address]]
#endif

namespace modern {

template <typename T1, typename T2>
class compressed_pair {
    COURSES_NO_UNIQUE_ADDRESS T1 first_{};
    COURSES_NO_UNIQUE_ADDRESS T2 second_{};

public:
    compressed_pair() = default;

    template <typename U1, typename U2>
    constexpr compressed_pair(U1&& arg1, U2&& arg2)
        : first_{std::forward<U1>(arg1)},
          second_{std::forward<U2>(arg2)} {}

    template <typename... Args1, typename... Args2>
    constexpr compressed_pair(std::piecewise_construct_t,
                              std::tuple<Args1...> first_args,
                              std::tuple<Args2...> second_args)
        : first_{std::make_from_tuple<T1>(std::move(first_args))},
          second_{std::make_from_tuple<T2>(std::move(second_args))} {}

    constexpr T1& first() noexcept { return first_; }
    constexpr const T1& first() const noexcept { return first_; }

    constexpr T2& second() noexcept { return second_; }
    constexpr const T2& second() const noexcept { return second_; }
};

// Інструкції автоматичного виведення типів аргументів шаблона (CTAD)
template <typename T1, typename T2>
compressed_pair(T1, T2) -> compressed_pair<T1, T2>;

} // namespace modern
```

Порівняння з кодом EBO демонструє кардинальну різницю:
- код скоротився на десятки рядків складної шаблонної інфраструктури;
- відсутні будь-які допоміжні базові класи та спеціалізації;
- класи з модифікатором `final` стискаються автоматично без вимкнення оптимізації;
- спрощується використання стандартної допоміжної функції `std::make_from_tuple`;
- додано правила виведення типів аргументів шаблона (CTAD — *Class Template Argument Deduction*);
- клас повністю задовольняє вимогам концепту стандартного макета (*standard-layout*), якщо типи елементів є типами стандартного макета.

---

### Підтримка структурованого зв'язування (*structured bindings*)

Щоб зробити `modern::compressed_pair` повноцінним громадянином екосистеми C++, додамо підтримку протоколу декомпозиції кортежів. Для цього необхідно спеціалізувати `std::tuple_size`, `std::tuple_element` та реалізувати вільну або член-функцію `get<I>()`:

```cpp
namespace modern {

template <size_t Index, typename T1, typename T2>
constexpr decltype(auto) get(compressed_pair<T1, T2>& p) noexcept {
    if constexpr (Index == 0) return p.first();
    else if constexpr (Index == 1) return p.second();
}

template <size_t Index, typename T1, typename T2>
constexpr decltype(auto) get(const compressed_pair<T1, T2>& p) noexcept {
    if constexpr (Index == 0) return p.first();
    else if constexpr (Index == 1) return p.second();
}

template <size_t Index, typename T1, typename T2>
constexpr decltype(auto) get(compressed_pair<T1, T2>&& p) noexcept {
    if constexpr (Index == 0) return std::move(p.first());
    else if constexpr (Index == 1) return std::move(p.second());
}

} // namespace modern

// Спеціалізації в просторі імен std
namespace std {

template <typename T1, typename T2>
struct tuple_size<modern::compressed_pair<T1, T2>>
    : std::integral_constant<size_t, 2> {};

template <typename T1, typename T2>
struct tuple_element<0, modern::compressed_pair<T1, T2>> {
    using type = T1;
};

template <typename T1, typename T2>
struct tuple_element<1, modern::compressed_pair<T1, T2>> {
    using type = T2;
};

} // namespace std
```

Тепер розробники можуть розпаковувати стиснені пари елегантно та ефективно:

```cpp
void demo_structured_binding() {
    modern::compressed_pair<int, double> point(10, 20.5);
    auto [x, y] = point;
    // x має тип int, y має тип double
}
```

---

### Практичне дослідження адрес у пам'яті: верифікація збігу адрес

Проведемо пряме експериментальне вимірювання числових адрес елементів у пам'яті за допомогою `std::addressof` та виведення через шістнадцятковий формат:

```cpp
#include <iostream>
#include <iomanip>

struct EmptyPolicyA {};
struct EmptyPolicyB {};

void inspect_memory_layout() {
    modern::compressed_pair<int*, EmptyPolicyA> compressed_ptr(nullptr, {});

    const void* base_addr = static_cast<const void*>(&compressed_ptr);
    const void* first_addr = static_cast<const void*>(std::addressof(compressed_ptr.first()));
    const void* second_addr = static_cast<const void*>(std::addressof(compressed_ptr.second()));

    std::cout << "Базова адреса пари:   " << base_addr << '\n';
    std::cout << "Адреса першого поля:  " << first_addr << '\n';
    std::cout << "Адреса другого поля:  " << second_addr << '\n';
}
```

Під час запуску на x86-64 Linux під компілятором GCC або Clang усі три адреси є абсолютно ідентичними:

```text
Базова адреса пари:   0x7ffeefbff560
Адреса першого поля:  0x7ffeefbff560
Адреса другого поля:  0x7ffeefbff560
```

Це наочно доводить, що порожній підоб'єкт `EmptyPolicyA` буквально ділить той самий початковий байт пам'яті з покажчиком `int*`. Компілятор не генерує жодних додаткових зсувів покажчика при виклику методів `EmptyPolicyA`.

---

### Як EBO реалізовано у промислових бібліотеках: кейс `std::vector`

Щоб побачити, як ця оптимізація формує ядро всієї стандартної бібліотеки, дослідимо внутрішню організацію динамічного масиву `std::vector<T, Allocator>` у двох провідних бібліотеках STL: GNU libstdc++ та LLVM libc++.

Стандартний вектор повинен зберігати три покажчики для керування буфером пам'яті:
- `T* begin_` — початок виділеного буфера;
- `T* end_` — кінець зайнятих елементів;
- `T* cap_` — кінець виділеної ємності пам'яті.

Крім того, вектор зобов'язаний зберігати екземпляр алокатора `Allocator`, переданого користувачем. За замовчуванням це `std::allocator<T>`, який не має жодного поля даних.

У бібліотеці **GNU libstdc++** реалізація вектора використовує проміжну базову структуру `_Vector_base`, внутрішній клас якої `_Vector_impl` приватно спадкує від алокатора:

```cpp
// Концептуальна схема організації вектора в GNU libstdc++
template <typename Tp, typename Alloc>
struct _Vector_base {
    struct _Vector_impl_data {
        Tp* _M_start{nullptr};
        Tp* _M_finish{nullptr};
        Tp* _M_end_of_storage{nullptr};
    };

    // Оптимізація: спадкування від алокатора Tp_alloc_type через EBO
    struct _Vector_impl : public Alloc, public _Vector_impl_data {
        _Vector_impl() = default;
        explicit _Vector_impl(const Alloc& a) : Alloc(a) {}
    };

    _Vector_impl _M_impl;
};
```

Завдяки EBO базовий клас `Alloc` ділить адресу з першим покажчиком `_M_start`. У результаті:
- `sizeof(std::vector<int, std::allocator<int>>) == 24` байти (рівно 3 машинних слова по 8 байтів);
- якби алокатор зберігався як звичайне поле, розмір становив би 32 байти (24 байти покажчиків + 1 байт алокатора + 7 байтів порожнього заповнення).

У бібліотеці **LLVM libc++** вектор зберігає дані у внутрішній парі `__compressed_pair`:

```cpp
// Концептуальна схема організації вектора в LLVM libc++
template <typename Tp, typename Alloc>
class vector {
    Tp* __begin_{nullptr};
    Tp* __end_{nullptr};
    std::__compressed_pair<Tp*, Alloc> __end_cap_;
};
```

Тут третій покажчик `__end_cap_` упакований разом з алокатором у `__compressed_pair`. На 64-бітній системі пара займає 8 байтів, а весь вектор — ті самі 24 байти.

---

### Поведінка зі stateful-алокаторами: зміна розкладки пам'яті

Що відбувається, коли алокатор перестає бути порожнім? Наприклад, у C++17 з'явилися поліморфні алокатори пам'яті `std::pmr::polymorphic_allocator<T>`, які містять покажчик на ресурс пам'яті `std::pmr::memory_resource*` (розмір 8 байтів).

Якщо ми створюємо вектор або розумний покажчик зі stateful-алокатором:
- тип перестає задовольняти умову `std::is_empty_v<T>`;
- метафункція `can_apply_ebo_v` обирає спеціалізацію зі звичайним полем даних, а атрибут `[[no_unique_address]]` виділяє під алокатор реальні 8 байтів;
- розмір `std::vector<int, std::pmr::polymorphic_allocator<int>>` автоматично зростає з 24 до 32 байтів.

Це ідеально ілюструє концепцію «плати лише за те, що використовуєш» (*pay-as-you-go*): для безстанних типів витрати дорівнюють нулю, а для типів зі станом пам'ять виділяється рівно в тому обсязі, який необхідний для збереження цього стану.

---

### Інтеграція в промисловий `optimal_unique_ptr`

Об'єднаймо наш `modern::compressed_pair` у повноцінний, безпечний до винятків розумний покажчик, який повністю відповідає семантиці володіння та ідіомі RAII:

```cpp
template <typename T, typename Deleter = std::default_delete<T>>
class optimal_unique_ptr {
    modern::compressed_pair<T*, Deleter> storage_;

public:
    constexpr optimal_unique_ptr() noexcept
        : storage_(nullptr, Deleter{}) {}

    constexpr explicit optimal_unique_ptr(T* ptr) noexcept
        : storage_(ptr, Deleter{}) {}

    constexpr optimal_unique_ptr(T* ptr, Deleter d) noexcept
        : storage_(ptr, std::move(d)) {}

    ~optimal_unique_ptr() {
        if (get()) {
            get_deleter()(get());
        }
    }

    // Заборона операцій копіювання для гарантії виключного володіння
    optimal_unique_ptr(const optimal_unique_ptr&) = delete;
    optimal_unique_ptr& operator=(const optimal_unique_ptr&) = delete;

    // Переміщувальний конструктор
    constexpr optimal_unique_ptr(optimal_unique_ptr&& other) noexcept
        : storage_(other.release(), std::move(other.get_deleter())) {}

    // Переміщувальний оператор присвоєння
    constexpr optimal_unique_ptr& operator=(optimal_unique_ptr&& other) noexcept {
        if (this != &other) {
            reset(other.release());
            get_deleter() = std::move(other.get_deleter());
        }
        return *this;
    }

    [[nodiscard]] constexpr T* get() const noexcept {
        return storage_.first();
    }

    [[nodiscard]] constexpr Deleter& get_deleter() noexcept {
        return storage_.second();
    }

    [[nodiscard]] constexpr const Deleter& get_deleter() const noexcept {
        return storage_.second();
    }

    constexpr T* release() noexcept {
        T* old_ptr = storage_.first();
        storage_.first() = nullptr;
        return old_ptr;
    }

    constexpr void reset(T* new_ptr = nullptr) noexcept {
        T* old_ptr = storage_.first();
        storage_.first() = new_ptr;
        if (old_ptr) {
            get_deleter()(old_ptr);
        }
    }

    [[nodiscard]] constexpr T& operator*() const noexcept {
        return *get();
    }

    [[nodiscard]] constexpr T* operator->() const noexcept {
        return get();
    }

    [[nodiscard]] constexpr explicit operator bool() const noexcept {
        return get() != nullptr;
    }
};
```

---

### Асемблерний аналіз та передача через регістри процесора

Стиснення розміру структури до одного машинного слова має колосальний вплив не лише на обсяг пам'яті, а й на двійковий інтерфейс виклику функцій (*ABI calling conventions*).

Згідно з угодою виклику System V AMD64 ABI (стандарт для Linux, macOS та BSD на архітектурі x86-64):
- структури розміром до 8 байтів розглядаються як один восьмибайтний блок і передаються або повертаються безпосередньо у загальних регістрах процесора (`rdi`, `rsi` для аргументів, `rax` для поверненого значення);
- структури розміром понад 16 байтів або структури з нетривіальними деструкторами передаються через непряму пам'ять у стеку (*stack memory*).

Розгляньмо генерацію коду фабричної функції:

```cpp
optimal_unique_ptr<int> create_resource() {
    return optimal_unique_ptr<int>(new int(42));
}
```

Для оптимізованого `optimal_unique_ptr` розмір структури дорівнює 8 байтам. Компілятор виділяє пам'ять через виклик оператора `operator new`, записує значення `42` за отриманою адресою і повертає сирий покажчик безпосередньо в регістрі `rax`:

```text
create_resource():
    sub     rsp, 8
    mov     edi, 4
    call    operator new(unsigned long)
    mov     dword ptr [rax], 42
    add     rsp, 8
    ret
```

Натомість для наївного `naive_unique_ptr` розміром 16 байтів функція змушена виконувати додаткові операції запису нульового фіктивного байта делітера у стек або оперувати двома регістрами (`rax` та `rdx`). У разі інтенсивного створення короткоживучих об'єктів (наприклад, у циклах обробки мережевих пакетів) оптимізація порожньої бази повністю усуває зайві операції з пам'яттю.

---

### Комплексне тестування та перевірка фізичних розмірів

Напишемо набір статичних перевірок під час компіляції (`static_assert`) для верифікації розмірів на 64-бітній платформі:

```cpp
// 1. Порожній безстанний делітер
struct StatelessDeleter {
    void operator()(int* ptr) const noexcept {
        delete ptr;
    }
};

// 2. Безстанний делітер, захищений від спадкування (final)
struct FinalStatelessDeleter final {
    void operator()(int* ptr) const noexcept {
        delete ptr;
    }
};

// 3. Делітер зі станом (наприклад, посилання на арену або лічильник)
struct StatefulDeleter {
    size_t* call_counter{nullptr};

    void operator()(int* ptr) const noexcept {
        if (call_counter) {
            ++(*call_counter);
        }
        delete ptr;
    }
};

// --- Тестування реалізації EBO (legacy) ---
// Звичайний порожній делітер стискається до 8 байтів:
static_assert(sizeof(legacy::compressed_pair<int*, StatelessDeleter>) == 8);
// Для final-делітера EBO вимикається -> розмір зростає до 16 байтів:
static_assert(sizeof(legacy::compressed_pair<int*, FinalStatelessDeleter>) == 16);
// Для stateful-делітера розмір становить 16 байтів (8 байтів покажчик + 8 байтів стан):
static_assert(sizeof(legacy::compressed_pair<int*, StatefulDeleter>) == 16);

// --- Тестування реалізації C++20 ([[no_unique_address]]) ---
// Звичайний порожній делітер:
static_assert(sizeof(modern::compressed_pair<int*, StatelessDeleter>) == 8);
// КРИТИЧНА РІЗНИЦЯ: C++20 успішно стискає final-делітер до 8 байтів!
static_assert(sizeof(modern::compressed_pair<int*, FinalStatelessDeleter>) == 8);
// Stateful-делітер:
static_assert(sizeof(modern::compressed_pair<int*, StatefulDeleter>) == 16);

// --- Тестування кінцевого розумного покажчика optimal_unique_ptr ---
static_assert(sizeof(optimal_unique_ptr<int, std::default_delete<int>>) == 8);
static_assert(sizeof(optimal_unique_ptr<int, StatelessDeleter>) == 8);
static_assert(sizeof(optimal_unique_ptr<int, FinalStatelessDeleter>) == 8);
static_assert(sizeof(optimal_unique_ptr<int, StatefulDeleter>) == 16);
```

---

### Проектування узагальненого кортежу: техніка `tuple_leaf`

Розгляньмо розвиток концепції стисненої пари до довільної кількості елементів — узагальненого кортежу `std::tuple`. У кортежі виникає серйозний виклик: користувач може створити кортеж, що містить кілька однакових порожніх типів, наприклад `std::tuple<Empty, Empty, Empty>`.

Якщо спробувати наївно застосувати `[[no_unique_address]]` до кількох однакових типів поспіль:

```cpp
struct EmptyTag {};

struct NaiveTuple {
    COURSES_NO_UNIQUE_ADDRESS EmptyTag a;
    COURSES_NO_UNIQUE_ADDRESS EmptyTag b;
    COURSES_NO_UNIQUE_ADDRESS EmptyTag c;
    int payload;
};
```

Згідно з розділом `[intro.object]` стандарту C++, два підоб'єкти **однакового типу** не можуть мати однакову адресу. Тому компілятор розмістить `a` за зміщенням 0, `b` — за зміщенням 1, `c` — за зміщенням 2. Після цього для розміщення поля `int payload` (яке вимагає 4-байтового вирівнювання) буде додано 1 байт заповнення до зміщення 4. Сумарний розмір структури `NaiveTuple` становитиме 8 байтів замість 4!

Щоб уникнути цього ефекту, бібліотеки libstdc++ та libc++ застосовують техніку типізованих листових вузлів (*tuple leaf*):

```cpp
template <size_t Index, typename T>
struct tuple_leaf {
    COURSES_NO_UNIQUE_ADDRESS T value;
};

template <typename IndexSeq, typename... Ts>
class optimal_tuple_impl;

template <size_t... Indices, typename... Ts>
class optimal_tuple_impl<std::index_sequence<Indices...>, Ts...>
    : private tuple_leaf<Indices, Ts>... {
public:
    // Конструктори та методи доступу get<I>()
};

template <typename... Ts>
using optimal_tuple = optimal_tuple_impl<std::index_sequence_for<Ts...>, Ts...>;
```

Чому ця ідіома працює ідеально?
Завдяки параметру шаблона `Index`, класи `tuple_leaf<0, EmptyTag>`, `tuple_leaf<1, EmptyTag>` та `tuple_leaf<2, EmptyTag>` є трьома **абсолютно різними типами** для системи типів C++. Оскільки їхні типи різняться, правило заборони однакових адрес для них не діє: компілятор має право призначити всім трьом базовим підоб'єктам зміщення 0. Якщо кортеж містить лише порожні типи, його розмір становитиме рівно 1 байт (як повного об'єкта), а за наявності корисного поля `int` — рівно 4 байти.

---

### Безпека до винятків та умовний noexcept (*exception safety*)

У системному програмуванні на C++ критично важливо, щоб допоміжні обгортки не створювали неявних накладних витрат під час генерації коду обробки винятків. Якщо операції переміщення або копіювання елементів пари не викидають винятків, методи самої пари `compressed_pair` зобов'язані поширювати специфікатор `noexcept`.

У сучасній версії C++20 це досягається виразами умовного `noexcept`:

```cpp
template <typename T1, typename T2>
class noexcept_compressed_pair {
    COURSES_NO_UNIQUE_ADDRESS T1 first_{};
    COURSES_NO_UNIQUE_ADDRESS T2 second_{};

public:
    constexpr noexcept_compressed_pair() noexcept(
        std::is_nothrow_default_constructible_v<T1> &&
        std::is_nothrow_default_constructible_v<T2>) = default;

    constexpr noexcept_compressed_pair(noexcept_compressed_pair&& other) noexcept(
        std::is_nothrow_move_constructible_v<T1> &&
        std::is_nothrow_move_constructible_v<T2>)
        : first_{std::forward<T1>(other.first_)},
          second_{std::forward<T2>(other.second_)} {}

    constexpr noexcept_compressed_pair& operator=(noexcept_compressed_pair&& other) noexcept(
        std::is_nothrow_move_assignable_v<T1> &&
        std::is_nothrow_move_assignable_v<T2>) {
        first_ = std::forward<T1>(other.first_);
        second_ = std::forward<T2>(other.second_);
        return *this;
    }

    constexpr void swap(noexcept_compressed_pair& other) noexcept(
        std::is_nothrow_swappable_v<T1> &&
        std::is_nothrow_swappable_v<T2>) {
        using std::swap;
        swap(first_, other.first_);
        swap(second_, other.second_);
    }
};
```

Чому це принципово для продуктивності?
Стандартний вектор `std::vector` під час динамічного перерозподілу пам'яті (*reallocation*) перевіряє умову `std::is_nothrow_move_constructible_v<T>`. Якщо об'єкт у векторі містить `compressed_pair` без коректного `noexcept`, вектор відмовиться від швидкого переміщення елементів і виконуватиме повільне копіювання для збереження суворої гарантії безпеки винятків (*strong exception safety guarantee*).

Крім того, у разі роботи з некопійовними типами (наприклад, делітерами, що тримають дескриптор сокета чи унікальний файл), відсутність `noexcept` може призвести до помилок компіляції в алгоритмах, які вимагають переміщення без винятків. Декларація умовного `noexcept` гарантує, що компілятор обиратиме оптимальний шлях виконання як для тривіальних типів без стану, так і для важких користувацьких структур.

---

### Порівняльний аналіз та рекомендації для архітектури

Підсумуємо сильні та слабкі сторони обох підходів при створенні бібліотечних компонентів:

| Критерій | Empty Base Optimization (C++11/17) | `[[no_unique_address]]` (C++20) |
| :--- | :--- | :--- |
| **Складність реалізації** | Висока (допоміжні класи, спеціалізації, SFINAE) | Мінімальна (декларативний атрибут біля поля) |
| **Підтримка `final`-типів** | Неможлива (вимагає вимкнення оптимізації) | Повна (стискаються на рівні полів) |
| **Сумісність зі скалярами** | Вимагає розгалуження через метафункції | Автоматична (атрибут ігнорується для скалярів) |
| **Вплив на пошук імен** | Можливі колізії імен методів бази й спадкоємця | Відсутній (імена інкапсульовані в полях) |
| **Підтримка constexpr** | Обмежена у складних ієрархіях C++11 | Повна та природна в C++20 |
| **Сумісність компіляторів** | Усі компілятори C++98/11/14/17 | Потрібен макрос для MSVC (`[[msvc::...]]`) |

Для нових проектів, що використовують стандарт C++20 або новіший, атрибут `[[no_unique_address]]` є єдиним рекомендованим вибором. Для фундаментальних бібліотек, що зобов'язані зберігати зворотну сумісність зі старими стандартами, класична структура `compressed_pair` на основі EBO залишається незамінним будівельним блоком.
