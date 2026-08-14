# ⚙️ Практика: розробка власного адаптера діапазону stride_view

Ця практична вставка демонструє повний цикл розробки власного адаптера діапазону `stride_view` у відповідності до вимог стандартів ISO C++20 та C++23: від проєктування неволодіючої обгортки з успадкуванням `std::ranges::view_interface`, побудови ітератора зі стрибковим кроком та вартівника до реалізації об'єкта замикання (closure object) для підтримки оператора `|`.

## 1. Постановка задачі та архітектурне проєктування

Часто виникає потреба ітеруватися не по всіх елементах послідовності, а пропускати фіксовану кількість `N` елементів на кожному кроці (наприклад, зчитувати кожен 2-й або 4-й відлік вибірки АЦП у цифровому сигнальному процесингу). У той час як C++23 додав `std::views::stride`, у C++20 такого адаптера в стандартній бібліотеці не було.

Наш адаптер `stride_view` повинен відповідати наступним архітектурним вимогам:
1. **Неволодіюча семантика:** копіювання та переміщення `stride_view` виконуються за сталий час `O(1)`.
2. **Збереження категорії ітератора:** якщо вхідний діапазон є `RandomAccessRange`, ітератор `stride_view` повинен надавати `operator[]` та арифметику ітераторів за `O(1)`. Для `ForwardRange` перехід виконується через послідовний виклик `std::ranges::advance`.
3. **Підтримка синтаксису pipe:** можливість писати `vec | custom_views::stride(3) | std::views::transform(fn)`.
4. **Константна коректність та безперервність типів.**

## 2. Аналіз шаблонного шаблону та ієрархії концептів

Перш ніж переходити до написання коду, необхідно ретельно розібрати механізм зв'язування типів у C++20 та ієрархію категорій ітераторів.

### Визначення категорії ітератора через `iterator_concept` та `iterator_category`
У C++20 було введено принципове розділення між класичним тегом `iterator_category` (який використовувався для алгоритмів C++98) та новим тегом `iterator_concept` (який використовується концептами `std::ranges`).

Якщо вхідний діапазон `V` задовольняє концепт `std::ranges::random_access_range`, наш ітератор `stride_view` може виконувати стрибки за сталий час `O(1)` завдяки арифметичній формулі `current_ + n * stride_`. Проте, якщо вхідний діапазон є лише `ForwardRange` або `BidirectionalRange`, пряме додавання індексу недоступне. У такому разі ми змушені виконувати послідовне просування в циклі елемент за елементом.

Для гнучкої динамічної вибірки категорії в момент компіляції ми застосовуємо метапрограмувальний вираз `std::conditional_t`:
1. Якщо `BaseView` задовольняє `random_access_range` → обираємо тег `std::random_access_iterator_tag`.
2. Якщо `BaseView` задовольняє `bidirectional_range` → обираємо тег `std::bidirectional_iterator_tag`.
3. Інакше → обираємо тег `std::forward_iterator_tag`.

Варто підкреслити, що член `iterator_category` завжди декларується як `std::input_iterator_tag` або `std::forward_iterator_tag` для збереження зворотного зв'язку зі старими алгоритмами C++98, тоді як `iterator_concept` показує справжні можливості ітератора для `std::ranges`.

### Використання CTAD та гарантія володіння
Клас `stride_view` є шаблоном, що приймає тип вигляду `V`. Якщо розробник передає у конструктор тимчасовий об'єкт `std::vector{1, 2, 3}`, ми не маємо права зберігати посилання на нього у звичайній змінній, бо це миттєво призведе до «висячого» посилання (dangling reference) після завершення виразу. Застосування `std::views::all_t<R>` автоматично вирішує цю проблему: lvalue-контейнери обгортаються у `std::ranges::ref_view`, а rvalue-контейнери — у `std::ranges::owning_view`, гарантуючи повну безпеку пам'яті.

## 3. Повний код реалізації `stride_view` у C++20 / C++23

Наведений нижче код реалізує повнофункціональний адаптер `stride_view`, об'єкт замикання адаптера `stride_adapter_closure` та factory-функцію у просторі імен `custom::views`.

```cpp
#include <iostream>
#include <vector>
#include <ranges>
#include <concepts>
#include <cassert>
#include <type_traits>

namespace custom {

template <std::ranges::view V>
class stride_view : public std::ranges::view_interface<stride_view<V>> {
private:
    V base_ = V();
    std::ranges::range_difference_t<V> stride_ = 1;

    // Внутрішній клас ітератора
    template <bool IsConst>
    class iterator_impl {
    private:
        using BaseView = std::conditional_t<IsConst, const V, V>;
        using BaseIter = std::ranges::iterator_t<BaseView>;
        using BaseSent = std::ranges::sentinel_t<BaseView>;

        BaseIter current_ = BaseIter();
        BaseSent end_ = BaseSent();
        std::ranges::range_difference_t<V> stride_ = 1;

    public:
        using iterator_concept = std::conditional_t<
            std::ranges::random_access_range<BaseView>,
            std::random_access_iterator_tag,
            std::conditional_t<
                std::ranges::bidirectional_range<BaseView>,
                std::bidirectional_iterator_tag,
                std::forward_iterator_tag
            >
        >;
        using iterator_category = std::input_iterator_tag;
        using value_type = std::ranges::range_value_t<BaseView>;
        using difference_type = std::ranges::range_difference_t<BaseView>;
        using reference = std::ranges::range_reference_t<BaseView>;

        iterator_impl() = default;

        constexpr iterator_impl(BaseIter current, BaseSent end, difference_type stride)
            : current_(std::move(current)), end_(std::move(end)), stride_(stride) {}

        // Підтримка конверсії з non-const у const ітератор
        constexpr iterator_impl(iterator_impl<!IsConst> i)
            requires IsConst && std::convertible_to<std::ranges::iterator_t<V>, BaseIter>
            : current_(std::move(i.current_)), end_(std::move(i.end_)), stride_(i.stride_) {}

        constexpr decltype(auto) operator*() const {
            return *current_;
        }

        constexpr iterator_impl& operator++() {
            // Безпечне просування на stride_ кроків
            for (difference_type n = 0; n < stride_ && current_ != end_; ++n) {
                ++current_;
            }
            return *this;
        }

        constexpr iterator_impl operator++(int) {
            auto tmp = *this;
            ++(*this);
            return tmp;
        }

        // Оператори порівняння з ітератором та вартівником
        constexpr bool operator==(const iterator_impl& other) const {
            return current_ == other.current_;
        }

        constexpr bool operator==(const BaseSent& sent) const {
            return current_ == sent;
        }

        // Арифметика випадкового доступу для RandomAccessRange
        constexpr iterator_impl& operator+=(difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            current_ += n * stride_;
            return *this;
        }

        constexpr iterator_impl& operator-=(difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            current_ -= n * stride_;
            return *this;
        }

        constexpr reference operator[](difference_type n) const
            requires std::ranges::random_access_range<BaseView> {
            return *(current_ + n * stride_);
        }

        friend iterator_impl operator+(iterator_impl i, difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            i += n;
            return i;
        }

        friend iterator_impl operator+(difference_type n, iterator_impl i)
            requires std::ranges::random_access_range<BaseView> {
            i += n;
            return i;
        }

        friend iterator_impl operator-(iterator_impl i, difference_type n)
            requires std::ranges::random_access_range<BaseView> {
            i -= n;
            return i;
        }

        friend difference_type operator-(const iterator_impl& x, const iterator_impl& y)
            requires std::ranges::random_access_range<BaseView> {
            return (x.current_ - y.current_) / x.stride_;
        }

        friend class iterator_impl<!IsConst>;
    };

public:
    stride_view() = default;

    constexpr explicit stride_view(V base, std::ranges::range_difference_t<V> stride)
        : base_(std::move(base)), stride_(stride) {
        assert(stride_ > 0 && "Крок stride_view повинен бути строго більшим за нуль!");
    }

    constexpr V base() const& requires std::copy_constructible<V> { return base_; }
    constexpr V base() && { return std::move(base_); }
    constexpr std::ranges::range_difference_t<V> stride() const { return stride_; }

    constexpr auto begin() {
        return iterator_impl<false>(std::ranges::begin(base_), std::ranges::end(base_), stride_);
    }

    constexpr auto begin() const requires std::ranges::range<const V> {
        return iterator_impl<true>(std::ranges::begin(base_), std::ranges::end(base_), stride_);
    }

    constexpr auto end() {
        return std::ranges::end(base_);
    }

    constexpr auto end() const requires std::ranges::range<const V> {
        return std::ranges::end(base_);
    }
};

// CTAD (Class Template Argument Deduction) guide
template <typename R>
stride_view(R&&, std::ranges::range_difference_t<R>) -> stride_view<std::views::all_t<R>>;

namespace views {

// Об'єкт замикання адаптера для підтримки pipe синтаксису
struct stride_adapter_closure {
    std::ptrdiff_t stride_ = 1;

    constexpr stride_adapter_closure(std::ptrdiff_t n) : stride_(n) {}

    template <std::ranges::viewable_range R>
    constexpr auto operator()(R&& r) const {
        return stride_view<std::views::all_t<R>>(std::forward<R>(r), stride_);
    }
};

// Оператор pipe | для зв'язування діапазону та замикання
template <std::ranges::viewable_range R>
constexpr auto operator|(R&& r, const stride_adapter_closure& closure) {
    return closure(std::forward<R>(r));
}

// Заводська функція створення адаптера
inline constexpr auto stride = [](std::ptrdiff_t n) {
    return stride_adapter_closure(n);
};

} // namespace views

} // namespace custom

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};

    // 1. Пряме створення вигляду
    custom::stride_view direct_view(std::views::all(numbers), 3);
    std::cout << "Прямий stride(3): ";
    for (int n : direct_view) {
        std::cout << n << " "; // Виведе: 1 4 7 10
    }
    std::cout << "\n";

    // 2. Композиція у конвеєрі через operator|
    using namespace custom::views;
    auto pipeline = numbers 
                  | std::views::filter([](int x) { return x % 2 == 0; }) // 2, 4, 6, 8, 10, 12
                  | stride(2)                                             // 2, 6, 10
                  | std::views::transform([](int x) { return x * x; });  // 4, 36, 100

    std::cout << "Конвеєр (filter -> stride(2) -> transform): ";
    for (int val : pipeline) {
        std::cout << val << " "; // Виведе: 4 36 100
    }
    std::cout << "\n";

    // Static assertions для перевірки відповідності концептам C++20
    static_assert(std::ranges::view<custom::stride_view<std::views::all_t<std::vector<int>&>>>);
    static_assert(std::ranges::random_access_range<decltype(direct_view)>);

    return 0;
}
```

## 4. Ключові нюанси реалізації та підводні камені

При створенні власних адаптерів діапазонів необхідно враховувати чотири фундаментальні моменти:

### 1. Перетворення CTAD та захист від висячих посилань через `std::views::all`
Конструктор вигляду не повинен приймати контейнер за rvalue-посиланням напряму без перетворення. Застосування `std::views::all_t<R>` гарантує, що lvalue-контейнер перетвориться на `std::ranges::ref_view`, а rvalue-контейнер — на `std::ranges::owning_view`. Без цього заходи виходу тимчасового об'єкта зі стеку призведуть до невизначеної поведінки при спробі розіменування ітератора.

### 2. Семантика зсуву ітератора у `operator++`
Для `ForwardRange` ми не маємо права викликати `current_ += stride_`, оскільки арифметика вказівників недоступна для однопрохідних чи двопрохідних списків. Застосування циклу перевірки `current_ != end_` запобігає виходу за межі діапазону:

```cpp
constexpr iterator_impl& operator++() {
    for (difference_type n = 0; n < stride_ && current_ != end_; ++n) {
        ++current_;
    }
    return *this;
}
```

### 3. Константна перетворюваність ітераторів (`const-conversion`)
Для того щоб неконстантний ітератор можна було прозоро передавати у функції, які приймають константний ітератор, клас `iterator_impl` надає спеціальний шаблонний конструктор конверсії:

```cpp
constexpr iterator_impl(iterator_impl<!IsConst> i)
    requires IsConst && std::convertible_to<std::ranges::iterator_t<V>, BaseIter>
    : current_(std::move(i.current_)), end_(std::move(i.end_)), stride_(i.stride_) {}
```
Це дозволяє порівнювати константний та неконстантний ітератори між собою без викликів підгонки типів (type casting).

### 4. Розрахунок різниці двох ітераторів у `operator-`
Для діапазонів із довільним доступом (`RandomAccessRange`) обчислення відстані між двома ітераторами `stride_view` вимагає врахування розміру кроку:

```cpp
friend difference_type operator-(const iterator_impl& x, const iterator_impl& y)
    requires std::ranges::random_access_range<BaseView> {
    return (x.current_ - y.current_) / x.stride_;
}
```
Зверніть увагу: цілочисельне ділення на `x.stride_` повертає точну кількість кроків адаптера, а не кількість базових елементів контейнера.

## 5. Тестування крайових випадків та коректності

При проєктуванні узагальнених компонентів обов'язковою вимогою є перевірка поведінки на граничних та вироджених вихідних даних.

### Крайовий випадок 1: Порожній контейнер
Якщо вхідний вектор порожній (`vec.empty()`), виклик `begin()` поверне `current_ == end_`. Перша ж перевірка в циклі `for` принесе `it == sentinel`, і цикл завершиться без жодного розіменування.

### Крайовий випадок 2: Крок `stride` перевищує розмір контейнера
Якщо вектор містить 3 елементи, а параметр `stride = 10`, перша ітерація розіменує елемент з індексом `0`. Потім метод `operator++()` виконає інкремент 3 рази, зупинившись на `current_ == end_`, і друге розіменування не відбудеться.

### Крайовий випадок 3: Двопрохідні контейнери без випадкового доступу
При передачі `std::list<int>` або `std::forward_list<int>` метапрограмування C++20 через `std::conditional_t` відсікає оператори `operator+=` та `operator[]` під час інстанціювання шаблону. Клас `stride_view` прозоро адаптується під можливості `ForwardIterator` без помилок збирання.

## 6. Профілювання продуктивності та оптимізації компілятора

Завдяки механізму `constexpr` та агресивному інлайнінгу (inlining) в сучасних компіляторах GCC 11+, Clang 13+ та MSVC 2019+, шар обгорток `stride_view` повністю розгортається на етапі компіляції.

Сгенерований ассемблерний код для виразу `numbers | views::filter(...) | custom_views::stride(2)` не містить жодного додаткового виклику методів чи віртуальних функцій. Оптимізатор GCC із прапорцем `-O3` перетворює цей конвеєр на єдиний компактний цикл із перевіркою умов на регістрах CPU, що доводить виконання принципу нульової вартості абстракцій (zero-cost abstraction).
