# ⚙️ SPSC-кільцевий буфер: черга без блокувань і без CAS

Кільцевий буфер для одного виробника й одного споживача (англ. *Single-Producer Single-Consumer*, SPSC) — це спеціалізована високопродуктивна структура даних для потокового обміну повідомленнями між двома паралельними потоками.

Головною перевагою SPSC-буфера є надання найсильніших гарантій надійності — **Wait-Free `O(1)`**. Кожна операція додавання або вилучення гарантовано завершується за фіксовану, детерміновану кількість процесорних тактів без жодних циклів очікування, без повторних спроб, без динамічного виділення пам'яті на гарячому шляху та навіть без використання апаратної інструкції Compare-And-Swap (CAS).

### Чому в SPSC-архітектурі не потрібен CAS

У чергах загального призначення, розрахованих на довільну кількість потоків (наприклад, MPMC — Multi-Producer Multi-Consumer), кілька виробників одночасно намагаються збільшити спільний покажчик запису. Щоб вирішити цю гонку між кількома авторами, обов'язково потрібен апаратний арбітраж через CAS.

В архітектурі SPSC діє фундаментальне розділення обов'язків між ядрами, яке повністю усуває стан конкуренції між записами:
- **Індекс запису (`head`):** Модифікується **виключно одним потоком-виробником**. Споживач лише періодично зчитує його для перевірки наявності свіжих даних.
- **Індекс читання (`tail`):** Модифікується **виключно одним потоком-споживачем**. Виробник лише зчитує його для перевірки наявності вільного місця в буфері.

Оскільки кожна змінна має рівно одного автора, запис у неї ніколи не може зіткнутися з іншим паралельним записом. Для абсолютно надійної та цілісної синхронізації виявляється достатньо звичайних атомарних інструкцій завантаження (`load`) та збереження (`store`) з відповідними бар'єрами пам'яті (`acquire`/`release`).

```
               Кільцевий буфер фіксованого розміру 2ⁿ:
             
                 ┌───┬───┬───┬───┬───┬───┬───┬───┐
                 │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │
                 └───┴───┴───┴───┴───┴───┴───┴───┘
                           ▲               ▲
                           │               │
                      tail (споживач)   head (виробник)
```

### Покрокова механіка роботи буфера

1. **Операція додавання (Push виробником):**
   - Виробник завантажує власний індекс `head` з моделлю `memory_order_relaxed` (оскільки він сам єдиний володар цього індексу).
   - Виробник зчитує індекс `tail` споживача з моделлю `memory_order_acquire`.
   - Обчислюється кількість зайнятих слотів: `head - tail`. Якщо різниця дорівнює місткості буфера, буфер повністю заповнений, і функція повертає `false` без блокування.
   - Елемент записується у комірку за індексом `head & (Capacity - 1)`.
   - Виробник публікує новий індекс `head + 1` за допомогою `memory_order_release`. Цей бар'єр гарантує, що корисні дані у комірці стануть видимими для споживача раніше, ніж оновлений індекс.

2. **Операція вилучення (Pop споживачем):**
   - Споживач завантажує власний індекс `tail` з моделлю `memory_order_relaxed`.
   - Споживач зчитує індекс `head` виробника з моделлю `memory_order_acquire`.
   - Якщо `tail == head`, буфер порожній, і функція повертає `std::nullopt` або `false`.
   - Споживач вичитує елемент із комірки `tail & (Capacity - 1)`.
   - Споживач оновлює індекс `tail + 1` за допомогою `memory_order_release`, сигналізуючи виробнику про звільнення слота.

### Реалізація: C та C++

:::tabs
```c
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define BUFFER_CAPACITY 1024 // Місткість обов'язково є степенем двійки
#define BUFFER_MASK (BUFFER_CAPACITY - 1)

typedef struct {
    // Масив даних фіксованого розміру
    int buffer[BUFFER_CAPACITY];

    // Розділення кеш-ліній для унеможливлення False Sharing (64 байти)
    _Alignas(64) _Atomic(size_t) head; // Модифікує тільки Producer
    _Alignas(64) _Atomic(size_t) tail; // Модифікує тільки Consumer
} SpscRingBuffer;

void spsc_init(SpscRingBuffer* q) {
    atomic_init(&q->head, 0);
    atomic_init(&q->tail, 0);
}

bool spsc_push(SpscRingBuffer* q, int item) {
    const size_t current_head = atomic_load_explicit(&q->head, memory_order_relaxed);
    const size_t current_tail = atomic_load_explicit(&q->tail, memory_order_acquire);

    // Перевірка на переповнення буфера
    if ((current_head - current_tail) >= BUFFER_CAPACITY) {
        return false; // Буфер повністю заповнений
    }

    // Запис елемента у відкриту комірку
    q->buffer[current_head & BUFFER_MASK] = item;

    // Публікація нового head через release
    atomic_store_explicit(&q->head, current_head + 1, memory_order_release);
    return true;
}

bool spsc_pop(SpscRingBuffer* q, int* item) {
    const size_t current_tail = atomic_load_explicit(&q->tail, memory_order_relaxed);
    const size_t current_head = atomic_load_explicit(&q->head, memory_order_acquire);

    // Перевірка на наявність даних
    if (current_tail == current_head) {
        return false; // Буфер порожній
    }

    // Зчитування елемента з комірки
    *item = q->buffer[current_tail & BUFFER_MASK];

    // Публікація звільнення комірки через release
    atomic_store_explicit(&q->tail, current_tail + 1, memory_order_release);
    return true;
}
```
```cpp
#include <atomic>
#include <array>
#include <cstddef>
#include <new>
#include <optional>

template <typename T, std::size_t Capacity = 1024>
class SpscRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");
    static constexpr std::size_t Mask = Capacity - 1;
    static constexpr std::size_t CacheLineSize = 64;

public:
    SpscRingBuffer() : head_(0), tail_(0) {}

    // Заборона копіювання для збереження цілісності індексів
    SpscRingBuffer(const SpscRingBuffer&) = delete;
    SpscRingBuffer& operator=(const SpscRingBuffer&) = delete;

    bool push(T item) {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);
        const std::size_t current_tail = tail_.load(std::memory_order_acquire);

        if (current_head - current_tail >= Capacity) {
            return false; // Буфер переповнений
        }

        buffer_[current_head & Mask] = std::move(item);

        // memory_order_release гарантує, що запис у buffer_ зафіксується в пам'яті
        // раніше, ніж споживач побачить оновлений індекс head_
        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);
        const std::size_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return std::nullopt; // Буфер порожній
        }

        T item = std::move(buffer_[current_tail & Mask]);

        // memory_order_release повідомляє виробнику про звільнення комірки
        tail_.store(current_tail + 1, std::memory_order_release);
        return item;
    }

private:
    // Масив елементів
    std::array<T, Capacity> buffer_{};

    // Рознесення змінних на окремі кеш-лінії для запобігання False Sharing
    alignas(CacheLineSize) std::atomic<std::size_t> head_;
    alignas(CacheLineSize) std::atomic<std::size_t> tail_;
};
```
:::

### Архітектурні тонкощі та апаратні деталі

1. **Запобігання явищу False Sharing (Хибне спільне використання кеш-ліній):**
   У сучасних мікропроцесорах обмін даними між ядрами та кешем відбувається блоками по 64 байти (кеш-лініями). Якщо змінні `head` та `tail` розташувати в пам'яті поруч, вони неминуче опиняться в одній такій 64-байтній лінії.
   Щоразу, коли виробник записує нове значення `head`, протокол когерентності (MESI) змушений інвалідувати весь рядок кеша в L1-кеші ядра споживача. І навпаки: щойно споживач оновлює `tail`, лінія інвалідується на ядрі виробника. Виникає безперервний кеш-пінг-понг між ядрами, який у 5–10 разів знижує реальну пропускну здатність.
   Вирівнювання `alignas(64)` або `_Alignas(64)` змушує компілятор розмістити `head` та `tail` у строго незалежних лініях кеша, повністю усуваючи взаємне витіснення.

2. **Оптимізація кешування індексів (Local Index Caching):**
   У базовій реалізації виробник перед кожним `push` звертається до атомарного `tail`, що належить споживачу. Це спричиняє читання чужої кеш-лінії. У високопродуктивних реалізаціях виробник зберігає локальну неатомарну копію `cached_tail`. Поки різниця `head - cached_tail < Capacity`, виробник взагалі не чіпає пам'ять споживача, здійснюючи читання справжнього `tail` лише тоді, коли локальний запас вільних слотів вичерпано. Аналогічну оптимізацію з `cached_head` застосовує споживач. Це зменшує між'ядерний трафік когерентності в десятки разів.

3. **Модульна арифметика без скидання до нуля:**
   Індекси `head` і `tail` монотонно збільшуються і ніколи не повертаються до нуля спеціальними умовними переходами. Завдяки правилам беззнакового переповнення типу `size_t` у стандарті C/C++, вираз `current_head - current_tail` математично точно повертає поточну заповненість буфера навіть у мить, коли лічильник переходить через межу `SIZE_MAX`. Розрахунок фізичного індексу через побітову маску `index & (Capacity - 1)` виконується процесором за 1 машинний такт.

4. **Порівняння продуктивності з блокуючими чергами:**
   У традиційних чергах на базі `std::mutex` або системних примітивів (наприклад, POSIX `pthread_mutex`) затримка передачі одного повідомлення за умови конкуренції коливається від 1500 до 5000 наносекунд. Це зумовлено необхідністю системних викликів ядра (`sys_futex`) та перемикання контексту операційної системи.
   На противагу цьому, SPSC-кільцевий буфер передає елемент за 5–15 наносекунд (затримка прямої між'ядерної передачі кеш-лінії через L3-кеш процесора).

5. **Сфера застосування SPSC у промислових системах:**
   SPSC-буфери є стандартом де-факто для передачі аудіопотоків між ядром звукової карти та користувацьким застосунком у реальному часі (де затримка понад 1 мілісекунду неприпустима), а також для зв'язку між обробниками апаратних переривань мережевих карт (ISR/DMA) та робочими потоками мережевого стека.
