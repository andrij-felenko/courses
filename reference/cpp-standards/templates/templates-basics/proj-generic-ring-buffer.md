# ⚙️ Розробка узагальненого кільцевого буфера на базі типів і NTTP

Кільцевий буфер (англ. *circular buffer* або *ring buffer*) фіксованого розміру є одним із найбільш затребуваних будівельних блоків у системному програмуванні, драйверах периферійних пристроїв, комунікаційних стеках, обробці цифрових аудіосигналів (DSP) та високочастотних торгових системах (Low-Latency Trading). Він реалізує чергу типу First-In-First-Out (FIFO) зі строго константним споживанням пам'яті та детермінованим часом операцій `O(1)` без жодного звернення до динамічної купи під час роботи.

У цьому практичному проєкті ми побудуємо узагальнений контейнер `RingBuffer<T, Capacity>`, який поєднує параметризацію типом `typename T` із нетипізованим параметром розміру `std::size_t Capacity` (NTTP). Ми розберемо архітектурний перехід від простого масиву до професійного керування неініціалізованою пам'яттю через `placement new`, забезпечимо сувору безпеку до винятків (Strong Exception Safety), реалізуємо ітератор із кільцевою адресацією, розберемо оптимізацію індексування для розмірів ступеня двійки, реалізуємо функціональні методи-шаблони трансформації `map()`, дослідимо роботу з міжрозмірними операціями копіювання, порівняємо статичний поліморфізм із динамічними віртуальними викликами, розберемо типові помилки трансляції NTTP, додамо інтеграцію з C++20 Ranges, оптимізуємо очищення для тривіальних типів, розглянемо взаємодію з AddressSanitizer, проаналізуємо потокобезпечну Lock-Free модифікацію, перевіримо механізм лінивого інстанціювання методів та налаштуємо багатофайлову компіляцію через `extern template`.

---

## Архітектурний вибір: масив проти неініціалізованої пам'яті

Найпростіший спосіб реалізації шаблону кільцевого буфера полягає у збереженні елементів усередині масиву `std::array<T, Capacity>` або сирого масиву `T buffer_[Capacity]`. Однак такий підхід створює три фундаментальні інженерні проблеми, неприйнятні для промислового системного коду:

1. **Вимога конструктора за замовчуванням:** Масив `T buffer_[Capacity]` вимагає, щоб тип `T` був за замовчуванням конструйованим (`std::is_default_constructible_v<T> == true`). Якщо тип `T` представляє дескриптор сокета, RAII-захоплювач ресурсу або складну структуру без дефолтного конструктора, такий шаблон взагалі не скомпілюється.
2. **Марні накладні витрати на ініціалізацію:** При створенні буфера на 1024 елементи компілятор змушений викликати 1024 конструктори за замовчуванням, навіть якщо буфер створюється порожнім. Це сповільнює ініціалізацію та створює зайві операції запису в пам'ять.
3. **Некоректний життєвий цикл об'єктів:** Порожні комірки буфера містять «живі» фіктивні об'єкти `T`, замість того щоб бути неініціалізованою сирою пам'яттю. Деструктори викликаються лише при знищенні всього буфера, а не в момент вилучення елемента.

Щоб створити справді професійний та універсальний контейнер, ми організуємо внутрішнє сховище як вирівняний масив сирих байтів (`alignas(alignof(T)) std::byte`), будемо явно конструювати об'єкти за місцем через розміщувальний оператор `new` (англ. *placement new*) під час викликів `push()`, і явно викликати деструктор `ptr->~T()` під час вилучення елементів у `pop()`.

---

## Повна реалізація контейнера RingBuffer

Наведений нижче клас підтримує повний життєвий цикл елементів, семантику переміщення, суворі гарантії винятків, функціональні шаблони методів, підтримку ітераторів діапазонів `range-based for`, конструктори з буферів іншої місткості та політику примусового витіснення.

```cpp
#include <iostream>
#include <cstddef>
#include <new>
#include <utility>
#include <type_traits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <iterator>
#include <algorithm>

template <typename T, std::size_t Capacity>
class RingBuffer {
    static_assert(Capacity > 0, "Розмір кільцевого буфера зобов'язаний бути більшим за 0!");

public:
    // Шаблони псевдонімів (Alias Templates) для стандартизації інтерфейсу
    using value_type      = T;
    using size_type       = std::size_t;
    using reference       = T&;
    using const_reference = const T&;
    using pointer         = T*;
    using const_pointer   = const T*;

    // Вкладений шаблон ітератора кільцевого буфера
    template <bool IsConst>
    class RingIterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type        = T;
        using difference_type   = std::ptrdiff_t;
        using pointer           = std::conditional_t<IsConst, const T*, T*>;
        using reference         = std::conditional_t<IsConst, const T&, T&>;

        RingIterator(std::conditional_t<IsConst, const RingBuffer*, RingBuffer*> buffer, size_type offset)
            : buffer_(buffer), offset_(offset) {}

        reference operator*() const {
            return (*buffer_)[offset_];
        }

        pointer operator->() const {
            return &((*buffer_)[offset_]);
        }

        RingIterator& operator++() {
            ++offset_;
            return *this;
        }

        RingIterator operator++(int) {
            RingIterator tmp = *this;
            ++offset_;
            return tmp;
        }

        bool operator==(const RingIterator& other) const noexcept {
            return buffer_ == other.buffer_ && offset_ == other.offset_;
        }

        bool operator!=(const RingIterator& other) const noexcept {
            return !(*this == other);
        }

    private:
        std::conditional_t<IsConst, const RingBuffer*, RingBuffer*> buffer_;
        size_type offset_{0};
    };

    using iterator       = RingIterator<false>;
    using const_iterator = RingIterator<true>;

    // Конструктор за замовчуванням: створює порожній буфер без конструювання елементів
    constexpr RingBuffer() noexcept : head_(0), tail_(0), size_(0) {}

    // Конструктор копіювання того ж типу
    RingBuffer(const RingBuffer& other) {
        for (size_type i = 0; i < other.size_; ++i) {
            push(other[i]);
        }
    }

    // Узагальнений конструктор копіювання з буфера іншої місткості OtherCapacity
    template <std::size_t OtherCapacity>
    explicit RingBuffer(const RingBuffer<T, OtherCapacity>& other) {
        const size_type count_to_copy = std::min(Capacity, other.size());
        for (size_type i = 0; i < count_to_copy; ++i) {
            push(other[i]);
        }
    }

    // Конструктор переміщення
    RingBuffer(RingBuffer&& other) noexcept(std::is_nothrow_move_constructible_v<T>) {
        while (!other.empty()) {
            auto val = other.pop();
            if (val) {
                push(std::move(*val));
            }
        }
    }

    // Деструктор: знищує лише реально існуючі елементи
    ~RingBuffer() noexcept {
        clear();
    }

    // Оператор копіювального присвоювання
    RingBuffer& operator=(const RingBuffer& other) {
        if (this != &other) {
            clear();
            for (size_type i = 0; i < other.size_; ++i) {
                push(other[i]);
            }
        }
        return *this;
    }

    // Оператор переміщувального присвоювання
    RingBuffer& operator=(RingBuffer&& other) noexcept(std::is_nothrow_move_constructible_v<T>) {
        if (this != &other) {
            clear();
            while (!other.empty()) {
                auto val = other.pop();
                if (val) {
                    push(std::move(*val));
                }
            }
        }
        return *this;
    }

    // Очищення буфера: оптимізовано для тривіальних та нетривіальних типів
    void clear() noexcept {
        if constexpr (!std::is_trivially_destructible_v<T>) {
            while (!empty()) {
                pop();
            }
        }
        head_ = 0;
        tail_ = 0;
        size_ = 0;
    }

    [[nodiscard]] constexpr size_type size() const noexcept { return size_; }
    [[nodiscard]] constexpr size_type capacity() const noexcept { return Capacity; }
    [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return size_ == Capacity; }

    // Додавання копіюванням: сувора безпека до винятків (Strong Exception Safety)
    bool push(const T& item) {
        if (full()) {
            return false;
        }
        // Placement new у комірку пам'яті tail_
        ::new (static_cast<void*>(element_address(tail_))) T(item);
        tail_ = next_index(tail_);
        ++size_;
        return true;
    }

    // Додавання переміщенням
    bool push(T&& item) {
        if (full()) {
            return false;
        }
        ::new (static_cast<void*>(element_address(tail_))) T(std::move(item));
        tail_ = next_index(tail_);
        ++size_;
        return true;
    }

    // Примусове додавання з витісненням найстарішого елемента при переповненні
    void push_overwrite(const T& item) {
        if (full()) {
            // Знищуємо найстаріший елемент перед перезаписом
            element_address(head_)->~T();
            head_ = next_index(head_);
            --size_;
        }
        push(item);
    }

    // Конструювання безпосередньо у буфері (Emplace)
    template <typename... Args>
    bool emplace(Args&&... args) {
        if (full()) {
            return false;
        }
        ::new (static_cast<void*>(element_address(tail_))) T(std::forward<Args>(args)...);
        tail_ = next_index(tail_);
        ++size_;
        return true;
    }

    // Вилучення елемента з поверненням через std::optional
    std::optional<T> pop() {
        if (empty()) {
            return std::nullopt;
        }
        T* ptr = element_address(head_);
        std::optional<T> result(std::move(*ptr));
        ptr->~T(); // Явний виклик деструктора вилученого об'єкта
        head_ = next_index(head_);
        --size_;
        return result;
    }

    // Доступ за логічним індексом (0 — найстаріший доданий елемент)
    reference operator[](size_type index) {
        return *element_address((head_ + index) % Capacity);
    }

    const_reference operator[](size_type index) const {
        return *element_address((head_ + index) % Capacity);
    }

    reference front() {
        if (empty()) throw std::underflow_error("RingBuffer порожній при зверненні до front()");
        return *element_address(head_);
    }

    const_reference front() const {
        if (empty()) throw std::underflow_error("RingBuffer порожній при зверненні до front() const");
        return *element_address(head_);
    }

    // Вкладений шаблон методу трансформації (Member Function Template)
    template <typename Transformer>
    auto map(Transformer&& fn) const {
        using ResultType = std::invoke_result_t<Transformer, const T&>;
        RingBuffer<ResultType, Capacity> result;
        for (size_type i = 0; i < size_; ++i) {
            result.push(fn((*this)[i]));
        }
        return result;
    }

    // Методи ітераторів
    iterator begin() noexcept { return iterator(this, 0); }
    iterator end() noexcept { return iterator(this, size_); }
    const_iterator begin() const noexcept { return const_iterator(this, 0); }
    const_iterator end() const noexcept { return const_iterator(this, size_); }
    const_iterator cbegin() const noexcept { return const_iterator(this, 0); }
    const_iterator cend() const noexcept { return const_iterator(this, size_); }

    // Метод діагностичного виведення (демонстрація лінивого інстанціювання!)
    // Вимагає наявності operator<< для типу T.
    void dump(std::string_view label = "Buffer") const {
        std::cout << "[" << label << " (size=" << size_ << "/" << Capacity << ")]: ";
        for (size_type i = 0; i < size_; ++i) {
            std::cout << (*this)[i] << " ";
        }
        std::cout << "\n";
    }

private:
    // Дружнє оголошення шаблону для доступу між екземплярами різного розміру
    template <typename U, std::size_t OtherCap>
    friend class RingBuffer;

    // Оптимізований розрахунок наступного індексу через побітову маску або остачу
    static constexpr bool is_power_of_two = (Capacity > 0) && ((Capacity & (Capacity - 1)) == 0);

    static constexpr size_type next_index(size_type idx) noexcept {
        if constexpr (is_power_of_two) {
            return (idx + 1) & (Capacity - 1);
        } else {
            return (idx + 1) % Capacity;
        }
    }

    // Допоміжний метод розрахунку адреси комірки
    T* element_address(size_type idx) noexcept {
        return reinterpret_cast<T*>(&storage_[idx * sizeof(T)]);
    }

    const T* element_address(size_type idx) const noexcept {
        return reinterpret_cast<const T*>(&storage_[idx * sizeof(T)]);
    }

    // Неініціалізоване сховище з коректним вирівнюванням
    alignas(alignof(T)) std::byte storage_[Capacity * sizeof(T)];
    size_type head_{0};
    size_type tail_{0};
    size_type size_{0};
};
```

---

## Детальний інженерний розбір ключових механізмів

### 1. Зберігання пам'яті через `alignas` та `std::byte`

Ключовим рядком у розкладці структури є оголошення буфера:
```cpp
alignas(alignof(T)) std::byte storage_[Capacity * sizeof(T)];
```
Оператор `alignof(T)` повертає вимогу апаратного вирівнювання для типу `T` у байтах (наприклад, 4 байти для `int`, 8 байтів для `double` чи покажчиків, 16 або 32 байти для типів із підтримкою SIMD-інструкцій AVX2/AVX-512). Специфікатор `alignas` змушує компілятор розмістити масив `storage_` за адресою, кратною цьому вирівнюванню.

Використання типу `std::byte` гарантує відсутність будь-яких неявних викликів конструкторів: при створенні об'єкта `RingBuffer<Widget, 100>` пам'ять залишається сирим байтовим масивом нульової вартості.

Для типів із підвищеними вимогами до вирівнювання (англ. *over-aligned types*), таких як вектори `__m256` або структури матриць для GPU-обчислень, компілятор гарантує, що базова адреса буфера завжди буде кратна 32 або 64 байтам. Це усуває небезпеку виникнення апаратного винятку процесора General Protection Fault (`#GP`), який трапляється при використанні не вирівняних векторних інструкцій завантаження пам'яті `vmovaps`.

### 2. Керування життєвим циклом об'єкта через Placement New та ручні деструктори

У звичайних масивах об'єкти існують протягом усього часу життя контейнера. У нашому `RingBuffer` об'єкти створюються та знищуються строго відповідно до семантики черги FIFO:

- **Створення елемента під час `push()` / `emplace()`:**
  Ми перетворюємо адресу відповідної комірки байтового масиву на нетипізований покажчик `void*` і передаємо його в розміщувальний оператор `::new`:
  ```cpp
  ::new (static_cast<void*>(element_address(tail_))) T(std::forward<Args>(args)...);
  ```
  Цей вираз викликає відповідний конструктор типу `T` безпосередньо у виділеному слоті пам'яті, не звертаючись до менеджера купи операційної системи.
- **Знищення елемента під час `pop()`:**
  Коли елемент вилучається з черги, ми переміщуємо його значення у результуючий об'єкт `std::optional<T>` і негайно викликаємо явний деструктор:
  ```cpp
  ptr->~T();
  ```
  Слот пам'яті переходить у статус неініціалізованого простору і стає готовим до повторного розміщення нових об'єктів.

### 3. Гарантії безпеки до винятків (Strong Exception Safety)

Усі модифікуючі методи спроектовані за принципом commit-or-rollback:
- Під час виклику `push(const T& item)` розміщувальний конструктор копіювання `T(item)` виконується до зміни індексу `tail_` та лічильника `size_`.
- Якщо конструктор копіювання кидає виняток (наприклад, виділення пам'яті всередині `std::string` завершилося невдачею), виняток вилітає назовні, а внутрішні змінні буфера залишаються в початковому коректному стані.
- Жодні індекси не зсуваються, буфер не пошкоджується і не виникає витоків раніше збережених об'єктів.

У конструкторі переміщення специфікація `noexcept(std::is_nothrow_move_constructible_v<T>)` повідомляє стандартній бібліотеці та іншим контейнерам, чи є переміщення безпечним без винятків. Це дозволяє оптимізаторам використовувати швидкі векторні перенесення пам'яті `memmove` у вищих структурах даних.

### 4. Оптимізація ступеня двійки через NTTP та compile-time розгалуження

Операція взяття залишку від ділення `(idx + 1) % Capacity` на класичних архітектурах процесорів транслюється в апаратну інструкцію цілочислового ділення `div` або `idiv`, яка виконується за 10–25 тактів процесора на x86-64 та 2–12 тактів на ARM Cortex-M.

Оскільки `Capacity` є константою часу компіляції (NTTP), ми використовуємо конструкцію `if constexpr`:
```cpp
static constexpr bool is_power_of_two = (Capacity > 0) && ((Capacity & (Capacity - 1)) == 0);

static constexpr size_type next_index(size_type idx) noexcept {
    if constexpr (is_power_of_two) {
        return (idx + 1) & (Capacity - 1);
    } else {
        return (idx + 1) % Capacity;
    }
}
```
Якщо розмір буфера обрано як ступінь двійки (наприклад, 16, 64, 256, 1024), компілятор під час Фази 2 повністю відкидає гілку ділення і генерує швидку побітову операцію `and eax, 255`, яка виконується за 1 такт процесора без затримок конвеєра.

### 5. Оптимізація очищення для тривіально деструктованих типів

У методі `clear()` ми перевіряємо властивість типу `T` через рису типу `std::is_trivially_destructible_v<T>`:
```cpp
void clear() noexcept {
    if constexpr (!std::is_trivially_destructible_v<T>) {
        while (!empty()) {
            pop();
        }
    }
    head_ = 0;
    tail_ = 0;
    size_ = 0;
}
```
Якщо буфер містить скалярні типи (`int`, `double`, `uint8_t` або прості структури C), компілятор повністю викидає цикл викликів деструкторів і генерує три інструкції запису нулів у поля `head_`, `tail_` та `size_`, що виконується миттєво.

### 6. Узагальнені міжрозмірні операції копіювання

Оскільки `RingBuffer<int, 10>` та `RingBuffer<int, 20>` є абсолютно різними типами даних, пряме присвоювання `buf10 = buf20` призведе до помилки компілятора `no match for operator=`.

Щоб дозволити безпечне перенесення даних між буферами різного розміру, ми оголосили шаблонний конструктор копіювання:
```cpp
template <std::size_t OtherCapacity>
explicit RingBuffer(const RingBuffer<T, OtherCapacity>& other);
```
Цей конструктор є явним (`explicit`) для запобігання випадковому неявному урізанню даних і копіює мінімальну кількість елементів `min(Capacity, other.size())`. Дружнє оголошення `template <typename U, std::size_t OtherCap> friend class RingBuffer;` забезпечує прямий доступ до внутрішніх структур буфера іншого розміру.

---

## Статичний поліморфізм проти динамічного диспетчеризування

Часто розробники задаються питанням: чи варто створювати абстрактний базовий клас `IQueue<T>` із віртуальними методами `virtual void push(const T&) = 0` та успадковувати `RingBuffer` від нього?

Порівняння архітектурних характеристик демонструє колосальну перевагу чистого статичного підходу на шаблонах:

1. **Ціна виклику віртуальної функції:** Кожен віртуальний виклик `queue->push(item)` вимагає зчитування покажчика на таблицю віртуальних методів (`vptr`), обчислення зміщення функції в `vtable` та виконання непрямого переходу (`call [rax + 16]`). Це унеможливлює апаратне передбачення розгалужень (Branch Prediction) на випадкових даних і коштує від 5 до 15 тактів процесора на кожен елемент.
2. **Блокування інлайнінгу та векторизації:** Компілятор не може вбудувати тіло віртуального методу на місці виклику, оскільки конкретний тип об'єкта стає відомим лише під час виконання. У шаблоні `RingBuffer` компілятор бачить весь код методу `push()` і повністю вбудовує його, об'єднуючи запис елемента з наступними математичними обчисленнями в один машинний блок.
3. **Автоматична векторизація SIMD:** Коли цикл обробки проходить по елементах шаблону `RingBuffer<float, 64>`, компілятор розгортає цикл і генерує інструкції паралельного додавання AVX2 `vaddps`, обробляючи 8 чисел з плаваючою комою за один такт процесора. У випадку з інтерфейсом `IQueue` векторизація принципово неможлива через бар'єри непрямих викликів.
4. **Економія пам'яті:** Віртуальні функції додають 8 байт покажчика `vptr` до кожного екземпляра класу, що руйнує компактність структур при створенні масивів буферів.

---

## Вкладені шаблони методів: функціональна трансформація через map()

Шаблони методів усередині шаблонів класів (англ. *Member Function Templates*) дозволяють параметризувати окремі операції власними типами, незалежними від типу самого класу `T`.

Реалізований метод `map()` приймає довільний функціональний об'єкт (лямбду, покажчик на функцію або функтор):
```cpp
template <typename Transformer>
auto map(Transformer&& fn) const {
    using ResultType = std::invoke_result_t<Transformer, const T&>;
    RingBuffer<ResultType, Capacity> result;
    for (size_type i = 0; i < size_; ++i) {
        result.push(fn((*this)[i]));
    }
    return result;
}
```

Компілятор використовує метафункцію `std::invoke_result_t` для автоматичного обчислення типу результату виклику функції `fn` над елементом `T`. Наприклад, якщо кільцевий буфер містить рядки `RingBuffer<std::string, 8>`, а лямбда повертає довжину рядка `[](const std::string& s) { return s.length(); }`, метод `map` автоматично інстанціює та поверне новий кільцевий буфер цілих чисел `RingBuffer<std::size_t, 8>` того ж розміру `Capacity`.

---

## Вкладений ітератор та інтеграція з Range-based For та C++20 Views

Для забезпечення зручності використання у сучасних алгоритмах C++ контейнер повинен підтримувати ітерацію. Оскільки елементи у кільцевому буфері можуть починатися з середини фізичного масиву і завертатися через кінець масиву на його початок (wrap-around), простий покажчик `T*` не може слугувати ітератором.

Клас реалізує узагальнений ітератор `RingIterator<IsConst>`, який зберігає логічний зсув `offset_` від початку черги `head_`. При розіменуванні `*it` ітератор викликає оператор індексації `(*buffer_)[offset_]`, автоматично виконуючи кільцеву трансформацію індексу.

Це дозволяє писати ідіоматичний код і підключати стандартні адаптери C++20 Ranges:
```cpp
#include <ranges>

RingBuffer<int, 8> numbers;
numbers.push(10);
numbers.push(15);
numbers.push(20);
numbers.push(25);

// Повноцінна ітерація через Range-based for
for (const auto& val : numbers) {
    std::cout << val << " ";
}

// Конвеєрна обробка через C++20 Views
auto even_numbers = numbers 
                  | std::views::filter([](int n) { return n % 2 == 0; })
                  | std::views::transform([](int n) { return n * 2; });

for (int n : even_numbers) {
    std::cout << "Трансформоване парне: " << n << "\n";
}
```

---

## Взаємодія з AddressSanitizer та перевірка витоків пам'яті

Під час низькорівневої роботи з сирими масивами байтів `std::byte storage_[]` динамічні аналізатори пам'яті (зокрема, AddressSanitizer — ASan) сприймають весь масив як єдиний виділений блок пам'яті на стеку. Якщо у звичайному коді виникає спроба прочитати порожній слот буфера, компілятор без додаткового інструментування може повернути старе сміття без генерації сигналу помилки segmentation fault.

Для критичних систем реального часу рекомендується додавати інструментування ASan у налагоджувальних збірках за допомогою макросів ручного отруєння пам'яті:
```cpp
#if defined(__SANITIZE_ADDRESS__) || (defined(__has_feature) && __has_feature(address_sanitizer))
#include <sanitizer/asan_interface.h>
#define ASAN_POISON_MEMORY_REGION(addr, size)   __asan_poison_memory_region((addr), (size))
#define ASAN_UNPOISON_MEMORY_REGION(addr, size) __asan_unpoison_memory_region((addr), (size))
#else
#define ASAN_POISON_MEMORY_REGION(addr, size)   ((void)0)
#define ASAN_UNPOISON_MEMORY_REGION(addr, size) ((void)0)
#endif
```

У конструкторі `RingBuffer` весь масив `storage_` позначається як отруєний (`ASAN_POISON_MEMORY_REGION`). Під час виклику `push()` пам'ять конкретної комірки розтрується (`ASAN_UNPOISON_MEMORY_REGION`) перед викликом `placement new`, а під час `pop()` — знову отруюється після виклику деструктора. Це забезпечує миттєве виявлення помилок звернення до неініціалізованих або раніше видалених слотів буфера безпосередньо в рантаймі налагодження.

---

## Типові помилки компіляції NTTP та їхнє усунення

Під час роботи з нетипізованими параметрами шаблону розробники-початківці часто стикаються з трьома характерними помилками трансляції:

### 1. Спроба передати змінну часу виконання (Runtime Variable)
```cpp
int runtime_size = 64;
// Помилка: аргумент NTTP зобов'язаний бути константою часу компіляції!
// RingBuffer<float, runtime_size> buffer; // error: 'runtime_size' is not a constant expression

// Виправлення: використання constexpr
constexpr std::size_t compile_time_size = 64;
RingBuffer<float, compile_time_size> buffer; // Успішна компіляція
```

### 2. Спроба зіставлення несумісних типів буферів
```cpp
RingBuffer<int, 32> small_buf;
RingBuffer<int, 64> large_buf;

// small_buf = large_buf; // Помилка: типи RingBuffer<int, 32> і RingBuffer<int, 64> несумісні!

// Виправлення: використання узагальненого конструктора
RingBuffer<int, 32> truncated_copy(large_buf); // Успішно копіює перші 32 елементи
```

### 3. Некоректний синтаксис виклику вкладеного шаблону map() через покажчик
```cpp
template <typename BufferPtr>
void process_buffer(BufferPtr ptr) {
    // Без префікса template парсер сприйме '<' як оператор порівняння!
    // auto res = ptr->map([](int x) { return x * 2; }); // Помилка на Фазі 1!
    
    // Виправлення: використання дисамбігуатора template
    auto res = ptr->template map([](int x) { return x * 2; });
}
```

---

## Порівняльний аналіз: RingBuffer проти std::deque та std::queue

У стандартній бібліотеці C++ черга `std::queue<T>` за замовчуванням будується поверх `std::deque<T>`. Порівняємо їхні архітектурні характеристики:

| Характеристика | `RingBuffer<T, N>` (наш шаблон) | `std::queue<T, std::deque<T>>` |
| :--- | :--- | :--- |
| **Розміщення в пам'яті** | Монолітний плоский буфер на стеку | Дворівневий масив сторінок на купі (map of chunks) |
| **Алокації пам'яті** | 0 динамічних алокацій (нульовий оверхед) | Динамічне виділення блоків сторінок через `malloc` |
| **Кеш-локальність** | Ідеальна: елементи лежать строго послідовно | Середня: перехід між сторінками викликає промахи кешу |
| **Детермінізм часу** | Суворе `O(1)` для всіх операцій | Амортизоване `O(1)`, можливі сплески затримки на алокацію |
| **Придатність до вбудованих систем** | 100% придатний (безпечний для bare-metal/MCU) | Небезпечний через непередбачуване використання купи |

У системах низької затримки (Low-Latency Trading), прошивках дронів та аудіодрайверах використання `std::deque` заборонено стандартом безпеки (MISRA C++), оскільки фрагментація купи може призвести до збою реального часу. Статичний `RingBuffer` на базі NTTP вирішує цю задачу з максимальною математичною гарантією.

---

## Потокобезпечна Lock-Free модифікація (SPSC Ring Buffer)

У багатопотокових архітектурах із моделлю «Один виробник — один споживач» (Single Producer Single Consumer — SPSC) кільцевий буфер є основним інструментом безблокувальної передачі повідомлень.

Завдяки шаблонам та атомарним операціям `std::atomic` ми можемо створити спеціалізовану lock-free версію буфера:

```cpp
#include <atomic>
#include <new>

template <typename T, std::size_t Capacity>
class LockFreeSPSCQueue {
    static_assert(Capacity > 0 && ((Capacity & (Capacity - 1)) == 0),
                  "Розмір Lock-Free черги зобов'язаний бути степенем двійки!");

public:
    LockFreeSPSCQueue() : head_(0), tail_(0) {}

    ~LockFreeSPSCQueue() {
        T dummy;
        while (pop(dummy)) {}
    }

    // Викликається винятково потоком-виробником (Producer)
    bool push(const T& item) {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t current_head = head_.load(std::memory_order_acquire);

        if ((current_tail - current_head) == Capacity) {
            return false; // Черга заповнена
        }

        ::new (static_cast<void*>(&storage_[(current_tail & (Capacity - 1)) * sizeof(T)])) T(item);
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    // Викликається винятково потоком-споживачем (Consumer)
    bool pop(T& item) {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);

        if (current_head == current_tail) {
            return false; // Черга порожня
        }

        T* ptr = reinterpret_cast<T*>(&storage_[(current_head & (Capacity - 1)) * sizeof(T)]);
        item = std::move(*ptr);
        ptr->~T();

        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

private:
    alignas(alignof(T)) std::byte storage_[Capacity * sizeof(T)];

    // Розділення індексів на різні кеш-лінії для запобігання False Sharing (64 байти)
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
};
```

У цій реалізації параметр NTTP `Capacity` забезпечує роботу швидкої побітової маски, а атомарні змінні з бар'єрами пам'яті `memory_order_acquire` та `memory_order_release` гарантують, що запис даних у пам'ять завершиться до того, як інший потік побачить оновлення індексу. Вирівнювання `alignas(64)` ізолює `head_` та `tail_` на окремих рядках процесорного кешу, виключаючи деградацію продуктивності через конфлікт кеш-ліній (англ. *False Sharing*).

---

## Практична перевірка лінивого інстанціювання

Ліниве інстанціювання методів (англ. *Lazy Member Instantiation*) гарантує, що методи шаблону класу, які не викликаються явно у коді, взагалі не транслюються компілятором і не проходять семантичну перевірку на Фазі 2.

Створимо структуру, яка свідомо не підтримує форматування та виведення в текстовий потік:

```cpp
struct HardwareFrame {
    std::uint32_t packet_id;
    std::uint16_t payload_crc;
    double timestamp;

    HardwareFrame(std::uint32_t id, std::uint16_t crc, double ts)
        : packet_id(id), payload_crc(crc), timestamp(ts) {}

    // operator<< свідомо ВІДСУТНІЙ!
};
```

Протестуємо поведінку компілятора:

```cpp
void test_lazy_compilation() {
    // 1. Успішна компіляція для HardwareFrame:
    RingBuffer<HardwareFrame, 32> telemetry_queue;
    telemetry_queue.emplace(101, 0xA4F2, 42.001);
    telemetry_queue.emplace(102, 0x11B0, 42.002);

    auto frame = telemetry_queue.pop();
    if (frame) {
        std::cout << "Отримано апаратний кадр #" << frame->packet_id << "\n";
    }

    // Компілятор успішно інстанціює emplace, pop, деструктор.
    // Метод dump() НЕ викликається, тому компілятор не перевіряє operator<<.

    // 2. Якщо розкоментувати наступний рядок, трансляція зупиниться з помилкою:
    // telemetry_queue.dump("Telemetry");
    // [error: no match for 'operator<<' (operand types are 'std::ostream' and 'HardwareFrame')]
}
```

---

## Тестування інваріантів пам'яті через клас-трекер

Щоб переконатися у відсутності витоків пам'яті або подвійного виклику деструкторів, створимо спеціальний клас-шпигун `InstanceTracker`:

```cpp
struct InstanceTracker {
    static inline int live_instances = 0;
    static inline int constructor_calls = 0;
    static inline int destructor_calls = 0;

    int id;

    explicit InstanceTracker(int val) : id(val) {
        ++live_instances;
        ++constructor_calls;
    }

    InstanceTracker(const InstanceTracker& other) : id(other.id) {
        ++live_instances;
        ++constructor_calls;
    }

    InstanceTracker(InstanceTracker&& other) noexcept : id(other.id) {
        ++live_instances;
        ++constructor_calls;
    }

    ~InstanceTracker() {
        --live_instances;
        ++destructor_calls;
    }
};

void run_memory_lifecycle_test() {
    {
        RingBuffer<InstanceTracker, 4> tracker_buffer;
        tracker_buffer.emplace(1);
        tracker_buffer.emplace(2);
        tracker_buffer.emplace(3);

        std::cout << "Створено об'єктів: " << InstanceTracker::live_instances << " (очікується 3)\n";

        auto item = tracker_buffer.pop(); // Вилучаємо один елемент
        std::cout << "Після pop(): живих " << InstanceTracker::live_instances << " (очікується 3: 2 в буфері + 1 у змінній item)\n";
    }
    // При виході з блоку знищується tracker_buffer та item
    std::cout << "Після завершення області видимості: живих " << InstanceTracker::live_instances << " (очікується 0)\n";
}
```

Цей тест підтверджує: наш узагальнений буфер конструює рівно стільки об'єктів, скільки було додано, і знищує їх рівно в момент вилучення або очищення, без жодного витоку пам'ять.

---

## Роздільна компіляція та оптимізація через extern template

У великих промислових проектах (наприклад, у прошивках авіоніки або мережевих серверах) одні й ті самі конфігурації кільцевого буфера (`RingBuffer<uint8_t, 256>`, `RingBuffer<double, 64>`) використовуються десятками вихідних файлів.

Щоб прискорити компіляцію та зменшити навантаження на лінкер, ми організуємо проект із трьох модулів:

### 1. Заголовковий файл: RingBuffer_Config.hpp
```cpp
#pragma once
#include "RingBuffer.hpp"
#include <cstdint>
#include <string>

// Оголошення зручних псевдонімів
using RawByteBuffer = RingBuffer<std::uint8_t, 256>;
using SignalBuffer  = RingBuffer<double, 64>;
using LogQueue      = RingBuffer<std::string, 16>;

// Заборона генерації коду в одиницях трансляції, що включають цей заголовок
extern template class RingBuffer<std::uint8_t, 256>;
extern template class RingBuffer<double, 64>;
extern template class RingBuffer<std::string, 16>;
```

### 2. Файл явного інстанціювання: RingBuffer_Config.cpp
```cpp
#include "RingBuffer_Config.hpp"

// Явне визначення інстанціювання: компілятор генерує асемблерний код рівно один раз
template class RingBuffer<std::uint8_t, 256>;
template class RingBuffer<double, 64>;
template class RingBuffer<std::string, 16>;
```

### 3. Файл основного модуля: main.cpp
```cpp
#include "RingBuffer_Config.hpp"
#include <iostream>

int main() {
    RawByteBuffer network_rx_queue;
    network_rx_queue.push(0x7E); // Символ прапорця HDLC
    network_rx_queue.push(0xFF);
    network_rx_queue.push(0x03);

    std::cout << "Розмір черги RX: " << network_rx_queue.size() << " байт\n";

    LogQueue system_events;
    system_events.push("BOOT_OK");
    system_events.push("SENSORS_CALIBRATED");
    system_events.dump("Events");

    // Перевірка функціональної трансформації map:
    auto event_lengths = system_events.map([](const std::string& s) { return s.length(); });
    std::cout << "Довжина першої події: " << event_lengths.front() << "\n";

    // Перевірка конструктора з іншої місткості:
    RingBuffer<std::string, 4> small_event_log(system_events);
    std::cout << "Скопійовано у малий буфер: " << small_event_log.size() << " події\n";

    run_memory_lifecycle_test();
    return 0;
}
```

Під час паралельної збірки компілятор у файлі `main.cpp` пропускає повторну трансляцію тіл методів `RingBuffer`, залишаючи зовнішні символи. Усі виклики лінкуються з єдиним скомпільованим об'єктним файлом `RingBuffer_Config.o`.

---

## Інженерні висновки

Розроблений у цьому проєкті `RingBuffer<T, Capacity>` є наочною демонстрацією сили та елегантності системи шаблонів C++:
- **Повна нульова вартість абстракцій (Zero-overhead abstraction):** Пам'ять виділяється безпосередньо у складі структури без звернення до купи, а розрахунок індексів оптимізується до однотактових побітових масок.
- **Строгий контроль життєвого циклу:** Завдяки поєднанню сирого сховища, `placement new` та ручних деструкторів контейнер підтримує типи без дефолтних конструкторів і не створює зайвих об'єктів.
- **Гнучкість та безпека:** Реалізація відповідає суворим гарантіям винятків, підтримує ітератори, методи-шаблони трансформації та надає масштабований механізм керування компіляцією через `extern template`.
