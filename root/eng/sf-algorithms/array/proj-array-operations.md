# ⚙️ Реалізація динамічного масиву та кеш-вирівняні операції

Цей навчально-практичний розділ містить закончену, працездатну реалізацію динамічного масиву мовами C та C++. У ньому детально висвітлено інженерні нюанси побудови високопродуктивних контейнерів даних: механізм геометричного розширення місткості (capacity allocation strategy), апаратне вирівнювання пам'яті за межею 64-байтної кеш-лінії процесора для забезпечення оптимізованої SIMD-векторизації інструкціями AVX-512 та ARM Neon, а також забезпечення стійкості до винятків (exception safety) та RAII-управління ресурсами у C++.

Програмування низькорівневих динамічних структур вимагає чіткого розмежування між двома поняттями: кількість фактично присутніх елементів та розмір виділеного блоку пам'яті. Якщо виділяти нову пам'ять при кожному додаванні елемента, програма витрачатиме більшість часу на виклики системного аллокатора й копіювання даних. Тому представлена реалізація використовує геометричне подвоєння місткості, що забезпечує `O(1)` амортизованого часу на вставку.

## Реалізація мовами C та C++

У наведених прикладах реалізовано динамічний вектор, який автоматично подвоює свою місткість при переповненні, підтримує вставку в кінець за `O(1)` амортизованого часу, вилучення за `O(1)` та довільний доступ за індексом.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

// 64 байти — розмір стандартної кеш-лінії x86/ARM для оптимізації SIMD
#define CACHE_LINE_ALIGN 64
#define INITIAL_CAPACITY 4
#define GROWTH_FACTOR 2

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} VectorC;

// Ініціалізація вектора з апаратним вирівнюванням пам'яті
bool vector_init(VectorC *vec, size_t initial_cap) {
    if (!vec) return false;
    
    vec->size = 0;
    vec->capacity = (initial_cap > 0) ? initial_cap : INITIAL_CAPACITY;
    
    // Виділення пам'яті, кратної CACHE_LINE_ALIGN
    size_t bytes = vec->capacity * sizeof(int);
    // Вирівнюємо загальний розмір виділення до кратного alignment
    size_t aligned_bytes = (bytes + CACHE_LINE_ALIGN - 1) & ~(CACHE_LINE_ALIGN - 1);
    
    #if defined(_MSC_VER)
    vec->data = (int *)_aligned_malloc(aligned_bytes, CACHE_LINE_ALIGN);
    #else
    vec->data = (int *)aligned_alloc(CACHE_LINE_ALIGN, aligned_bytes);
    #endif

    if (!vec->data) {
        vec->capacity = 0;
        return false;
    }
    return true;
}

// Звільнення пам'яті
void vector_free(VectorC *vec) {
    if (vec && vec->data) {
        #if defined(_MSC_VER)
        _aligned_free(vec->data);
        #else
        free(vec->data);
        #endif
        vec->data = NULL;
        vec->size = 0;
        vec->capacity = 0;
    }
}

// Зміна місткості при досягненні ліміту
static bool vector_reserve(VectorC *vec, size_t new_cap) {
    if (new_cap <= vec->capacity) return true;
    
    size_t bytes = new_cap * sizeof(int);
    size_t aligned_bytes = (bytes + CACHE_LINE_ALIGN - 1) & ~(CACHE_LINE_ALIGN - 1);
    
    int *new_data = NULL;
    #if defined(_MSC_VER)
    new_data = (int *)_aligned_realloc(vec->data, aligned_bytes, CACHE_LINE_ALIGN);
    #else
    new_data = (int *)aligned_alloc(CACHE_LINE_ALIGN, aligned_bytes);
    if (new_data && vec->data) {
        memcpy(new_data, vec->data, vec->size * sizeof(int));
        free(vec->data);
    }
    #endif

    if (!new_data) return false;
    
    vec->data = new_data;
    vec->capacity = new_cap;
    return true;
}

// Вставка елемента в кінець: амортизовано O(1)
bool vector_push_back(VectorC *vec, int value) {
    if (vec->size >= vec->capacity) {
        size_t new_cap = vec->capacity * GROWTH_FACTOR;
        if (!vector_reserve(vec, new_cap)) return false;
    }
    vec->data[vec->size++] = value;
    return true;
}

// Безпечне отримання елемента за індексом
bool vector_get(const VectorC *vec, size_t index, int *out_val) {
    if (!vec || index >= vec->size || !out_val) return false;
    *out_val = vec->data[index];
    return true;
}

int main(void) {
    VectorC vec;
    if (!vector_init(&vec, 4)) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    for (int i = 0; i < 10; ++i) {
        vector_push_back(&vec, i * 10);
    }

    printf("Розмір C-вектора: %zu, Місткість: %zu\n", vec.size, vec.capacity);
    for (size_t i = 0; i < vec.size; ++i) {
        int val;
        vector_get(&vec, i, &val);
        printf("[%zu] = %d\n", i, val);
    }

    vector_free(&vec);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <utility>
#include <new>
#include <cstddef>

template <typename T, std::size_t Alignment = 64>
class DynamicArray {
private:
    T* data_{nullptr};
    std::size_t size_{0};
    std::size_t capacity_{0};

    // Оптимізоване виділення вирівняного блоку пам'яті без виклику конструкторів
    static T* allocate_aligned(std::size_t capacity) {
        if (capacity == 0) return nullptr;
        std::size_t bytes = capacity * sizeof(T);
        std::size_t aligned_bytes = (bytes + Alignment - 1) & ~(Alignment - 1);
        
        void* ptr = ::operator new[](aligned_bytes, std::align_val_t{Alignment});
        return static_cast<T*>(ptr);
    }

    static void deallocate_aligned(T* ptr) noexcept {
        if (ptr) {
            ::operator delete[](ptr, std::align_val_t{Alignment});
        }
    }

    void reallocate(std::size_t new_capacity) {
        T* new_data = allocate_aligned(new_capacity);
        std::size_t i = 0;
        try {
            // Переміщення або копіювання елементів у новий буфер
            for (; i < size_; ++i) {
                new (new_data + i) T(std::move_if_noexcept(data_[i]));
            }
        } catch (...) {
            // Знищення вже створених об'єктів у разі винятку
            for (std::size_t j = 0; j < i; ++j) {
                new_data[j].~T();
            }
            deallocate_aligned(new_data);
            throw;
        }

        // Знищення старих елементів і звільнення буфера
        for (std::size_t j = 0; j < size_; ++j) {
            data_[j].~T();
        }
        deallocate_aligned(data_);

        data_ = new_data;
        capacity_ = new_capacity;
    }

public:
    DynamicArray() = default;

    explicit DynamicArray(std::size_t initial_capacity) {
        reserve(initial_capacity);
    }

    ~DynamicArray() noexcept {
        clear();
        deallocate_aligned(data_);
    }

    // Заборона копіювання для простоти (можна реалізувати глибоке копіювання)
    DynamicArray(const DynamicArray&) = delete;
    DynamicArray& operator=(const DynamicArray&) = delete;

    // Підтримка Move-семантики (RAII)
    DynamicArray(DynamicArray&& other) noexcept
        : data_(other.data_), size_(other.size_), capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }

    DynamicArray& operator=(DynamicArray&& other) noexcept {
        if (this != &other) {
            clear();
            deallocate_aligned(data_);

            data_ = other.data_;
            size_ = other.size_;
            capacity_ = other.capacity_;

            other.data_ = nullptr;
            other.size_ = 0;
            other.capacity_ = 0;
        }
        return *this;
    }

    void reserve(std::size_t new_capacity) {
        if (new_capacity > capacity_) {
            reallocate(new_capacity);
        }
    }

    template <typename... Args>
    T& emplace_back(Args&&... args) {
        if (size_ >= capacity_) {
            std::size_t next_cap = (capacity_ == 0) ? 4 : capacity_ * 2;
            reserve(next_cap);
        }
        T* slot = data_ + size_;
        new (slot) T(std::forward<Args>(args)...);
        ++size_;
        return *slot;
    }

    void push_back(const T& value) {
        emplace_back(value);
    }

    void push_back(T&& value) {
        emplace_back(std::move(value));
    }

    void clear() noexcept {
        for (std::size_t i = 0; i < size_; ++i) {
            data_[i].~T();
        }
        size_ = 0;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }

    T& operator[](std::size_t index) noexcept { return data_[index]; }
    const T& operator[](std::size_t index) const noexcept { return data_[index]; }

    T& at(std::size_t index) {
        if (index >= size_) {
            throw std::out_of_range("Індекс вийшов за межі DynamicArray");
        }
        return data_[index];
    }

    // Підтримка ітераторів для range-based for
    T* begin() noexcept { return data_; }
    T* end() noexcept { return data_ + size_; }
    const T* begin() const noexcept { return data_; }
    const T* end() const noexcept { return data_ + size_; }
};

int main() {
    try {
        DynamicArray<int> arr;
        for (int i = 1; i <= 8; ++i) {
            arr.push_back(i * 100);
        }

        std::cout << "C++ DynamicArray (Розмір: " << arr.size() 
                  << ", Місткість: " << arr.capacity() << "):\n";

        for (int val : arr) {
            std::cout << val << " ";
        }
        std::cout << "\nДоступ через at(3): " << arr.at(3) << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
    }
    return 0;
}
```
:::

## Детальний аналіз реалізації та інженерні пастки

При створенні власних контейнерів динамічних масивів розробник зіштовхується з кількома фундаментальними проблемами системного програмування, які часто залишаються непоміченими при використанні високорівневих обгортків.

### 1. Вирівнювання пам'яті та специфіка функції `realloc`
У стандарту мови C функція `aligned_alloc(alignment, size)` вимагає, щоб розмір виділеного блоку `size` був строго кратним параметру вирівнювання `alignment`. Якщо спробувати передати некратний розмір, функція повертає нульовий вказівник. Крім того, стандартна функція `realloc()` у C **не гарантує** збереження апаратного вирівнювання, якщо початковий блок було виділено через `aligned_alloc()`. Реалокатор може перемістити дані за довільною адресою в купі, яка не вирівняна за межею 64 байтів. Це призводить до падіння продуктивності або навіть до апаратного збою (General Protection Fault) при виконанні SIMD-інструкцій векторизації (наприклад, `_mm256_load_si256`), які вимагають строго вирівняних адрес.

Тому в ідіоматичній реалізації мовою C для безпечної зміни розміру з вирівнюванням доводиться самостійно виділяти новий вирівняний блок через `aligned_alloc()`, копіювати вміст за допомогою `memcpy()`, після чого звільняти старий блок пам'яті.

### 2. Безпека винятків та Move-семантика у C++
У мові C++ виділення пам'яті для контейнера розділяється на два незалежних етапи:
- Виділення сирої невикристалізованої пам'яті без виклику конструкторів (використання `operator new[]`).
- Створення об'єктів у вже виділеній пам'яті за допомогою конструкцій Placement New (`new (slot) T(...)`).

При перерозподілі пам'яті під час виклику `reallocate()` існує ризик того, що конструктор переміщення або копіювання елемента `T` згенерує виняток (наприклад, при браку пам'яті всередині самого елемента). Якщо це станеться посередині циклу переносу елементів, частина об'єктів опиниться у новому буфері, частина — у старому, а програма втратить цілісність даних.

Щоб забезпечити **сильну гарантію безпеки винятків** (Strong Exception Guarantee), реалізація на C++ повинна використовувати обгортку `std::move_if_noexcept()`. Вона переміщує елементи лише тоді, коли їхній конструктор переміщення позначений як `noexcept`. Якщо ж переміщення може кинути виняток, контейнер безпечно відкочується до копіювання елементів. У разі збою реалізація перехоплює виняток у блоці `catch (...)`, викликає деструктори для вже створених нових об'єктів, звільняє новий буфер і прокидає виняток далі, зберігаючи початковий стан масиву недоторканим.

### 3. Оптимізація викликів деструкторів для Trivial-типів
Для багатьох бакалійних типів даних (тривіально копійовані типи, Trivially Copyable: `int`, `double`, прості структури) процес виклику деструктора в циклі є непотрібною витратою ресурсів. У промислових бібліотеках (наприклад, `std::vector` у libstdc++ чи libc++) перед використанням циклів перевіряють метку типізації через метапрограмування шаблонів:

```cpp
if constexpr (std::is_trivially_copyable_v<T>) {
    std::memcpy(new_data, data_, size_ * sizeof(T));
} else {
    // Цикл із Placement New та Move-семантикою
}
```

Використання `std::memcpy()` для тривіальних типів дозволяє процесору задіяти апаратні блоки векторного пересилки пам'яті (AVX/RAM DMA), що прискорює процес розширення масиву в десятки разів.

### 4. Інвалідація посилань та безпека ітераторів
Усі покажчики та посилання на елементи динамічного масиву залишаються дійсними лише до першої операції `reallocate()`. Як тільки контейнер виходить за межі початкової місткості (`capacity`), початковий блок пам'яті повертається аллокатору операційної системи. Будь-який збережений покажчик `T* p = &vec[0]` стає висячим покажчиком (Dangling Pointer). У мовах високого рівня (Rust, C++) для боротьби з цією проблемою застосовують аналізатори позичання (Borrow Checker) або рекомендують замість збереження посилань зберігати числові індекси усунення від початку масиву.

### 5. Стратегії протидії фрагментації оперативно пам'яті
При частих реалокаціях масивів великого розміру системний аллокатор пам'яті (ptmalloc у glibc, jemalloc чи tcmalloc) може зіштовхнутися з проблемами зовнішньої фрагментації. Виділення неперервних блоків розміром у сотні мегабайтів вимагає звернення до операційної системи через системний виклик `mmap()`, оминаючи стандартний ареальний хіп `brk()`. Використання методів попереднього резервування `reserve(N)` дозволяє звести кількість звернень до OS крантів до одиниці, уникаючи розщеплення віртуальних сторінок пам'яті.

### 6. Взаємодія з системною віртуальною пам’яттю та Huge Pages
У сучасних операційних системах (Linux, Windows) виділення великих масивів відображається на сторінки віртуальної пам'яті (Virtual Memory Pages, зазвичай 4 КБ). При створенні масиву розміром у гігабайти використання стандартних 4-кілобайтних сторінок призводить до великих накладних витрат у буфері швидкої адресації процесора (TLB, Translation Lookaside Buffer). Для прискорення доступу до великих масивів у системному програмуванні застосовують **Huge Pages** (великі сторінки розміром 2 МБ або 1 ГБ), викликаючи `madvise(MADV_HUGEPAGE)` у Linux. Це зменшує кількість промахів TLB і підвищує швидкість адресації масиву.
