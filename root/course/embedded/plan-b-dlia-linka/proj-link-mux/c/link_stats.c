#include "link_stats.h"

#include <string.h>

#define EWMA_SHIFT 3   /* alpha = 1/8: помітно згладжує, але не запізнюється на секунди */

static void push_bit(link_stats_t *s, bool received) {
    s->rx_packet_mask = (s->rx_packet_mask << 1) | (received ? 1u : 0u);
    if (received) {
        s->rx_total++;
    } else {
        s->lost_total++;
    }
}

static void recompute(link_stats_t *s) {
    uint32_t mask = s->rx_packet_mask;
    uint8_t  received = 0;
    for (uint8_t i = 0; i < STATS_WINDOW; i++) {
        received += (uint8_t)(mask & 1u);
        mask >>= 1;
    }
    s->per_percent = (uint8_t)(((STATS_WINDOW - received) * 100u) / STATS_WINDOW);

    /* Бал якості: втрати важать найбільше, рівень і шум лише додають штраф */
    int32_t score = 100 - (int32_t)s->per_percent;
    const int16_t rssi = link_stats_rssi_dbm(s);
    if (rssi < -100) {
        score -= 20;            /* біля порога чутливості приймача */
    } else if (rssi < -90) {
        score -= 10;
    }
    if (link_stats_snr_db(s) < 0) {
        score -= 10;            /* сигнал під шумом — типовий почерк завади */
    }
    s->score = (uint8_t)(score < 0 ? 0 : (score > 100 ? 100 : score));
}

void link_stats_init(link_stats_t *s, uint16_t slot_ms, uint32_t now_ms) {
    memset(s, 0, sizeof(*s));
    s->slot_ms          = (slot_ms == 0u) ? 100u : slot_ms;
    s->rx_packet_mask      = 0xFFFFFFFFu;   /* до першої втрати вважаємо канал чистим */
    s->slot_deadline_ms = now_ms + s->slot_ms;
    s->last_rx_time       = now_ms;
    s->score            = 100;
}

uint16_t link_stats_on_packet_rx(link_stats_t *s, uint16_t seq, int16_t rssi_dbm,
                          int8_t snr_db, uint32_t now_ms) {
    uint16_t missed = 0;

    if (!s->have_seq) {
        s->have_seq = true;
        s->last_seq = seq;
    } else {
        /* Знакова різниця переживає обгортання uint16 без жодного «якщо» */
        const int16_t gap = (int16_t)(seq - s->last_seq);
        if (gap <= 0) {
            return 0;   /* спізнілий або дубльований кадр вікна втрат не рухає */
        }
        missed = (uint16_t)(gap - 1);
        for (uint16_t i = 0; i < missed && i < STATS_WINDOW; i++) {
            push_bit(s, false);
        }
        s->last_seq = seq;
    }
    push_bit(s, true);

    if (!s->seeded) {
        s->rssi_q8 = (int32_t)rssi_dbm << 8;
        s->snr_q8  = (int32_t)snr_db << 8;
        s->seeded  = true;
    } else {
        /* Класичний цілочисловий EWMA: x += (нове - x) / 8, зсув арифметичний */
        s->rssi_q8 += (((int32_t)rssi_dbm << 8) - s->rssi_q8) >> EWMA_SHIFT;
        s->snr_q8  += (((int32_t)snr_db  << 8) - s->snr_q8)  >> EWMA_SHIFT;
    }

    s->last_rx_time       = now_ms;
    s->slot_deadline_ms = now_ms + s->slot_ms;
    recompute(s);
    return missed;
}

void link_stats_on_tick(link_stats_t *s, uint32_t now_ms) {
    /* Тиша — теж вимір: за кожен прострочений слот у вікно падає нуль */
    while ((int32_t)(now_ms - s->slot_deadline_ms) >= 0) {
        push_bit(s, false);
        s->slot_deadline_ms += s->slot_ms;
        recompute(s);
    }
}

void link_stats_resume(link_stats_t *s, uint32_t now_ms) {
    /* Поки приймач спав, кадрів не було не через ефір, а через нас: у втрати
       цей час не пишемо, лише відсуваємо очікування наступного слота. */
    s->slot_deadline_ms = now_ms + s->slot_ms;
}

void link_stats_reset(link_stats_t *s, uint32_t now_ms) {
    s->rx_packet_mask      = 0xFFFFFFFFu;
    s->per_percent      = 0;
    s->slot_deadline_ms = now_ms + s->slot_ms;
    recompute(s);
}

int16_t link_stats_rssi_dbm(const link_stats_t *s) {
    return (int16_t)((s->rssi_q8 + 128) >> 8);
}

int8_t link_stats_snr_db(const link_stats_t *s) {
    return (int8_t)((s->snr_q8 + 128) >> 8);
}

uint32_t link_stats_silence_ms(const link_stats_t *s, uint32_t now_ms) {
    return now_ms - s->last_rx_time;
}

void dedup_init(dedup_window_t *d) {
    memset(d, 0, sizeof(*d));
}

bool dedup_accept(dedup_window_t *d, uint16_t seq) {
    if (!d->primed) {
        d->primed     = true;
        d->newest_seq = seq;
        d->seen_mask  = 1u;
        return true;
    }

    const int16_t diff = (int16_t)(seq - d->newest_seq);
    if (diff > 0) {
        if (diff >= (int16_t)STATS_WINDOW) {
            d->seen_mask = 0u;          /* стрибок далі за вікно — починаємо заново */
        } else {
            d->seen_mask <<= diff;
        }
        d->seen_mask |= 1u;
        d->newest_seq = seq;
        return true;
    }

    const uint16_t back = (uint16_t)(-diff);
    if (back >= STATS_WINDOW) {
        d->too_old++;                   /* відстав більше як на вікно — уже неактуальний */
        return false;
    }
    const uint32_t bit = 1u << back;
    if ((d->seen_mask & bit) != 0u) {
        d->duplicates++;                /* той самий кадр прийшов другим носієм */
        return false;
    }
    d->seen_mask |= bit;
    return true;                        /* спізнився, але новий — беремо */
}
