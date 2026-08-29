#include "deadman.h"
#include "safety_hal.h"

#define SPLIT_MAX_MS         100U     /* розбіжність контактів дозволу */
#define VIGILANCE_CYCLE_MS   45000U   /* T_cycle: 30–60 с спокою */
#define VIGILANCE_WARN_MS    2500U    /* T_warn: світлова фаза */
#define VIGILANCE_ALARM_MS   2500U    /* T_alarm: звукова фаза */

void deadman_init(deadman_t *d)
{
    d->grip           = GRIP_RELEASED;
    d->panic_latch    = false;
    d->contacts_split = false;
    d->split_ms       = 0;
    d->idle_ms        = 0;
    d->ack_prev       = false;
    d->lamp           = false;
    d->buzzer         = false;
}

/* Позиція за трьома контактами. NC паніки розмикається першим і має
   найвищий пріоритет: продавлена кнопка — це завжди Позиція 3. */
static grip_t raw_position(bool a, bool b, bool panic_nc, bool *split)
{
    *split = (a != b);
    if (!panic_nc) {
        return GRIP_PANIC;
    }
    if (*split) {
        return GRIP_FAULT;   /* попереднє значення, поки не збіг таймер */
    }
    return (a && b) ? GRIP_ENABLED : GRIP_RELEASED;
}

/* Ескалація: спокій → лампа → зумер → зняття дозволу.
   Скидає таймер тільки ФРОНТ кнопки підтвердження або справжня дія
   оператора: затиснута стяжкою кнопка тримає постійний рівень і доказом
   присутності не є. */
static void update_vigilance(deadman_t *d, uint32_t dt_ms)
{
    const bool ack      = hal_read_ack_button();
    const bool ack_edge = ack && !d->ack_prev;
    d->ack_prev = ack;

    if (d->grip != GRIP_ENABLED && d->grip != GRIP_DOZED) {
        d->idle_ms = 0;
        d->lamp    = false;
        d->buzzer  = false;
        return;
    }

    if (d->grip == GRIP_DOZED) {
        /* Спрацювала — тримаємо доти, доки кнопку не повернуть у Позицію 1.
           Інакше сонний оператор поновив би рух самим лише підтвердженням. */
        d->lamp   = true;
        d->buzzer = true;
        return;
    }

    if (ack_edge || hal_operator_active()) {
        d->idle_ms = 0;
    } else {
        d->idle_ms += dt_ms;
    }

    d->lamp   = (d->idle_ms >= VIGILANCE_CYCLE_MS);
    d->buzzer = (d->idle_ms >= VIGILANCE_CYCLE_MS + VIGILANCE_WARN_MS);
    if (d->idle_ms >= VIGILANCE_CYCLE_MS + VIGILANCE_WARN_MS + VIGILANCE_ALARM_MS) {
        d->grip = GRIP_DOZED;
    }
}

void deadman_update(deadman_t *d, uint32_t dt_ms)
{
    if (d->grip == GRIP_FAULT) {
        d->lamp   = false;
        d->buzzer = false;
        return;   /* залипла апаратна помилка — лише обслуговування */
    }

    bool a = false, b = false, panic_nc = false;
    hal_read_enabling_contacts(&a, &b, &panic_nc);

    bool split = false;
    const grip_t raw = raw_position(a, b, panic_nc, &split);

    /* Паніка старша за розбіжність: продавлена кнопка розмикає NO-кола не
       синхронно, і чекати на збіг каналів тут не можна. */
    if (raw == GRIP_PANIC) {
        split = false;
        d->contacts_split = false;
        d->split_ms       = 0;
    }

    if (split) {
        d->contacts_split = true;
        d->split_ms += dt_ms;
        if (d->split_ms >= SPLIT_MAX_MS) {
            d->grip = GRIP_FAULT;
            d->lamp = d->buzzer = false;
            return;
        }
    } else {
        d->contacts_split = false;
        d->split_ms       = 0;

        switch (raw) {
        case GRIP_PANIC:
            /* Панічне стискання зводить блокування. */
            d->panic_latch = true;
            d->grip        = GRIP_PANIC;
            break;

        case GRIP_RELEASED:
            /* Лише повне повернення в Позицію 1 знімає блокування —
               і паніки, і пропущеної пильності. */
            d->panic_latch = false;
            d->grip        = GRIP_RELEASED;
            break;

        case GRIP_ENABLED:
            if (d->panic_latch) {
                d->grip = GRIP_PANIC;   /* зворотний хід крізь Позицію 2 не вмикає */
            } else if (d->grip != GRIP_DOZED) {
                d->grip = GRIP_ENABLED;
            }
            break;

        default:
            break;
        }
    }

    update_vigilance(d, dt_ms);
}

bool deadman_ready(const deadman_t *d)
{
    return d->grip == GRIP_ENABLED && !d->contacts_split;
}

grip_t deadman_grip(const deadman_t *d)
{
    return d->grip;
}
