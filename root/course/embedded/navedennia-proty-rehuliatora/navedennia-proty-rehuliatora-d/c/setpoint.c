#include "setpoint.h"

#include <stdatomic.h>
#include <string.h>

void sp_mailbox_init(SetpointMailbox *mb)
{
    memset(&mb->data, 0, sizeof(mb->data));
    mb->data.q_target = quat_identity();
    atomic_store_explicit(&mb->seq, 0u, memory_order_relaxed);
}

void sp_publish(SetpointMailbox *mb, const Setpoint *sp)
{
    const uint32_t s = atomic_load_explicit(&mb->seq, memory_order_relaxed);

    /* Непарне значення — попередження читачеві: дані зараз рвані. */
    atomic_store_explicit(&mb->seq, s + 1u, memory_order_relaxed);
    atomic_thread_fence(memory_order_release);

    mb->data = *sp;

    atomic_thread_fence(memory_order_release);
    atomic_store_explicit(&mb->seq, s + 2u, memory_order_relaxed);
}

bool sp_consume(SetpointMailbox *mb, Setpoint *out)
{
    for (int attempt = 0; attempt < SP_READ_ATTEMPTS; ++attempt) {
        const uint32_t s0 = atomic_load_explicit(&mb->seq, memory_order_acquire);

        if (s0 == 0u || (s0 & 1u) != 0u) {
            continue;                 /* даних ще не було / письменник усередині */
        }

        *out = mb->data;

        atomic_thread_fence(memory_order_acquire);
        if (atomic_load_explicit(&mb->seq, memory_order_relaxed) == s0) {
            return true;              /* копія цілісна */
        }
        /* Письменник устиг втрутитися — пробуємо ще раз. Письменник ходить
           у 20 разів рідше за читача, тож більш ніж один повтор — екзотика. */
    }
    return false;
}

void fb_init(ControlFeedback *fb)
{
    atomic_store_explicit(&fb->bits, 0u, memory_order_relaxed);
}

void fb_set_bit(ControlFeedback *fb, uint32_t bit, bool on)
{
    if (on) {
        atomic_fetch_or_explicit(&fb->bits, bit, memory_order_relaxed);
    } else {
        atomic_fetch_and_explicit(&fb->bits, ~bit, memory_order_relaxed);
    }
}

bool fb_test(ControlFeedback *fb, uint32_t bit)
{
    return (atomic_load_explicit(&fb->bits, memory_order_relaxed) & bit) != 0u;
}
