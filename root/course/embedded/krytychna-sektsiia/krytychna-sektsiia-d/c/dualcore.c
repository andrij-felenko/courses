/*
 * Два ядра — дві незалежні маски переривань. CPSID i на ядрі M7 нічого не
 * забороняє ядру M4, тому спільну памʼять доводиться замикати ще й апаратним
 * спінлоком. Приклад для RP2040: два Cortex-M0+ і блок SIO.
 */
#include <stddef.h>

#include "critical_section.h"
#include "demos.h"

#define SIO_BASE 0xD0000000UL
/* Читання спінлока повертає ненуль, якщо лок дістався нам, і 0, якщо ним
 * володіє інше ядро. Запис будь-якого значення звільняє лок. */
#define SIO_SPINLOCK(n) (*(volatile uint32_t *)(SIO_BASE + 0x100UL + 4UL * (n)))

#define MAILBOX_SPINLOCK 0U
#define SPIN_LIMIT 10000U /* межа очікування: краще помилка, ніж вічний цикл */

typedef struct {
    uint32_t seq; /* лічильник публікацій — видно, чи оновлюється скринька */
    int32_t setpoint_ma;
    int32_t measured_ma;
} mailbox_t;

/* Лінкер кладе структуру в ділянку SRAM, видиму обом ядрам. */
static volatile mailbox_t g_mailbox;

/* Захоплення з обмеженням: якщо друге ядро тримає лок надто довго, це вже
 * несправність, і чекати на неї вічно — гірше, ніж повернути помилку. */
static int spinlock_try_acquire(void)
{
    for (uint32_t spins = 0U; spins < SPIN_LIMIT; spins++) {
        if (SIO_SPINLOCK(MAILBOX_SPINLOCK) != 0U) {
            __DMB(); /* усе, що нижче, не має випередити захоплення лока */
            return 1;
        }
    }
    return 0;
}

static void spinlock_release(void)
{
    __DMB();
    SIO_SPINLOCK(MAILBOX_SPINLOCK) = 1U;
}

int mailbox_publish(int32_t setpoint_ma, int32_t measured_ma)
{
    /* 1. Спершу локальні переривання цього ядра. Інакше ISR того самого ядра
     *    зайде сюди й чекатиме на лок, який тримає воно саме, — це глухий кут. */
    const irq_state_t saved = irq_lock();

    /* 2. Апаратний спінлок між ядрами. */
    if (!spinlock_try_acquire()) {
        irq_unlock(saved);
        return -1;
    }

    g_mailbox.seq++;
    g_mailbox.setpoint_ma = setpoint_ma;
    g_mailbox.measured_ma = measured_ma;

    spinlock_release(); /* 3. звільняємо лок */
    irq_unlock(saved);  /* 4. і лише потім переривання */
    return 0;
}

int mailbox_read(int32_t *setpoint_ma)
{
    if (setpoint_ma == NULL) {
        return -1;
    }

    const irq_state_t saved = irq_lock();

    if (!spinlock_try_acquire()) {
        irq_unlock(saved);
        return -1;
    }

    *setpoint_ma = g_mailbox.setpoint_ma;

    spinlock_release();
    irq_unlock(saved);
    return 0;
}
