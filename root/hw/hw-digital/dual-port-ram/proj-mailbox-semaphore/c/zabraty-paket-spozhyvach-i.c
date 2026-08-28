// Забирає один пакет. Повертає довжину (>0), 0 якщо порожньо, -1 якщо не дали замка.
int mailbox_recv(mailbox_t volatile *mb, volatile uint8_t *sem,
                 uint8_t *out, uint8_t out_cap)
{
    if (!sem_lock_timeout(sem, 64))
        return -1;                      // замок у сусіда — спробуємо пізніше

    uint16_t t = mb->tail;
    if (t == mb->head) {                // порожньо
        sem_unlock(sem);
        return 0;
    }

    slot_t volatile *s = &mb->slot[t];
    uint8_t len = s->len;
    if (len > out_cap) len = out_cap;

    for (uint8_t i = 0; i < len; i++)   // СПЕРШУ дані зі слота
        out[i] = s->payload[i];

    mb->tail = (uint16_t)((t + 1u) & SLOT_MASK);  // ПОТІМ звільняємо слот

    sem_unlock(sem);
    return len;
}
