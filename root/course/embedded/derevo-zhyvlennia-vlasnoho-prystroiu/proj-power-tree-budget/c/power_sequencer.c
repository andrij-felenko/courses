#include "power_sequencer.h"

#include "board.h"

/* Знеструмлення завжди йде у зворотному до підняття порядку, і першою дією
 * ізолює сигнальні лінії: доки піни I2C активні, датчик без VCC живиться
 * витоком через підтяжки. */
static void rails_down(void)
{
    board_bus_pins_isolate();
    board_periph_switch_en(false);
    board_reset_assert(true);
    board_io_rail_en(false);
    board_core_rail_en(false);
}

static void enter_fault(power_sequencer_t *seq, pwr_error_t err)
{
    rails_down();
    seq->state = PWR_STATE_FAULT;
    seq->last_error = err;
    seq->state_timer_ms = 0;
    seq->fault_count++;
}

static void go(power_sequencer_t *seq, pwr_state_t next)
{
    seq->state = next;
    seq->state_timer_ms = 0;
}

void pwr_seq_init(power_sequencer_t *seq, const pwr_config_t *cfg)
{
    if (seq == NULL || cfg == NULL) {
        return;
    }
    seq->cfg = *cfg;
    seq->state = PWR_STATE_OFF;
    seq->last_error = PWR_ERR_NONE;
    seq->state_timer_ms = 0;
    seq->fault_count = 0;
    rails_down();
}

void pwr_seq_start(power_sequencer_t *seq)
{
    if (seq == NULL) {
        return;
    }
    /* Підняття з-під аварії дозволене, повторний старт у польоті — ні. */
    if (seq->state != PWR_STATE_OFF && seq->state != PWR_STATE_FAULT) {
        return;
    }

    rails_down();
    seq->last_error = PWR_ERR_NONE;

    /* Немає сенсу відкривати ключі, коли вхід уже поза робочим діапазоном:
     * Buck піде в режим прямої передачі й PGOOD не з'явиться взагалі. */
    if (board_vin_mv() < seq->cfg.vin_min_mv) {
        enter_fault(seq, PWR_ERR_VIN_LOW);
        return;
    }

    board_core_rail_en(true);
    go(seq, PWR_STATE_WAIT_CORE_PG);
}

void pwr_seq_shutdown(power_sequencer_t *seq)
{
    if (seq == NULL) {
        return;
    }
    rails_down();
    seq->state = PWR_STATE_OFF;
    seq->state_timer_ms = 0;
}

void pwr_seq_tick(power_sequencer_t *seq, uint32_t elapsed_ms)
{
    if (seq == NULL) {
        return;
    }
    if (seq->state == PWR_STATE_OFF || seq->state == PWR_STATE_FAULT) {
        return; /* аварія засувна: вихід лише через pwr_seq_start() */
    }

    /* Лічильник насичується, а не перевертається: переповнення на довгій
     * витримці мовчки скинуло б таймаут і автомат завис би назавжди. */
    if (seq->state_timer_ms > UINT32_MAX - elapsed_ms) {
        seq->state_timer_ms = UINT32_MAX;
    } else {
        seq->state_timer_ms += elapsed_ms;
    }

    /* Крок 5 послідовності: аварія й просідання входу мають пріоритет над
     * будь-яким кроком підняття. Перевіряємо їх до switch, а не в кожній гілці. */
    if (board_fault_irq()) {
        enter_fault(seq, PWR_ERR_OVERCURRENT);
        return;
    }
    if (board_vin_mv() < seq->cfg.vin_min_mv) {
        enter_fault(seq, PWR_ERR_BROWNOUT);
        return;
    }

    switch (seq->state) {
    case PWR_STATE_WAIT_CORE_PG:
        if (board_core_pgood()) {
            board_io_rail_en(true);
            go(seq, PWR_STATE_WAIT_IO_PG);
        } else if (seq->state_timer_ms >= seq->cfg.core_pg_timeout_ms) {
            enter_fault(seq, PWR_ERR_CORE_TIMEOUT);
        }
        break;

    case PWR_STATE_WAIT_IO_PG:
        if (board_io_pgood()) {
            go(seq, PWR_STATE_RELEASE_RESET);
        } else if (seq->state_timer_ms >= seq->cfg.io_pg_timeout_ms) {
            enter_fault(seq, PWR_ERR_IO_TIMEOUT);
        }
        break;

    case PWR_STATE_RELEASE_RESET:
        /* PGOOD спрацьовує на порозі ~90% номіналу; даємо рейці добрати
         * решту й лише тоді відпускаємо NRST. */
        if (seq->state_timer_ms >= seq->cfg.reset_release_ms) {
            board_reset_assert(false);
            /* Піни шини досі високоомні — саме тому ключ периферії можна
             * відкривати вже зараз, не боячись фантомного живлення. */
            board_periph_switch_en(true);
            go(seq, PWR_STATE_PERIPH_RAMP);
        }
        break;

    case PWR_STATE_PERIPH_RAMP:
        /* Поки ємність навантаження заряджається, вхід просідає; якщо
         * просідання перейшло межу, ми вже вилетіли у FAULT вище. */
        if (seq->state_timer_ms >= seq->cfg.periph_ramp_ms) {
            if (!board_core_pgood() || !board_io_pgood()) {
                enter_fault(seq, PWR_ERR_BROWNOUT);
                break;
            }
            board_bus_pins_activate();
            go(seq, PWR_STATE_READY);
        }
        break;

    case PWR_STATE_READY:
        if (!board_core_pgood() || !board_io_pgood()) {
            enter_fault(seq, PWR_ERR_BROWNOUT);
        }
        break;

    case PWR_STATE_OFF:
    case PWR_STATE_FAULT:
    default:
        break;
    }
}

bool pwr_seq_is_ready(const power_sequencer_t *seq)
{
    return seq != NULL && seq->state == PWR_STATE_READY;
}

const char *pwr_state_name(pwr_state_t state)
{
    switch (state) {
    case PWR_STATE_OFF:           return "OFF";
    case PWR_STATE_WAIT_CORE_PG:  return "WAIT_CORE_PG";
    case PWR_STATE_WAIT_IO_PG:    return "WAIT_IO_PG";
    case PWR_STATE_RELEASE_RESET: return "RELEASE_RESET";
    case PWR_STATE_PERIPH_RAMP:   return "PERIPH_RAMP";
    case PWR_STATE_READY:         return "READY";
    case PWR_STATE_FAULT:         return "FAULT";
    default:                      return "?";
    }
}

const char *pwr_error_name(pwr_error_t err)
{
    switch (err) {
    case PWR_ERR_NONE:         return "немає";
    case PWR_ERR_VIN_LOW:      return "вхід нижчий за робочий діапазон";
    case PWR_ERR_CORE_TIMEOUT: return "немає PGOOD первинного перетворювача";
    case PWR_ERR_IO_TIMEOUT:   return "немає PGOOD шини DVDD";
    case PWR_ERR_BROWNOUT:     return "просідання живлення";
    case PWR_ERR_OVERCURRENT:  return "аварія силового ключа";
    default:                   return "?";
    }
}
