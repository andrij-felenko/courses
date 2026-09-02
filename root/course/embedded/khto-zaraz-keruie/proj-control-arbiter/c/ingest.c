#include "ingest.h"

/* Скільки разів переспробувати копію, перервану перериванням. Три — з великим
   запасом: щоб зірвати спробу, кадр має прийти між двома читаннями лічильника. */
#define TAKE_RETRIES 3

void sp_mailbox_init(sp_mailbox_t *mb)
{
    int i, a;

    for (i = 0; i < 2; ++i) {
        mb->slot[i].stamp_us = 0;
        for (a = 0; a < AX_COUNT; ++a)
            mb->slot[i].ch[a] = 0.0f;
    }
    atomic_init(&mb->seq, 0u);
    atomic_init(&mb->front, 0u);
    mb->seen    = 0;
    mb->dropped = 0;
    mb->torn    = 0;
}

void sp_mailbox_publish(sp_mailbox_t *mb, const setpoint_t *sp)
{
    uint_fast32_t front = atomic_load_explicit(&mb->front, memory_order_relaxed);
    uint_fast32_t back  = front ^ 1u;

    /* Тіньовий слот споживачеві не видно — пишемо звичайним присвоєнням. */
    mb->slot[back] = *sp;

    /* release: усе, що записано вище, стане видно тому, хто прочитає front
       з acquire. Порядок саме такий — спершу індекс, потім лічильник, щоб
       споживач ніколи не побачив «новий кадр є» раніше за сам кадр. */
    atomic_store_explicit(&mb->front, back, memory_order_release);
    atomic_fetch_add_explicit(&mb->seq, 1u, memory_order_release);
}

bool sp_mailbox_take(sp_mailbox_t *mb, setpoint_t *out)
{
    int attempt;

    for (attempt = 0; attempt < TAKE_RETRIES; ++attempt) {
        uint_fast32_t before = atomic_load_explicit(&mb->seq, memory_order_acquire);
        uint_fast32_t front;
        uint_fast32_t after;

        if ((uint32_t)before == mb->seen)
            return false;   /* нового кадру немає — джерело мовчить цей такт */

        front = atomic_load_explicit(&mb->front, memory_order_acquire);
        *out  = mb->slot[front];

        /* Двох слотів мало, якщо переривання встигне опублікувати ДВІЧІ поки
           ми копіюємо: другий кадр ляже саме в той слот, який ми читаємо.
           Ловимо це лічильником публікацій — він росте з кожним кадром. */
        after = atomic_load_explicit(&mb->seq, memory_order_acquire);
        if (after != before) {
            mb->torn++;
            continue;
        }

        mb->dropped += (uint32_t)before - mb->seen - 1u;  /* скільки цикл проспав */
        mb->seen = (uint32_t)before;
        return true;
    }

    /* Джерело сипле швидше, ніж цикл читає: кадр візьмемо наступного такту.
       Серце джерела при цьому не б'ється — і сторож це побачить. */
    return false;
}

uint32_t sp_mailbox_dropped(const sp_mailbox_t *mb)
{
    return mb->dropped;
}

uint32_t sp_mailbox_torn(const sp_mailbox_t *mb)
{
    return mb->torn;
}
