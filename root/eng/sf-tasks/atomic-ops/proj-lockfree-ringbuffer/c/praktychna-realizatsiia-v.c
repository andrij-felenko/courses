#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/atomic.h>

#define RING_SIZE 64 // Мусить бути ступенем двійки (2^N)
#define RING_MASK (RING_SIZE - 1)

struct kernel_spsc_ring {
    void *buffer[RING_SIZE];
    atomic_t head ____cacheline_aligned;
    atomic_t tail ____cacheline_aligned;
};

struct kernel_spsc_ring *ring_create(void)
{
    struct kernel_spsc_ring *rb = kmalloc(sizeof(*rb), GFP_KERNEL);
    if (!rb)
        return NULL;

    atomic_set(&rb->head, 0);
    atomic_set(&rb->tail, 0);
    return rb;
}

void ring_destroy(struct kernel_spsc_ring *rb)
{
    kfree(rb);
}

bool ring_push(struct kernel_spsc_ring *rb, void *item)
{
    // head правимо тільки ми — читаємо без бар'єра
    int head = atomic_read(&rb->head);
    // tail пише споживач на іншому ядрі — потрібен acquire
    int tail = atomic_read_acquire(&rb->tail);

    // Перевірка на заповненість буфера
    if ((head - tail) >= RING_SIZE)
        return false;

    // Запис даних у слот
    rb->buffer[head & RING_MASK] = item;

    // Забезпечуємо завершення запису даних до оновлення індексу head
    atomic_set_release(&rb->head, head + 1);
    return true;
}

void *ring_pop(struct kernel_spsc_ring *rb)
{
    int tail = atomic_read(&rb->tail);
    // Гарантуємо зчитування оновленого head після перевірки
    int head = atomic_read_acquire(&rb->head);

    // Перевірка на порожнечу буфера
    if (tail == head)
        return NULL;

    void *item = rb->buffer[tail & RING_MASK];

    // Оновлюємо tail із семантикою release
    atomic_set_release(&rb->tail, tail + 1);
    return item;
}
