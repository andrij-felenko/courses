#include "fsm_table.h"

#include <stddef.h>

#define ENTRY_DELAY_MS 20000u
#define SIREN_TIMEOUT_MS 180000u

typedef void (*sec_action_fn)(sec_fsm_t *fsm);

/*
 * Клітинка матриці. Прапорець valid обов'язковий: без нього неможливо
 * відрізнити «переходу немає» від «перехід у стан із кодом 0 без дії» — саме
 * на цьому підмінюванні нуля порожнечею й ловляться реалізації цього патерну.
 */
typedef struct {
    sec_state_t   next;
    sec_action_fn action;
    bool          valid;
} sec_transition_t;

static void act_arm(sec_fsm_t *fsm)
{
    fsm->timer_ms = 0u;
}

static void act_start_entry_delay(sec_fsm_t *fsm)
{
    fsm->timer_ms = ENTRY_DELAY_MS;
}

static void act_sound_siren(sec_fsm_t *fsm)
{
    fsm->siren_active = true;
    fsm->timer_ms     = SIREN_TIMEOUT_MS;
    if (fsm->alarm_count != UINT16_MAX) {
        ++fsm->alarm_count;
    }
}

static void act_silence(sec_fsm_t *fsm)
{
    fsm->siren_active = false;
    fsm->timer_ms     = 0u;
}

/*
 * Увесь граф автомата — тут і більше ніде. Рядок — стан, стовпчик — сигнал.
 * Позначені ініціалізатори тримають таблицю читабельною й, головне, не дають
 * їй розповзтися, коли до переліків додається новий стан або сигнал.
 */
static const sec_transition_t k_table[SEC_ST_COUNT][SEC_SIG_COUNT] = {
    [SEC_ST_IDLE] = {
        [SEC_SIG_CODE] = { SEC_ST_ARMED, act_arm, true },
    },
    [SEC_ST_ARMED] = {
        [SEC_SIG_PIR]  = { SEC_ST_ENTRY_DELAY, act_start_entry_delay, true },
        [SEC_SIG_CODE] = { SEC_ST_IDLE, act_silence, true },
    },
    [SEC_ST_ENTRY_DELAY] = {
        [SEC_SIG_CODE]    = { SEC_ST_IDLE, act_silence, true },
        [SEC_SIG_TIMEOUT] = { SEC_ST_TRIGGERED, act_sound_siren, true },
    },
    [SEC_ST_TRIGGERED] = {
        [SEC_SIG_CODE]    = { SEC_ST_IDLE, act_silence, true },
        /* Сирена не виє вічно: за три хвилини вертаємося під охорону. */
        [SEC_SIG_TIMEOUT] = { SEC_ST_ARMED, act_silence, true },
    },
};

void sec_fsm_init(sec_fsm_t *fsm)
{
    fsm->state        = SEC_ST_IDLE;
    fsm->siren_active = false;
    fsm->alarm_count  = 0u;
    fsm->timer_ms     = 0u;
}

/* Увесь диспетчер: жодної логіки, лише пошук клітинки й порядок дій. */
void sec_fsm_dispatch(sec_fsm_t *fsm, sec_signal_t sig)
{
    if ((unsigned)fsm->state >= (unsigned)SEC_ST_COUNT ||
        (unsigned)sig >= (unsigned)SEC_SIG_COUNT) {
        return;
    }

    const sec_transition_t *t = &k_table[fsm->state][sig];
    if (!t->valid) {
        return; /* стан свідомо ігнорує цей сигнал */
    }

    if (t->action != NULL) {
        t->action(fsm);
    }
    fsm->state = t->next;
}

void sec_fsm_tick(sec_fsm_t *fsm, uint32_t elapsed_ms)
{
    if (fsm->timer_ms == 0u) {
        return;
    }

    if (fsm->timer_ms <= elapsed_ms) {
        fsm->timer_ms = 0u;
        sec_fsm_dispatch(fsm, SEC_SIG_TIMEOUT);
    } else {
        fsm->timer_ms -= elapsed_ms;
    }
}

/*
 * Перевірка графа обходом у ширину: з кожного стану мусить існувати шлях у
 * SEC_ST_IDLE. Матриця — звичайні дані, тому таку перевірку можна прогнати
 * і в модульному тесті, і одноразово на старті прошивки.
 */
bool sec_fsm_graph_is_sane(void)
{
    for (unsigned start = 0; start < (unsigned)SEC_ST_COUNT; ++start) {
        bool     seen[SEC_ST_COUNT] = { false };
        unsigned queue[SEC_ST_COUNT];
        unsigned head = 0u, tail = 0u;
        bool     reached_idle = false;

        seen[start]   = true;
        queue[tail++] = start;

        while (head < tail) {
            const unsigned s = queue[head++];
            if (s == (unsigned)SEC_ST_IDLE) {
                reached_idle = true;
                break;
            }
            for (unsigned sig = 0; sig < (unsigned)SEC_SIG_COUNT; ++sig) {
                const sec_transition_t *t = &k_table[s][sig];
                if (t->valid && !seen[t->next]) {
                    seen[t->next] = true;
                    queue[tail++] = (unsigned)t->next;
                }
            }
        }

        if (!reached_idle) {
            return false; /* глухий кут: стан, з якого нема виходу */
        }
    }
    return true;
}

const char *sec_state_name(sec_state_t s)
{
    switch (s) {
        case SEC_ST_IDLE:        return "IDLE";
        case SEC_ST_ARMED:       return "ARMED";
        case SEC_ST_ENTRY_DELAY: return "ENTRY_DELAY";
        case SEC_ST_TRIGGERED:   return "TRIGGERED";
        default:                 return "?";
    }
}
