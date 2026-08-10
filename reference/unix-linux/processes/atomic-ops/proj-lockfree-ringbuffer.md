# ⚙️ Безблокувальний кільцевий буфер на atomic_t

Ця проектна стаття описує практичну реалізацію C-коду безблокувального кільцевого буфера (Lock-Free Single-Producer Single-Consumer Ring Buffer) з використанням атомарних примітивів ядра Linux `atomic_t` для високоефективної передачі даних між паралельними потоками без м'ютексів та блокувань.

У високопродуктивних підсистемах ядра Linux (таких як мережевий стек, драйвери дискового вводу-виводу, обробники апаратних переривань ISR та системи трасування ftrace/perf) використання класичних спінлоків або м'ютексів є неприпустимим через високі накладні витрати на синхронізацію та ризик виникнення мертвих блокувань (deadlocks) у контексті переривань. 

Для організації зв'язку між одним виробником даних (Producer) та одним споживачем (Consumer) застосовується алгоритм безблокувального кільцевого буфера на атомарних лічильниках читання та запису.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/atomic.h>

#define RING_BUFFER_SIZE 64 // Мусить бути обов'язково ступенем двійки

struct lockfree_ringbuffer {
    void *data[RING_BUFFER_SIZE];
    atomic_t head; // Індекс додавання нових елементів (Producer)
    atomic_t tail; // Індекс зчитування елементів (Consumer)
};

void ringbuffer_init(struct lockfree_ringbuffer *rb)
{
    atomic_set(&rb->head, 0);
    atomic_set(&rb->tail, 0);
}

bool ringbuffer_push(struct lockfree_ringbuffer *rb, void *item)
{
    int head = atomic_read(&rb->head);
    int tail = atomic_read(&rb->tail);

    // Перевірка на переповнення кольцевого буфера
    if ((head - tail) >= RING_BUFFER_SIZE) {
        return false; // Буфер повністю заповнений
    }

    // Запис елемента за масковим індексом (замість % використовуємо бітове AND)
    rb->data[head & (RING_BUFFER_SIZE - 1)] = item;

    // Атомарно просуваємо head вперед для виділення слота
    atomic_inc(&rb->head);
    return true;
}

void *ringbuffer_pop(struct lockfree_ringbuffer *rb)
{
    int tail = atomic_read(&rb->tail);
    int head = atomic_read(&rb->head);

    // Перевірка на порожнечу кольцевого буфера
    if (tail == head) {
        return NULL; // В буфері немає даних
    }

    void *item = rb->data[tail & (RING_BUFFER_SIZE - 1)];

    // Атомарно просуваємо tail вперед після зчитування
    atomic_inc(&rb->tail);
    return item;
}
```

## Ключові пастки та апаратні оптимізації

1. **Розмір як ступінь двійки:** Завдяки вибору розміру буфера як `2^N` (наприклад, 64), замість дорогої операції ділення з остачею `%` (яка вимагає 20-40 тактів CPU) взяття маскового індексу виконується за 1 процесорний такт через бітову операцію `head & (RING_BUFFER_SIZE - 1)`.
2. **Абсолютна відсутність блокувань:** Producer оновлює тільки атомарне значення `head`, а Consumer — тільки `tail`. Обидва атомарні лічильники гарантують відсутність race condition без використання будь-яких примітивів взаємного виключення.
3. **Обробка оверфлоу:** Використання значень `atomic_t` гарантує коректне обгортання лічильників при досягненні `INT_MAX` завдяки математиці за модулем $2^{32}$.
