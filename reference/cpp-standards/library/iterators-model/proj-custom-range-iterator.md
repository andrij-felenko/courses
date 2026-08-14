# ⚙️ Практика: реалізація власного ітератора та адаптера діапазонів

У цій практичній вставці ми розберемо покрокове створення власного розрідженого ітератора кроку (англ. *strided iterator*) та асиметричного вартового кінця рядка (англ. *null-terminated sentinel*). Приклад демонструє підтримку двох світів C++: класичного підходу C++17 на основі `std::iterator_traits` та сучасного підходу C++20 на основі концептів `std::random_access_iterator` і `std::sentinel_for`.

Також ми порівняємо цей підхід із низькорівневим C-стилем обходу масивів через крокові курсори.

## Задача: Розріджений обхід масивів та дешифрація сигналів

У задачах обробки сигналів, комп'ютерного зору (OpenCV) та геометрії нерідко виникає потреба обробляти не кожен елемент масиву, а лише кожен `k`-й елемент (наприклад, зчитувати лише червоний канал RGB-зображення з інтервалом у 3 байти або брати кожну 4-ту відбірку звукового сигналу).

Якщо створювати новий `std::vector` із вибраними елементами, ми витратимо час на виділення динамічної пам'яті (англ. *heap allocation*) та копіювання даних. Це створює непотрібний тиск на кеш процесора (L1/L2 data cache) та менеджери пам'яті операційної системи. Потрібно створити **ледачий ітератор кроку** (англ. *strided iterator*), який обгортає оригінальний ітератор і при кожному інкременті `++it` зсувається на `k` позицій вперед без створення копій даних та без додаткового виділення динамічної пам'яті.

## Проектування C-курсора проти C++20 ітератора

Перш ніж переходити до реалізації мовою C++, розглянемо, як ця задача вирішується мовою C. У C відсутні шаблони та перевантаження операторів, тому обхід реалізується через структуру-курсор `struct stride_cursor`:

:::tabs
```c
#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>

// Структура крокового курсора мовою C
typedef struct {
    const int* ptr;       // Поточна адреса елемента
    const int* end;       // Адреса за останнім елементом масиву
    size_t stride;        // Крок зсуву (наприклад, 2 або 3)
} stride_cursor_t;

// Ініціалізація курсора
stride_cursor_t stride_cursor_init(const int* array, size_t size, size_t stride) {
    stride_cursor_t cursor;
    cursor.ptr = array;
    cursor.end = array + size;
    cursor.stride = stride;
    return cursor;
}

// Перевірка, чи не досягнуто кінця
bool stride_cursor_has_next(const stride_cursor_t* cursor) {
    return cursor->ptr < cursor->end;
}

// Перехід до наступного елемента з кроком
void stride_cursor_next(stride_cursor_t* cursor) {
    if (cursor->ptr < cursor->end) {
        cursor->ptr += cursor->stride;
    }
}

// Отримання поточного значення
int stride_cursor_get(const stride_cursor_t* cursor) {
    return *(cursor->ptr);
}

int main(void) {
    int data[] = {10, 20, 30, 40, 50, 60, 70, 80, 90};
    size_t count = sizeof(data) / sizeof(data[0]);

    // Обхід кожного 2-го елемента мовою C
    stride_cursor_t cursor = stride_cursor_init(data, count, 2);
    printf("C-style stride traversal: ");
    while (stride_cursor_has_next(&cursor)) {
        printf("%d ", stride_cursor_get(&cursor));
        stride_cursor_next(&cursor);
    }
    printf("\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <iterator>
#include <concepts>
#include <ranges>
#include <cassert>

// Узагальнений кроковий ітератор C++20
template<std::random_access_iterator UnderlyingIt>
class StrideIterator {
public:
    using iterator_concept  = std::random_access_iterator_tag;
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = std::iter_value_t<UnderlyingIt>;
    using difference_type   = std::iter_difference_t<UnderlyingIt>;
    using pointer           = UnderlyingIt;
    using reference         = std::iter_reference_t<UnderlyingIt>;

    // Конструктор за замовчуванням (вимога концепту std::regular)
    StrideIterator() default = default;

    constexpr StrideIterator(UnderlyingIt current, difference_type stride)
        : current_(current), stride_(stride) {
        assert(stride > 0 && "Крок ітератора має бути строго додатним");
    }

    // Операції розіменування
    [[nodiscard]] constexpr reference operator*() const {
        return *current_;
    }

    [[nodiscard]] constexpr pointer operator->() const {
        return current_;
    }

    // Навігація вперед / назад
    constexpr StrideIterator& operator++() {
        current_ += stride_;
        return *this;
    }

    constexpr StrideIterator operator++(int) {
        StrideIterator temp = *this;
        ++(*this);
        return temp;
    }

    constexpr StrideIterator& operator--() {
        current_ -= stride_;
        return *this;
    }

    constexpr StrideIterator operator--(int) {
        StrideIterator temp = *this;
        --(*this);
        return temp;
    }

    // Арифметика довільного доступу
    constexpr StrideIterator& operator+=(difference_type n) {
        current_ += n * stride_;
        return *this;
    }

    constexpr StrideIterator& operator-=(difference_type n) {
        current_ -= n * stride_;
        return *this;
    }

    [[nodiscard]] friend constexpr StrideIterator operator+(StrideIterator it, difference_type n) {
        it += n;
        return it;
    }

    [[nodiscard]] friend constexpr StrideIterator operator+(difference_type n, StrideIterator it) {
        it += n;
        return it;
    }

    [[nodiscard]] friend constexpr StrideIterator operator-(StrideIterator it, difference_type n) {
        it -= n;
        return it;
    }

    [[nodiscard]] friend constexpr difference_type operator-(const StrideIterator& lhs, const StrideIterator& rhs) {
        assert(lhs.stride_ == rhs.stride_ && "Порівняння ітераторів з різним кроком неможливе");
        return (lhs.current_ - rhs.current_) / lhs.stride_;
    }

    // Доступ за індексом
    [[nodiscard]] constexpr reference operator[](difference_type n) const {
        return *(*this + n);
    }

    // Порівняння рівності та порядку
    [[nodiscard]] friend constexpr bool operator==(const StrideIterator& lhs, const StrideIterator& rhs) {
        return lhs.current_ == rhs.current_;
    }

    [[nodiscard]] friend constexpr auto operator<=>(const StrideIterator& lhs, const StrideIterator& rhs) {
        return lhs.current_ <=> rhs.current_;
    }

private:
    UnderlyingIt current_{};
    difference_type stride_{1};
};

int main() {
    std::vector<int> data = {10, 20, 30, 40, 50, 60, 70, 80, 90};

    // Створення крокових ітераторів для зчитування кожного 2-го елемента
    StrideIterator begin(data.begin(), 2);
    StrideIterator end(data.begin() + 8, 2); // Вказує на 90

    std::cout << "C++20 StrideIterator traversal: ";
    for (auto it = begin; it != end; ++it) {
        std::cout << *it << " ";
    }
    std::cout << "\n";

    // Перевірка відповідності концептам C++20 під час компіляції
    static_assert(std::random_access_iterator<StrideIterator<std::vector<int>::iterator>>);
    return 0;
}
```
:::

## Покроковий розбір реалізації C++20 StrideIterator

Розглянемо ключові елементи дизайну класу `StrideIterator`, які забезпечують його повну сумісність із концептами стандарту C++20:

### 1. Використання асоційованих типів C++20
Замість прямих оголошень типів через `typename UnderlyingIt::value_type`, у C++20 ми використовуємо меташаблони `std::iter_value_t<UnderlyingIt>` та `std::iter_reference_t<UnderlyingIt>`. Це гарантує, що `StrideIterator` буде однаково успішно працювати як з контейнерами `std::vector`, так і з сирими вказівниками C-стилю `const int*`, у яких немає вкладених синонімів типів.

### 2. Оголошення двох категорій тегів: `iterator_concept` та `iterator_category`
Ми визначаємо два синоніми категорій:
- `iterator_concept = std::random_access_iterator_tag;` — для нових алгоритмів C++20 Ranges.
- `iterator_category = std::random_access_iterator_tag;` — для класичних алгоритмів C++98/17 (`std::iterator_traits`).

Це дозволяє компілятору обирати найбільш оптимізовану гілку алгоритму як у застарілому, так і у сучасному коді.

### 3. Механіка оператора віднімання `operator-` та масштабування різниці
Оператор віднімання двох крокових ітераторів `operator-(lhs, rhs)` повертає кількість **кроків** між ними, а не абсолютну кількість елементів у пам'яті. Саме тому вираз `(lhs.current_ - rhs.current_) / lhs.stride_` ділить математичну різницю вказівників на величину кроку `stride_`. Це критично для правильної роботи таких функцій, як `std::distance` та `std::ranges::distance`, які розраховують на логічну кількість елементів у діапазоні.

### 4. Використання тристороннього порівняння `operator<=>`
Завдяки оператору spaceship `operator<=>` у C++20, нам не потрібно писати окремі шість операторів порівняння (`==`, `!=`, `<`, `>`, `<=`, `>=`). Компілятор автоматично генерує всі нерівності на основі порівняння внутрішніх ітераторів `current_`.

## Аналіз відмінностей C та C++ реалізацій

Порівняння двох підходів демонструє глибоку фундаментальну різницю між імперативним курсором C та алгебраїчним ітератором C++:

1. **Безпека типів та компіляційна перевірка**: C-курсор `stride_cursor_t` працює виключно з вказівниками типу `const int*`. Щоб обробити `float` або структуру `Vector3D`, доведеться створювати новий дублікат функції або використовувати небезпечний `void*` з явним приведенням типів. C++ шаблон `StrideIterator<UnderlyingIt>` приймає **будь-який** ітератор довільного доступу (`std::vector<T>`, `std::array<T>`, сирий вказівник `T*`) і перевіряє вимоги концепту `std::random_access_iterator` ще до запуску програми.

2. **Інтеграція зі стандартними алгоритмами**: C-курсор вимагає ручного написання циклу `while(stride_cursor_has_next(&cursor))`. Об'єкт `StrideIterator` у C++ сумісний із будь-якими стандартними алгоритмами STL — його можна передавати в `std::copy`, `std::accumulate`, `std::find_if` або `std::ranges::sort`.

3. **Накладні витрати (Zero-Overhead)**: У C++ завдяки операції інлайнінгу (`constexpr` та `inline`) виклик `operator++` для `StrideIterator` компілюється в одну машинную інструкцію додавання зсуву до адресного регістру `add rdi, 8` — точно так само, як і в код мови C.

## Простеження машинного коду та кеш-ефективність

При виконанні циклу з кроком `stride` процесор взаємодіє з підсистемою пам'яті через кеш-лінії (англ. *cache lines*), розмір яких у більшості сучасних архітектур (x86_64, ARM64) становить 64 байти.

Якщо ми ітеруємося по масиву `int` (4 байти) з кроком `stride = 1`, одна 64-байтова кеш-лінія містить 16 елементів. Перше звернення викликає промах кешу (англ. *cache miss*), але наступні 15 звернень відбуваються миттєво з кешу L1.

Якщо ж ми використовуємо `StrideIterator` з кроком `stride = 16`, кожне розіменування `*it` влучає у нову кеш-лінію. Апаратний префетчер процесора (англ. *hardware data prefetcher*) аналізує регулярність зсувів адрес у регістрі `rdi` і автоматично завантажує наступні кеш-лінії з оперативної пам'яті до того, як інструкція розіменування насправді виконається.

Компілятор GCC та Clang під час оптимізації `-O3` повністю розгортає `StrideIterator` у такий асемблерний цикл:

```assembly
.L3:
    mov     eax, DWORD PTR [rdi]        ; eax = *current_
    add     rdi, rsi                    ; rdi += stride * sizeof(int)
    call    print_int                   ; виклик функції обробки
    cmp     rdi, rdx                    ; порівняння з end_
    jne     .L3                         ; продовження циклу
```

Як видно з дизасемблерного коду, жодних тимчасових об'єктів або віртуальних викликів не створюється. Шаблонна абстракція C++ повністю зникає під час компіляції.

## Реалізація асиметричного вартового Нуль-Термінованого Рядка (C++20)

Розглянемо другий приклад: створення **вартового кінця рядка** `NullTerminatedSentinel`, який дозволяє ітеруватися по звичайному C-рядку `const char*` без попереднього обчислення його довжини через `strlen()`.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>

// Прохід по C-рядку до null-термінатора мовою C
void print_c_string(const char* str) {
    printf("C-string traversal: ");
    while (*str != '\0') {
        printf("%c", *str);
        str++;
    }
    printf("\n");
}

int main(void) {
    const char* text = "Hello, C++20 Sentinels!";
    print_c_string(text);
    return 0;
}
```
```cpp
#include <iostream>
#include <concepts>
#include <iterator>
#include <algorithm>

// Об'єкт-вартовий C++20 для нуль-термінованих рядків
struct NullTerminatedSentinel {
    // Порівняння вартового з будь-яким ітератором, що читає char
    template<std::indirectly_readable It>
    requires std::same_as<std::iter_value_t<It>, char>
    friend constexpr bool operator==(It it, NullTerminatedSentinel) {
        return *it == '\0'; // Умова зупинки — досягнення нуля
    }
};

int main() {
    const char* text = "Hello, C++20 Sentinels!";

    // Обхід діапазону [text, NullTerminatedSentinel{})
    std::cout << "C++20 Sentinel traversal: ";
    for (auto it = text; it != NullTerminatedSentinel{}; ++it) {
        std::cout << *it;
    }
    std::cout << "\n";

    // Перевірка відповідності концепту std::sentinel_for під час компіляції
    static_assert(std::sentinel_for<NullTerminatedSentinel, const char*>);

    // Використання зі стандартними алгоритмами C++20 ranges
    auto count = std::ranges::distance(text, NullTerminatedSentinel{});
    std::cout << "Computed string length via sentinel without strlen(): " << count << "\n";

    return 0;
}
```
:::

## Детальний розбір роботи вартового (Sentinel Mechanics)

У традиційній моделі C++98 для обходу рядка `text` доводилося писати таке:

```cpp
const char* text = "Hello World";
const char* end = text + std::strlen(text); // Прохід №1 по всьому рядку
std::for_each(text, end, print_char);       // Прохід №2 по всьому рядку
```

Це змушувало процесор двічі сканувати ту саму ділянку оперативної пам'яті. Перший прохід Шукав символ `\0` для обчислення адреси `end`, а другий прохід виконував корисну роботу.

Введення вартового `NullTerminatedSentinel` у C++20 повністю усуває перший прохід. Оскільки тип вартового не зобов'язаний бути ітератором і не зберігає жодної адреси у пам'яті (його розмір `sizeof(NullTerminatedSentinel) == 1` як порожньої структури), операція порівняння `it == NullTerminatedSentinel{}` перетворюється у простий вираз `*it == '\0'`. 

Таким чином, цикл виконує корисну роботу та перевірку умови зупинки **за один єдиний прохід по пам'яті**.

## Обертання ітератора в Range Adaptor (C++20 views::stride)

Щоб зробити `StrideIterator` ще більш зручним у повсякденному розробленні, у C++20 ми можемо обгорнути його у зручний **вид діапазону** (англ. *range view*), який дозволить використовувати синтаксис пайплайнів `|`:

```cpp
template<std::ranges::viewable_range Range>
class StrideView : public std::ranges::view_interface<StrideView<Range>> {
public:
    StrideView() = default;
    
    constexpr StrideView(Range&& range, std::ranges::range_difference_t<Range> stride)
        : range_(std::forward<Range>(range)), stride_(stride) {}

    constexpr auto begin() {
        return StrideIterator(std::ranges::begin(range_), stride_);
    }

    constexpr auto end() {
        auto end_it = std::ranges::end(range_);
        // Обчислення точної межі кінця з урахуванням кроку
        auto dist = std::ranges::distance(range_);
        auto remainder = dist % stride_;
        auto offset = dist - remainder;
        return StrideIterator(std::ranges::begin(range_) + offset, stride_);
    }

private:
    Range range_{};
    std::ranges::range_difference_t<Range> stride_{1};
};
```

Завдяки цьому виробу розробник отримує чистий декларативний синтаксис обходу:

```cpp
std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Вибір кожного 3-го елемента без виділення нової пам'яті
for (int val : StrideView(numbers, 3)) {
    std::cout << val << " "; // Надрукує: 1 4 7 10
}
```

У C++23 подібна функціональність була офіційно стандартизована під назвою `std::views::stride(k)`.

## Безпека часу життя та запобігання завислим ітераторам (Dangling Iterators)

Створюючи власні види діапазонів (views), такі як `StrideView`, розробник має враховувати правила володіння даними та часу життя (англ. *lifetime safety*).

Якщо передати у `StrideView` тимчасовий контейнер (rvalue, наприклад `StrideView(make_vector(), 2)`), то після завершення повного виразу створення `StrideView` тимчасовий вектор знищується. Ітератори всередині `StrideView` стають **завислими вказівниками** (англ. *dangling iterators*), і спроба обходу в циклі `for (int val : view)` призведе до прочитання звільненої пам'яті (Use-After-Free).

У C++20 для запобігання цій помилці введено концепт `std::ranges::borrowed_range` та функцію `std::ranges::dangling`. Якщо діапазон є тимчасовим об'єктом і не гарантує збереження пам'яті (наприклад `std::vector`), алгоритми C++20 повертають об'єкт `std::ranges::dangling` замість ітератора. Це виявляє помилку використання завислого ітератора ще під час компіляції.

## Гарантії винятків та кваліфікатор noexcept

Під час виклику методів ітератора (`operator*`, `operator++`, `operator==`) стандарти C++ вимагають забезпечення певного рівня гарантій безпеки винятків (англ. *exception safety guarantees*):

- **No-throw guarantee (`noexcept`)**: Переміщення та інкремент ітераторів для суцільної пам'яті (вказівники `T*`, `std::vector::iterator`) не повинні генерувати винятків. Усі методи `StrideIterator` варто позначати кваліфікатором `noexcept(noexcept(++std::declval<UnderlyingIt&>()))`, щоб дозволити компіляторові генерувати оптимізовані інструкції розгортання циклів.
- **Basic guarantee**: Якщо оператор розіменування `operator*()` власного ітератора генерує виняток (наприклад, при зчитуванні з пошкодженого файлового потоку), стан ітератора має залишатися коректним і дозволяти його подальше знищення без витоків ресурсів.

## Обхід двовимірних матрицій через MatrixColumnIterator

У математичних та графічних алгоритмах двовимірна матриця розміром `R × C` зазвичай зберігається у пам'яті як суцільний одновимірний масив (англ. *row-major order*).

Якщо обхід елементів одного рядка є послідовним і швидко завантажується у кеш L1, то обхід стовпчика матриці вимагає зсуву на `C` елементів на кожному кроці. Для наочної реалізації обходу стовпчика двовимірної матриці ми можемо повторно використати наш `StrideIterator`, передавши `stride = C`:

```cpp
template<typename T>
class Matrix2D {
public:
    Matrix2D(size_t rows, size_t cols)
        : rows_(rows), cols_(cols), data_(rows * cols) {}

    T& at(size_t r, size_t c) { return data_[r * cols_ + c]; }

    // Ітератор для обходу c-го стовпчика матриці
    auto column_begin(size_t col_index) {
        return StrideIterator(data_.begin() + col_index, cols_);
    }

    auto column_end(size_t col_index) {
        return StrideIterator(data_.begin() + col_index + rows_ * cols_, cols_);
    }

private:
    size_t rows_;
    size_t cols_;
    std::vector<T> data_;
};
```

Цей приклад демонструє силу алгебраїчної абстракції ітератора: один і той самий клас `StrideIterator` однаково успішно працює як для дешифрації аудіосигналів, так і для лінійної алгебри та комп'ютерного зору.

## Складніший приклад: Синхронний Zip-ітератор для паралельних масивів

Іншим класичним прикладом користувацького ітератора є `ZipIterator`, який об'єднує два незалежні ітератори різних контейнерів і при розіменуванні повертає кортеж посилань `std::tuple<Ref1, Ref2>`.

Такий ітератор дозволяє паралельно обходити два масиви (наприклад, координати X та Y) в одному циклі:

```cpp
template<typename It1, typename It2>
class ZipIterator {
public:
    using value_type = std::tuple<std::iter_value_t<It1>, std::iter_value_t<It2>>;
    using reference  = std::tuple<std::iter_reference_t<It1>, std::iter_reference_t<It2>>;
    using difference_type = std::common_type_t<std::iter_difference_t<It1>, std::iter_difference_t<It2>>;
    using iterator_category = std::forward_iterator_tag;

    ZipIterator(It1 it1, It2 it2) : it1_(it1), it2_(it2) {}

    reference operator*() const {
        return reference(*it1_, *it2_);
    }

    ZipIterator& operator++() {
        ++it1_;
        ++it2_;
        return *this;
    }

    friend bool operator==(const ZipIterator& lhs, const ZipIterator& rhs) {
        return lhs.it1_ == rhs.it1_ || lhs.it2_ == rhs.it2_;
    }

private:
    It1 it1_;
    It2 it2_;
};
```

Зверніть увагу: `ZipIterator` є прикладом **проксі-ітератора**, оскільки `operator*` повертає тимчасовий об'єкт `std::tuple` посилань. У C++20 концепт `std::indirectly_readable` гарантує, що такий ітератор може безпечно використовуватися зі стандартними алгоритмами сортування та трансформації через CPO `std::ranges::iter_move`.

## Реалізація RingBufferIterator для кільцевого буфера

Ще однією практичною задачею у розробці операційних систем та систем реального часу є реалізація ітератора для кільцевого буфера (англ. *ring buffer* або *circular buffer*). У такій структурі даних масив пам'яті фіксованого розміру `N` обходить кільцевий покажчик, виконуючи остачу від ділення `(index + 1) % N`.

Розглянемо дизайн `RingBufferIterator`, який перетворює циліндричну пам'ять у лінійну послідовність для стандартних алгоритмів C++:

```cpp
template<typename T, size_t Capacity>
class RingBufferIterator {
public:
    using iterator_concept  = std::random_access_iterator_tag;
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = T;
    using difference_type   = std::ptrdiff_t;
    using pointer           = T*;
    using reference         = T&;

    RingBufferIterator(T* buffer_base, size_t head_index, difference_type pos)
        : base_(buffer_base), pos_(pos) {}

    reference operator*() const {
        return base_[(pos_) % Capacity];
    }

    pointer operator->() const {
        return &base_[(pos_) % Capacity];
    }

    RingBufferIterator& operator++() {
        ++pos_;
        return *this;
    }

    RingBufferIterator operator++(int) {
        RingBufferIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    RingBufferIterator& operator+=(difference_type n) {
        pos_ += n;
        return *this;
    }

    friend difference_type operator-(const RingBufferIterator& a, const RingBufferIterator& b) {
        return a.pos_ - b.pos_;
    }

    friend bool operator==(const RingBufferIterator& a, const RingBufferIterator& b) {
        return a.pos_ == b.pos_;
    }

    friend auto operator<=>(const RingBufferIterator& a, const RingBufferIterator& b) {
        return a.pos_ <=> b.pos_;
    }

private:
    T* base_{nullptr};
    difference_type pos_{0};
};
```

Головна алгебраїчна ідея `RingBufferIterator` полягає у відокремленні логічної позиції `pos_` (яка зростає монотонно від 0 до `size`) від фізичного індексу `pos_ % Capacity` в масиву. Завдяки цьому операції віднімання ітераторів `b - a` та порівняння `a < b` залишаються монотонними та передбачуваними для `std::sort` або `std::lower_bound`, навіть коли за ними стоїть закольцована пам'ять.

## Векторизація та SIMD інструкції для ContiguousIterator

Коли клас ітератора позначається тегом `std::contiguous_iterator_tag` у C++20, це сигналізує автовекторизатору компілятора (англ. *auto-vectorizer*), що елементи розташовані у фізично неперервному блоці пам'яті.

Для таких ітераторів GCC та Clang автоматично замінюють скалярні цикли розіменування на векторизовані інструкції AVX-256 або AVX-512 (`vmovdqu`, `vpaddd`), які обробляють 8 або 16 цілих чисел за один такт процесора:

```assembly
.L4:
    vmovdqu ymm0, YMMWORD PTR [rdi + rax*4]   ; Завантаження 8 елементів int32 у регістр AVX2
    vpaddd  ymm0, ymm0, ymm1                  ; Векторне додавання 8 елементів паралельно
    vmovdqu YMMWORD PTR [rsi + rax*4], ymm0   ; Запис 8 результатів у вихідний масив
    add     rax, 8                            ; Зсув індексу на 8
    cmp     rax, rcx
    jl      .L4
```

Якщо ж ітератор оголошує лише `random_access_iterator_tag` (але не `contiguous_iterator_tag`), компілятор мусить припустити можливість проксі-об'єктів або не-суцільного кроку і згенерувати повільніший скалярний цикл.

## Генераторний ітератор Фібоначчі (Fibonacci Generator Iterator)

Не всі ітератори зобов’язані вказувати на масив або контейнер у пам'яті. **Генераторний ітератор** (англ. *generator iterator*) обчислює значення елементів «на льоту» під час розіменування `*it`, не зберігаючи їх у RAM.

Нижче наведено приклад ітератора нескінченної послідовності чисел Фібоначчі:

```cpp
class FibonacciIterator {
public:
    using iterator_concept  = std::input_iterator_tag;
    using iterator_category = std::input_iterator_tag;
    using value_type        = uint64_t;
    using difference_type   = std::ptrdiff_t;
    using pointer           = const uint64_t*;
    using reference         = uint64_t;

    FibonacciIterator() = default;

    constexpr uint64_t operator*() const {
        return a_;
    }

    constexpr FibonacciIterator& operator++() {
        uint64_t next = a_ + b_;
        a_ = b_;
        b_ = next;
        return *this;
    }

    constexpr FibonacciIterator operator++(int) {
        FibonacciIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    friend bool operator==(const FibonacciIterator& lhs, const FibonacciIterator& rhs) {
        return lhs.a_ == rhs.a_ && lhs.b_ == rhs.b_;
    }

private:
    uint64_t a_{0};
    uint64_t b_{1};
};
```

Такий ітератор задовольняє концепт `std::input_iterator` і може використовуватися разом із `std::take_view` у C++20 для обчислення перших `N` чисел Фібоначчі без створення вектора.

## Сумісність із std::ranges::subrange у C++20

Будь-який власний ітератор `MyIt` та вартовий `MySentinel` можна об'єднати у стандартний об'єкт діапазону через `std::ranges::subrange(begin_it, sentinel)`. Це позбавляє розробника потреби писати власні класи видів (views) та забезпечує повну сумісність із ледачими адаптерами бібліотеки C++20 Ranges.

Завдяки цьому ми можемо писати вирази вигляду `std::ranges::subrange(StrideIterator(vec.begin(), 2), StrideIterator(vec.end(), 2)) | std::views::filter(is_even)`, отримати нульову ціну абстракції під час виконання та повну підтримку безпеки типів.

## Діагностика та налагодження ітераторів з AddressSanitizer

При розробці власних ітераторів найнебезпечнішими помилками є вихід за межі масиву (out-of-bounds access) та розіменування інвалідованих ітераторів. Для їх автоматичного виявлення рекомендується збирати програму із прапорцем **AddressSanitizer (ASan)**:

```bash
g++ -O2 -fsanitize=address -g main.cpp -o main
```

При виході ітератора за межі контейнера ASan зупиняє виконання та видає детальний стек викликів із зазначенням точно того рядка коду, де відбулося невалідне розіменування `*it`. Крім того, стандартні бібліотеки libstdc++ (GCC) та libc++ (Clang) підтримують режим суворої перевірки ітераторів через макрос `-D_GLIBCXX_DEBUG`, який перевіряє сумісність діапазонів `[first, last)` під час виконання кожної стандартної функції STL. Це миттєво відловлює спроби порівняння ітераторів з різних контейнерів.

## Крайові випадки та гарантії безпеки

При роботі з розрідженими ітераторами необхідно враховувати три крайові ситуації:

1. **Порожні контейнери**: Якщо контейнер містить 0 елементів, виклик `StrideIterator(vec.begin(), 2)` створить ітератор, у якого `begin == end`. Умова виходу з циклу справцює одразу, і жодного звернення до пам'яті не відбудеться.
2. **Розмір контейнера не ділиться на `stride`**: Якщо масив має 9 елементів (індекси від 0 до 8, а `vec.end()` знаходиться на індексі 9), а `stride = 2`, ітератор відвідає індекси 0, 2, 4, 6, 8 (усього 5 елементів). Пряме додавання кроку `stride = 2` до індексу 8 дало б індекс 10, що є виходом за межу `vec.end()` (індекс 9) і спричиняє невизначену поведінку (UB). Для безпечного обчислення межі обходу `StrideView` враховує відстань `dist = 9` та залишок `dist % stride_ = 9 % 2 = 1`. Зсув останнього кроку становить `dist - (dist % stride_) = 9 - 1 = 8`, а перевірка зупинки через вартовий `it.base() >= vec.end()` гарантує, що ітератор не виконує арифметику вказівників за межами масиву (не переходить на індекс 10).
3. **Від'ємні та нульові кроки**: Передача `stride <= 0` є логічною помилкою. Конструктор `StrideIterator` перевіряє цю умову через `assert(stride > 0)`.

## Типові пастки при реалізації власних ітераторів

При написанні власних ітераторів розробники найчастіше припускаються п'яти системних помилок:

1. **Забутий `difference_type`**: Якщо в класі ітератора не оголошено `using difference_type = std::ptrdiff_t;`, шаблон `std::iterator_traits` розпізнає такий клас як невалідний ітератор, і спроба передати його в `std::distance` призведе до довгої помилки компіляції.

2. **Неповернення посилання у префіксному `operator++()`**: Префіксний інкремент зобов'язаний повертати посилання на поточний об'єкт `MyIterator&`. Повернення значення за копією `MyIterator` ламає вимогу концепту `std::incrementable` і викликає зайве копіювання стану на кожному кроці циклу.

3. **Плутанина між `iterator_category` та `iterator_concept`**: Якщо ви створюєте ітератор у C++20, який є `ContiguousIterator`, обов'язково вказуйте `using iterator_concept = std::contiguous_iterator_tag;`. Якщо вказати лише `iterator_category`, нові алгоритми `std::ranges` будуть вважати його звичайним `random_access_iterator` і не застосують швидкі SIMD-оптимізації.

4. **Порушення симетрії операторів порівняння**: В операторі віднімання двох ітераторів `operator-(lhs, rhs)` обов'язково додавайте перевірку на однаковий крок. Віднімання ітераторів, що належать різним контейнерам або мають різний крок зсуву, є джерелом невизначеної поведінки.

5. **Нехтування `constexpr` та `noexcept`**: Всі методи навігації ітератора повинні позначатися кваліфікатором `constexpr`, щоб дозволити обхід масивів та обчислення алгоритмів прямо під час компіляції (у `consteval` та `constexpr` контекстах).
