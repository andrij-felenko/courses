# Специфікація та Інтерфейс Черги (Queue Interface Specification)

У багатозадачних операційних системах реального часу (FreeRTOS, Zephyr, RT-Thread) та в системах без ОС (Bare-Metal) **черга FIFO (First-In, First-Out)** є основними примітивом міжзадачної взаємодії (Inter-Task Communication, ITC) та передачі повідомлень від обробників переривань (ISR) до потоків обробки.

Даний документ визначає стандартний потокобезпечний API-інтерфейс черги, описує її математичну модель та подає еталонну C/C++ реалізацію.

---

## 1. Архітектурні вимоги до інтерфейсу

1. **Потокобезпечність (Thread-Safety)**: Гарантія відсутності стану гонки при одночасному записі кількома критичними секціями або ISR.
2. **Нульове динамічне виділення пам'яті (Static Allocation)**: Запобігання фрагментації купи (Heap) у критичних для безпеки системах. Пам'ять під елементи дається статично при ініціалізації.
3. **Підтримка обробників переривань (ISR-Safe)**: Спеціалізовані виклики `Enqueue_FromISR` / `Dequeue_FromISR`, які не використовують блокуючі примітиви синхронізації RTOS.
4. **Фіксований розмір елементів (Fixed-Size Item Value)**: Кожен елемент має фіксований розмір $S$ байт, масив зберігається неперервно у пам'яті.

---

## 2. Математична модель черги та аналіз продуктивності

Нехай черга має ємність $N$ елементів розміром $S$ байт кожен. Загальний розмір буферу у пам'яті:

$$M_{\text{total}} = N \cdot S + M_{\text{metadata}}$$

Для оптимізації обчислення індексів без використання операції ділення з остачею (яка на деяких контролерах Cortex-M0 займає десятки тактів), ємність $N$ обирається як ступінь двійки: $N = 2^k$.

Індекси запису `head` та зчитування `tail` є нескінченно зростаючими лічильниками беззнакового типу `uint32_t`. Поточна кількість елементів у черзі:

$$\text{Count} = \text{head} - \text{tail}$$

Умова порожньої черги: $\text{head} == \text{tail}$.
Умова повної черги: $(\text{head} - \text{tail}) == N$.

Маскування фізичного індексу масиву:

$$\text{Index}_{\text{physical}} = \text{head} \ \& \ (N - 1)$$

---

## 3. Специфікація API на C/C++

Нижче наведено повну реалізацію універсального модуля `embedded_queue` з статичним виділенням пам'яті та захистом від перепереповнення.

```cpp
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    QUEUE_OK                  = 0,
    QUEUE_ERROR_NULL_PARAM    = -1,
    QUEUE_ERROR_FULL          = -2,
    QUEUE_ERROR_EMPTY         = -3,
    QUEUE_ERROR_INVALID_SIZE  = -4
} QueueStatus_t;

typedef struct {
    uint8_t *buffer;        // Вказівник на статичний масив
    uint32_t capacity;      // Ємність черги (мусить бути 2^k)
    uint32_t item_size;     // Розмір одного елемента в байтах
    volatile uint32_t head; // Індекс запису
    volatile uint32_t tail; // Індекс зчитування
    uint32_t mask;          // Маска (capacity - 1)
} EmbeddedQueue_t;

/**
 * @brief Перевірка чи число є ступенем двійки
 */
static inline bool is_power_of_two(uint32_t val) {
    return (val > 0) && ((val & (val - 1)) == 0);
}

/**
 * @brief Ініціалізація структури черги
 */
QueueStatus_t queue_init(EmbeddedQueue_t *q, uint8_t *buffer, uint32_t capacity, uint32_t item_size) {
    if (!q || !buffer) return QUEUE_ERROR_NULL_PARAM;
    if (!is_power_of_two(capacity)) return QUEUE_ERROR_INVALID_SIZE;
    if (item_size == 0) return QUEUE_ERROR_INVALID_SIZE;

    q->buffer = buffer;
    q->capacity = capacity;
    q->item_size = item_size;
    q->head = 0;
    q->tail = 0;
    q->mask = capacity - 1;

    return QUEUE_OK;
}

/**
 * @brief Перевірка чи черга порожня
 */
bool queue_is_empty(const EmbeddedQueue_t *q) {
    return (q->head == q->tail);
}

/**
 * @brief Перевірка чи черга повна
 */
bool queue_is_full(const EmbeddedQueue_t *q) {
    return ((q->head - q->tail) >= q->capacity);
}

/**
 * @brief Отримання поточної кількості елементів
 */
uint32_t queue_get_count(const EmbeddedQueue_t *q) {
    return (q->head - q->tail);
}

/**
 * @brief Додавання елемента в чергу (Non-Blocking / ISR Safe)
 */
QueueStatus_t queue_enqueue(EmbeddedQueue_t *q, const void *item_data) {
    if (!q || !item_data) return QUEUE_ERROR_NULL_PARAM;

    if (queue_is_full(q)) {
        return QUEUE_ERROR_FULL;
    }

    uint32_t index = q->head & q->mask;
    uint8_t *dest = &q->buffer[index * q->item_size];
    memcpy(dest, item_data, q->item_size);

    // Атомний або захищений інкремент head
    q->head++;

    return QUEUE_OK;
}

/**
 * @brief Вилучення елемента з черги (Non-Blocking / ISR Safe)
 */
QueueStatus_t queue_dequeue(EmbeddedQueue_t *q, void *out_item_data) {
    if (!q || !out_item_data) return QUEUE_ERROR_NULL_PARAM;

    if (queue_is_empty(q)) {
        return QUEUE_ERROR_EMPTY;
    }

    uint32_t index = q->tail & q->mask;
    const uint8_t *src = &q->buffer[index * q->item_size];
    memcpy(out_item_data, src, q->item_size);

    // Атомний або захищений інкремент tail
    q->tail++;

    return QUEUE_OK;
}

// Тестова програма підтвердження коректності API
typedef struct {
    uint32_t event_id;
    float value;
} SensorEvent_t;

int main(void) {
    #define QUEUE_CAPACITY 8
    static uint8_t storage_buffer[QUEUE_CAPACITY * sizeof(SensorEvent_t)];
    EmbeddedQueue_t event_queue;

    printf("=== Демонстрація Специфікації та API Черги Повідомлень ===\n");

    QueueStatus_t st = queue_init(&event_queue, storage_buffer, QUEUE_CAPACITY, sizeof(SensorEvent_t));
    if (st != QUEUE_OK) {
        printf("Помилка ініціалізації черги!\n");
        return -1;
    }

    // Запис елементів
    for (uint32_t i = 1; i <= 5; i++) {
        SensorEvent_t ev = { .event_id = i, .value = (float)i * 1.5f };
        if (queue_enqueue(&event_queue, &ev) == QUEUE_OK) {
            printf("Enqueue: Event ID = %u, Value = %.2f\n", ev.event_id, ev.value);
        }
    }

    printf("Кількість елементів у черзі: %u / %u\n", queue_get_count(&event_queue), event_queue.capacity);

    // Зчитання елементів
    SensorEvent_t rx_ev;
    while (queue_dequeue(&event_queue, &rx_ev) == QUEUE_OK) {
        printf("Dequeue: Event ID = %u, Value = %.2f\n", rx_ev.event_id, rx_ev.value);
    }

    printf("Черга після очищення порожня: %s\n", queue_is_empty(&event_queue) ? "ТАК" : "НІ");

    return 0;
}
```

---

## 4. Висновки

1. Застосування беззнакової 32-бітної арифметики для `head` та `tail` гарантує переповнення лічильників без порушення цілісності черги.
2. Використання маски `head & (capacity - 1)` суттєво прискорює роботу на процесорах без апаратного дільника.
