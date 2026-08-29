#include "estop_channels.h"
#include "safety_hal.h"

#define DEBOUNCE_MS       8U     /* брязкіт срібних контактів — одиниці мілісекунд */
#define PULSE_PERIOD_MS   20U    /* T_test: 10–50 мс */
#define PULSE_WIDTH_US    300U   /* t_pulse: 100–500 мкс, котушка не встигає відпустити */
#define PULSE_GAP_US      200U   /* фази T1 і T2 не перекриваються НІКОЛИ */
#define DISCREPANCY_MS    100U   /* t_disc: 50–200 мс */

void estop_channels_init(estop_channels_t *c)
{
    for (uint8_t ch = 0; ch < 2; ch++) {
        c->input[ch].stable    = false;
        c->input[ch].candidate = false;
        c->input[ch].settle_ms = 0;
    }
    c->pulse_timer_ms = 0;
    c->mismatch_ms    = 0;
    c->mismatching    = false;
    c->fault          = CH_FAULT_NONE;

    hal_set_test_output(HAL_CH_A, true);
    hal_set_test_output(HAL_CH_B, true);
}

/* Фільтр брязкоту: рівень переходить у стабільний лише після того, як
   протримався незмінним DEBOUNCE_MS. Вікно навмисно набагато вужче за
   t_disc, інакше фільтр сам створював би розбіжність каналів. */
static void debounce(debounced_input_t *d, bool raw, uint32_t dt_ms)
{
    if (raw != d->candidate) {
        d->candidate = raw;
        d->settle_ms = 0;
        return;
    }
    if (d->stable == raw) {
        d->settle_ms = 0;
        return;
    }
    d->settle_ms += dt_ms;
    if (d->settle_ms >= DEBOUNCE_MS) {
        d->stable    = raw;
        d->settle_ms = 0;
    }
}

/* Динамічний імпульсний тест зі зсувом фаз.
   Спершу знімаємо опорні рівні: діагностувати можна лише ЗАМКНЕНИЙ канал.
   На розімкненому вході й так нуль, і провал тестового виходу туди не
   доходить — без цієї перевірки натиснутий грибок читався б як міжканальне
   замикання. */
static void run_pulse_test(estop_channels_t *c)
{
    const bool idle_a = hal_read_estop_input(HAL_CH_A);
    const bool idle_b = hal_read_estop_input(HAL_CH_B);

    /* Фаза 1: провал на T1, T2 тримає високий рівень. */
    hal_set_test_output(HAL_CH_A, false);
    hal_busy_wait_us(PULSE_WIDTH_US);
    const bool a_at_t1 = hal_read_estop_input(HAL_CH_A);
    const bool b_at_t1 = hal_read_estop_input(HAL_CH_B);
    hal_set_test_output(HAL_CH_A, true);

    hal_busy_wait_us(PULSE_GAP_US);

    /* Фаза 2: провал на T2. */
    hal_set_test_output(HAL_CH_B, false);
    hal_busy_wait_us(PULSE_WIDTH_US);
    const bool a_at_t2 = hal_read_estop_input(HAL_CH_A);
    const bool b_at_t2 = hal_read_estop_input(HAL_CH_B);
    hal_set_test_output(HAL_CH_B, true);

    hal_busy_wait_us(PULSE_GAP_US);   /* лінії встигають відновитися до опитування */

    /* Замкнений канал, що впав під ЧУЖИЙ імпульс, зрощений із сусіднім.
       Судимо це першим: міжканальне замикання підживлює вхід і виглядає
       ще й як замикання на живлення. */
    if ((idle_a && !a_at_t2) || (idle_b && !b_at_t1)) {
        c->fault = CH_FAULT_CROSS_CIRCUIT;
        return;
    }

    /* Замкнений канал, що НЕ впав під власний імпульс, живиться збоку. */
    if ((idle_a && a_at_t1) || (idle_b && b_at_t2)) {
        c->fault = CH_FAULT_SHORT_TO_SUPPLY;
        return;
    }
}

bool estop_channels_update(estop_channels_t *c, uint32_t dt_ms)
{
    if (c->fault != CH_FAULT_NONE) {
        return false;   /* дефект лінії залипає до обслуговування */
    }

    c->pulse_timer_ms += dt_ms;
    if (c->pulse_timer_ms >= PULSE_PERIOD_MS) {
        c->pulse_timer_ms = 0;
        run_pulse_test(c);
        if (c->fault != CH_FAULT_NONE) {
            return false;
        }
    }

    debounce(&c->input[HAL_CH_A], hal_read_estop_input(HAL_CH_A), dt_ms);
    debounce(&c->input[HAL_CH_B], hal_read_estop_input(HAL_CH_B), dt_ms);

    if (c->input[HAL_CH_A].stable != c->input[HAL_CH_B].stable) {
        if (!c->mismatching) {
            c->mismatching = true;
            c->mismatch_ms = 0;
        } else {
            c->mismatch_ms += dt_ms;
            if (c->mismatch_ms >= DISCREPANCY_MS) {
                c->fault = CH_FAULT_DISCORDANCE;
            }
        }
        return false;   /* безпека не чекає: розбіжність уже знімає дозвіл */
    }

    c->mismatching = false;
    c->mismatch_ms = 0;
    return c->input[HAL_CH_A].stable && c->input[HAL_CH_B].stable;
}

channel_fault_t estop_channels_fault(const estop_channels_t *c)
{
    return c->fault;
}
