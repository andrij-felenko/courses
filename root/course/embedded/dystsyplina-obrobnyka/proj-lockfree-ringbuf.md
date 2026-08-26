# ⚙️ Lock-Free кільцевий буфер для зв'язку ISR та основного потоку

Цей проект реалізує односпрямовану чергу без блокувань (Single-Producer Single-Consumer Lock-Free Ring Buffer), розроблену спеціально для безпечної передачі байтів або структурованих повідомлень від обробника переривання (ISR) до основного циклу програми чи фонового завдання операційної системи реального часу без вимкнення глобальних переривань, м'ютексів та динамічного виділення пам'яті.

## Задача: передача даних з переривання без очікування

Коли апаратний периферійний модуль (UART, SPI, ADC або CAN) генерує переривання на кожен отриманий байт або пакет, обробник переривання не має права зупинятися на очікування м'ютекса, блокувати виконання чи виділяти пам'ять через `malloc()`. Якщо головний потік затримається на обробці попередніх даних або утримуватиме замок, переривання не може чекати — воно мусить за лічені такти зберегти байт у пам'ять і повернути керування процесору.

Потрібна структура даних, яка задовольняє чотири жорсткі інженерні вимоги:
1. **Детермінований час запису `O(1)`**: запис одного елемента в ISR займає фіксовану кількість процесорних інструкцій без циклів очікування чи розгалужень із невідомим часом виконання.
2. **Повна відсутність блокувань (Lock-Free)**: жодна сторона не вимикає переривання ядра і не захоплює примітиви синхронізації (м'ютекси, спінлоки).
3. **Статичне розміщення в пам'яті**: буфер виділяється компілятором у секції BSS або на стеку на етапі компіляції без використання купи (англ. *heap*).
4. **Коректне впорядкування пам'яті (Memory Ordering)**: робота без збоїв на процесорних ядрах зі слабким порядком пам'яті (ARM Cortex-M, RISC-V, ESP32 Xtensa), де конвеєр або буфер шини може перевпорядковувати операції запису.

## Ідея: топологія SPSC з індексами степеня двійки

Класичний кільцевий буфер (англ. *circular buffer*) складається з масиву фіксованого розміру `Capacity` та двох індексів:
- `head` (голова): індекс комірки, куди записується наступний елемент. Змінюється **виключно постачальником** (у нашому випадку — обробником переривання ISR).
- `tail` (хвіст): індекс комірки, звідки вичитується наступний елемент. Змінюється **виключно споживачем** (головним циклом `main()` або RTOS-завданням).

Оскільки кожен індекс модифікується лише одним контекстом виконання, стан перегонів (англ. *race condition*) між записом у `head` та записом у `tail` фізично неможливий. Єдина точка перетину — це перевірка умов заповненості:
- Буфер порожній: `head == tail`.
- Буфер заповнений: `((head + 1) & MASK) == tail`.

Якщо розмір буфера обрати рівним степеню двійки (`Capacity = 2^K`, наприклад 64, 128, 256 байтів), операція взяття залишку від ділення `(index + 1) % Capacity` замінюється швидкою порозрядною операцією побітового «І» з маскою `MASK = Capacity - 1`: `(index + 1) & MASK`. На 32-бітних мікроконтролерах ARM Cortex-M це економить десятки тактів процесора, уникаючи важкої апаратної або бібліотечної інструкції ділення `UDIV`.

```
Індекси буфера (Capacity = 8, MASK = 0b0111 = 7):
  
  head = 0  → next_head = (0 + 1) & 7 = 1
  ...
  head = 7  → next_head = (7 + 1) & 7 = 0  (автоматичне закільцьовування без if/else)
```

Для запобігання перевпорядкуванню інструкцій компілятором і процесором використовуються бар'єри пам'яті (Data Memory Barrier, `__DMB()`) у мові C або семантика `acquire-release` стандарту C++11 / C11.

## Робочий код

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUFFER_SIZE 128
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1)

#if (RING_BUFFER_SIZE & RING_BUFFER_MASK) != 0
#error "RING_BUFFER_SIZE must be a power of two!"
#endif

typedef struct {
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} spsc_ring_buffer_t;

void ring_buffer_init(spsc_ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

/* Викликається з ISR: записує байт, повертає false якщо буфер переповнено */
bool ring_buffer_push_isr(spsc_ring_buffer_t *rb, uint8_t byte) {
    uint32_t current_head = rb->head;
    uint32_t current_tail = rb->tail;
    uint32_t next_head = (current_head + 1) & RING_BUFFER_MASK;

    if (next_head == current_tail) {
        /* Буфер повний: переповнення (overrun) */
        return false;
    }

    rb->buffer[current_head] = byte;

    /* Бар'єр пам'яті DMB: гарантує, що запис байта в масив завершено
       ДО того, як нове значення head стане видимим для інших потоків */
    __asm volatile ("dmb" ::: "memory");

    rb->head = next_head;
    return true;
}

/* Викликається з основного потоку: вичитує байт */
bool ring_buffer_pop_main(spsc_ring_buffer_t *rb, uint8_t *byte) {
    uint32_t current_tail = rb->tail;
    uint32_t current_head = rb->head;

    if (current_tail == current_head) {
        /* Буфер порожній */
        return false;
    }

    *byte = rb->buffer[current_tail];

    /* Бар'єр пам'яті: байт прочитано до оновлення tail */
    __asm volatile ("dmb" ::: "memory");

    rb->tail = (current_tail + 1) & RING_BUFFER_MASK;
    return true;
}

/* Кількість елементів, доступних для читання */
size_t ring_buffer_available(const spsc_ring_buffer_t *rb) {
    uint32_t head = rb->head;
    uint32_t tail = rb->tail;
    return (head - tail) & RING_BUFFER_MASK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <optional>
#include <span>
#include <concepts>

template <typename T, size_t Capacity>
requires ((Capacity & (Capacity - 1)) == 0 && Capacity > 1)
class SpscRingBuffer {
public:
    constexpr SpscRingBuffer() : head_(0), tail_(0) {}

    /* Викликається з ISR: запис елемента без блокування */
    bool push_from_isr(const T& item) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);
        const size_t next_head = (current_head + 1) & kMask;

        if (next_head == current_tail) {
            return false; // Буфер переповнено (Overrun)
        }

        buffer_[current_head] = item;

        // Release-бар'єр: гарантує, що запис buffer_[current_head] завершено
        // до оновлення head_, щоб читач не побачив сміття
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    /* Викликається з основного потоку: читання елемента */
    std::optional<T> pop_from_main() noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        // Acquire-бар'єр: гарантує актуальність даних у буфері, записаних в ISR
        const size_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return std::nullopt; // Буфер порожній
        }

        T item = buffer_[current_tail];
        tail_.store((current_tail + 1) & kMask, std::memory_order_release);
        return item;
    }

    [[nodiscard]] size_t size() const noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t tail = tail_.load(std::memory_order_relaxed);
        return (head - tail) & kMask;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] static constexpr size_t capacity() noexcept {
        return Capacity - 1; // 1 слот зарезервовано під умову заповненості
    }

private:
    static constexpr size_t kMask = Capacity - 1;
    
    // Вирівнювання за кеш-лінією для запобігання False Sharing на багатоядерних МК (ESP32/RP2040)
    alignas(64) std::array<T, Capacity> buffer_{};
    alignas(64) std::atomic<size_t> head_{0};
    alignas(64) std::atomic<size_t> tail_{0};
};
```
:::

## Покроковий механізм роботи пам'яті та бар'єрів

Розглянемо, що відбувається на рівні конвеєра процесора під час виклику `push_from_isr()`:

1. **Зчитування індексів**: ISR завантажує локальні копії `head` і `tail`. Оскільки `head` змінює лише сам обробник, його читання є абсолютно точним. Значення `tail` могло змінитися головним потоком (збільшитися), але найгірший наслідок цього — ISR вважатиме буфер трохи більш заповненим, ніж він є насправді, що абсолютно безпечно.
2. **Запис даних у масив**: Байт даних записується за адресою `&buffer[current_head]`. У цей момент нові дані лежать у пам'яті або в буфері запису шини.
3. **Виконання бар'єра пам'яті (`DMB` / `memory_order_release`)**: Інструкція `DMB` (Data Memory Barrier) наказує матриці шин мікроконтролера завершити всі попередні операції запису даних у пам'ять до того, як почнеться виконання наступної інструкції запису.
4. **Публікація нового індексу `head`**: Лише після фіксації даних оновлюється індекс `head`. Головний потік, перевіряючи умову `head != tail`, побачить оновлений індекс тільки тоді, коли дані в комірці гарантовано валідні.

На двоядерних мікроконтролерах (ESP32, Raspberry Pi Pico RP2040, STM32H7) або процесорах з кеш-пам'яттю L1 (Cortex-M7) атрибут `alignas(64)` для масиву та індексів розносить змінні `head` і `tail` у різні лінії кешу (англ. *Cache Line*). Це повністю ліквідує ефект хибного розділення пам'яті (англ. *False Sharing*), коли запис в один індекс змушує інше ядро інвалідувати всю свою кеш-лінію.

## Підводні камені та крайові випадки

1. **Обмеження моделі Single-Producer Single-Consumer (SPSC)**: Ця реалізація розрахована суворо на взаємодію між **одним постачальником** і **одним споживачем**. Якщо дані в один буфер намагатимуться одночасно записувати два різних переривання (наприклад, UART1 RX та UART2 RX), виникне стан перегонів за значення `head`. Для кількох переривань кожне джерело повинно мати свій власний окремий буфер.
2. **Втрата одного слота в буфері**: За класичного підходу з побітовою маскою буфер розміром `Capacity` здатний вмістити максимум `Capacity - 1` елементів, оскільки стан `head == tail` зарезервовано для порожнього буфера. Якщо дозволити заповнити всі `Capacity` слотів, умова `next_head == tail` зробить буфер невідрізним від порожнього.
3. **Бар'єри пам'яті на конвеєрних ядрах**: На ядрах архітектур ARMv7-M (Cortex-M3/M4/M7) і ARMv8-M процесор може виконувати спекулятивні звернення до пам'яті та кешувати запис у буфері шини. Без бар'єра `dmb` або семантики `std::memory_order_release` запис у змінну `head` може завершитися в оперативній пам'яті раніше, ніж завершиться запис самих даних у масив `buffer`. У результаті головний потік побачить новий індекс `head`, прочитає елемент, але отримає старе сміття з пам'яті.
4. **Обробка переповнення (Overrun)**: Якщо ISR повертає `false`, буфер вичерпано. Обробник повинен або зафіксувати апаратний лічильник втрачених пакетів (для діагностики), або скинути найстаріший байт (якщо в системі пріоритетом є найновіші дані). У жодному разі не можна блокувати ISR у циклі очікування звільнення місця.
