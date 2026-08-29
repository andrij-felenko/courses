/* rs485.c — автомат напівдуплексної шини.
 * Усі функції rs485_isr_* викликаються з переривань і мусять бути короткими:
 * жодних циклів очікування, жодного розбору протоколу — тільки стан і буфер.
 */
#include "rs485.h"

#include <string.h>

/* Modbus RTU: понад 19200 біт/с стандарт фіксує абсолютні значення пауз,
 * нижче — рахуємо від тривалості символу в 11 біт. */
static void compute_timing(rs485_port_t *p, uint32_t baud)
{
    if (baud > 19200u) {
        p->t15_us = 750u;
        p->t35_us = 1750u;
    } else {
        const uint32_t char_us = (11u * 1000000u + baud - 1u) / baud;
        p->t15_us = (char_us * 3u) / 2u;
        p->t35_us = (char_us * 7u) / 2u;
    }
}

static void arm_timer(rs485_port_t *p, rs485_timer_job_t job, uint32_t us)
{
    p->timer_job = job;
    p->hw.timer_arm_us(us);
}

static void drive_enable(rs485_port_t *p, bool on)
{
    if (p->hw.set_de != NULL) {
        p->hw.set_de(on);
    }
    /* Інакше вивід DE веде сам UART — процесору тут робити нічого. */
}

/* Аварійне припинення передачі: DMA стоп, DE вниз, далі — захисна пауза. */
static void abort_tx(rs485_port_t *p, rs485_err_t err)
{
    p->hw.tx_dma_abort();
    p->hw.tc_irq_enable(false);
    drive_enable(p, false);

    p->echo_wait = false;
    p->last_error = err;
    p->state = RS485_GUARD;
    arm_timer(p, RS485_T_GUARD, p->t35_us);
}

void rs485_init(rs485_port_t *p, const rs485_hw_t *hw, uint32_t baud)
{
    memset(p, 0, sizeof(*p));
    p->hw = *hw;
    compute_timing(p, baud);

    p->state = RS485_IDLE;
    p->timer_job = RS485_T_NONE;
    p->last_error = RS485_OK;

    p->hw.timer_stop();
    p->hw.tc_irq_enable(false);
    drive_enable(p, false);   /* стан спокою — приймання */
}

rs485_err_t rs485_send(rs485_port_t *p, const uint8_t *data, size_t len)
{
    if (len == 0u || len > RS485_BUF_SIZE) {
        return RS485_ERR_TOO_LONG;
    }

    const uint32_t saved = p->hw.irq_lock();
    if (p->state != RS485_IDLE) {
        /* RX, TX або ще не витримана пауза розвороту — лізти в лінію не можна */
        p->hw.irq_unlock(saved);
        return RS485_ERR_BUSY;
    }

    memcpy(p->tx_buf, data, len);
    p->tx_len = len;
    p->echo_idx = 0u;
    p->echo_wait = true;
    p->state = RS485_TX;

    p->hw.timer_stop();
    p->timer_job = RS485_T_NONE;

    /* 1. Передавач у лінію. 2. DMA у TDR. DE до кінця кадру не чіпаємо. */
    drive_enable(p, true);
    p->hw.tx_dma_start(p->tx_buf, len);

    p->hw.irq_unlock(saved);
    return RS485_OK;
}

bool rs485_frame_ready(const rs485_port_t *p)
{
    return p->frame_ready;
}

const uint8_t *rs485_frame(const rs485_port_t *p, size_t *len)
{
    if (!p->frame_ready) {
        *len = 0u;
        return NULL;
    }
    *len = p->rx_len;
    return p->rx_buf;
}

/* Поки кадр не звільнено, приймач нові байти губить (rx_discard) —
 * саме тому застосунок може розбирати буфер із увімкненими перериваннями. */
void rs485_frame_release(rs485_port_t *p)
{
    const uint32_t saved = p->hw.irq_lock();
    p->frame_ready = false;
    if (p->state != RS485_RX) {
        p->rx_len = 0u;
    }
    p->hw.irq_unlock(saved);
}

rs485_err_t rs485_take_error(rs485_port_t *p)
{
    const uint32_t saved = p->hw.irq_lock();
    const rs485_err_t err = p->last_error;
    p->last_error = RS485_OK;
    p->hw.irq_unlock(saved);
    return err;
}

const rs485_stats_t *rs485_stats(const rs485_port_t *p)
{
    return &p->stats;
}

/* Кадр скінчено: тиша тривала повні T3.5 */
static void finish_frame(rs485_port_t *p)
{
    p->timer_job = RS485_T_NONE;
    p->state = RS485_IDLE;

    if (p->rx_len == 0u && !p->rx_discard) {
        return;
    }
    if (p->rx_discard) {
        p->stats.overruns++;
        p->last_error = RS485_ERR_OVERRUN;
        p->rx_discard = false;
        return;
    }
    if (p->frame_bad) {
        p->frame_bad = false;
        p->rx_len = 0u;
        return;
    }
    p->frame_ready = true;
    p->stats.frames++;
}

/* Звіряння відлуння: /RE притягнуто до землі, тож кожен власний байт
 * повертається на RX. Розбіжність — це або колізія, або несправність лінії. */
static bool consume_echo(rs485_port_t *p, uint8_t byte)
{
    if (!p->echo_wait) {
        return false;
    }
    if (p->echo_idx >= p->tx_len || byte != p->tx_buf[p->echo_idx]) {
        p->stats.collisions++;
        if (p->state == RS485_TX || p->state == RS485_TX_DRAIN) {
            abort_tx(p, RS485_ERR_COLLISION);
        } else {
            p->echo_wait = false;
            p->last_error = RS485_ERR_COLLISION;
        }
        return true;
    }

    p->echo_idx++;
    if (p->echo_idx == p->tx_len) {
        p->echo_wait = false;   /* уся передача підтверджена лінією */
    }
    return true;
}

void rs485_isr_rx(rs485_port_t *p, uint8_t byte)
{
    /* Спершу власне відлуння — воно приходить і в GUARD, бо останній байт
     * добігає на вхід приблизно тоді ж, коли спрацьовує TC. */
    if (p->state == RS485_TX || p->state == RS485_TX_DRAIN || p->state == RS485_GUARD) {
        if (consume_echo(p, byte)) {
            return;
        }
        if (p->state != RS485_GUARD) {
            return;   /* чужий байт посеред нашої передачі вже опрацьовано вище */
        }
        /* GUARD і відлуння вичерпано: ведений почав відповідати — приймаємо */
    }

    if (p->state != RS485_RX) {
        p->rx_len = 0u;
        p->frame_bad = false;
        p->rx_discard = p->frame_ready;   /* попередній кадр ще в роботі */
        p->state = RS485_RX;
    } else if (p->timer_job == RS485_T_T35) {
        /* Байт прийшов після T1.5 — за Modbus такий кадр недійсний */
        p->frame_bad = true;
        p->stats.gaps++;
        p->last_error = RS485_ERR_GAP;
    }

    if (p->rx_discard) {
        /* буфер зайнятий застосунком */
    } else if (p->rx_len < RS485_BUF_SIZE) {
        p->rx_buf[p->rx_len++] = byte;
    } else {
        p->frame_bad = true;
        p->stats.overruns++;
        p->last_error = RS485_ERR_OVERRUN;
    }

    arm_timer(p, RS485_T_T15, p->t15_us);   /* watchdog кадру — з кожним байтом наново */
}

void rs485_isr_rx_error(rs485_port_t *p, uint32_t flags)
{
    if ((flags & RS485_RX_OVERRUN) != 0u) {
        p->stats.overruns++;
        p->last_error = RS485_ERR_OVERRUN;
    }
    if ((flags & RS485_RX_FRAMING) != 0u) {
        p->stats.framings++;
        p->last_error = RS485_ERR_FRAMING;
    }
    if ((flags & RS485_RX_NOISE) != 0u) {
        p->stats.noises++;
        p->last_error = RS485_ERR_NOISE;
    }

    p->hw.rx_error_clear();

    if (p->state == RS485_TX || p->state == RS485_TX_DRAIN) {
        /* Зіпсований стоп-біт під час власної передачі — це колізія на шині */
        p->stats.collisions++;
        abort_tx(p, RS485_ERR_COLLISION);
        return;
    }

    if (p->state == RS485_RX) {
        p->frame_bad = true;
        arm_timer(p, RS485_T_T15, p->t15_us);
    }
}

/* DMA доклав останній байт у TDR — у лінії він ще навіть не почався.
 * DE не чіпаємо, лише вмикаємо переривання TC. */
void rs485_isr_dma_done(rs485_port_t *p)
{
    if (p->state != RS485_TX) {
        return;
    }
    p->state = RS485_TX_DRAIN;
    p->hw.tc_irq_enable(true);
}

/* TC: стоп-біт фізично вийшов у дріт — тільки тепер DE вниз. */
void rs485_isr_uart_tc(rs485_port_t *p)
{
    p->hw.tc_irq_enable(false);
    if (p->state != RS485_TX_DRAIN) {
        return;
    }

    drive_enable(p, false);
    p->state = RS485_GUARD;
    arm_timer(p, RS485_T_GUARD, p->t35_us);   /* час розвороту шини */
}

void rs485_isr_timer(rs485_port_t *p)
{
    switch (p->timer_job) {
    case RS485_T_T15:
        if (p->state == RS485_RX) {
            /* Міжсимвольний інтервал вичерпано — чекаємо решту тиші до T3.5 */
            arm_timer(p, RS485_T_T35, p->t35_us - p->t15_us);
        } else {
            p->timer_job = RS485_T_NONE;
        }
        break;

    case RS485_T_T35:
        finish_frame(p);
        break;

    case RS485_T_GUARD:
        if (p->echo_wait) {
            /* Байти пішли, а лінія їх не повернула: обрив, КЗ або мертвий трансивер */
            p->echo_wait = false;
            p->stats.no_echo++;
            p->last_error = RS485_ERR_NO_ECHO;
        }
        p->timer_job = RS485_T_NONE;
        p->state = RS485_IDLE;
        break;

    case RS485_T_NONE:
    default:
        break;
    }
}
