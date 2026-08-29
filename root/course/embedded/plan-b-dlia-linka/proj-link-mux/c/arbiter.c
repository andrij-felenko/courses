#include "arbiter.h"

#include <string.h>

static void apply_mode(bearer_t *b, bearer_mode_t mode) {
    if (b->mode == mode) {
        return;
    }
    b->mode = mode;
    if (b->drv.set_mode != NULL) {
        b->drv.set_mode(mode, b->drv.ctx);
    }
}

static void enter_state(link_arbiter_t *a, arbiter_state_t next, uint32_t now_ms) {
    if (a->state == next) {
        return;
    }
    a->state          = next;
    a->state_since_ms = now_ms;
    a->switches++;

    bearer_t *prim = &a->bearers[BEARER_PRIMARY];
    bearer_t *fall = &a->bearers[BEARER_FALLBACK];

    switch (next) {
    case ARB_PRIMARY_OK:
        a->active = BEARER_PRIMARY;
        apply_mode(prim, BEARER_MODE_ACTIVE);
        apply_mode(fall, BEARER_MODE_LISTEN);   /* резерв слухає, але не гріє підсилювач */
        link_stats_resume(&fall->stats, now_ms);
        break;

    case ARB_FALLBACK_ACTIVE:
        a->active = BEARER_FALLBACK;
        apply_mode(fall, BEARER_MODE_ACTIVE);
        /* Заглушений основний тримати в ефірі — це 3..8 Вт батареї в нікуди.
           Замість цього черговий прийом: 10 мс слухаємо раз на 500 мс. */
        apply_mode(prim, BEARER_MODE_SLEEP);
        a->sniff_next_ms = now_ms + SNIFF_PERIOD_MS;
        a->sniff_open    = false;
        /* На 10..50 кбіт/с відео не пролізе — черга йде геть одразу, а не
           лежить, збільшуючи затримку всьому іншому. */
        tx_queue_flush(&a->tx[PRIO_VIDEO]);
        break;

    case ARB_RECOVERY_EVAL:
        /* Основний слухаємо безперервно й міряємо з чистого аркуша: старе вікно
           повне нулів завади й ніколи б не опустилося під поріг повернення. */
        apply_mode(prim, BEARER_MODE_LISTEN);
        a->sniff_open = true;
        link_stats_reset(&prim->stats, now_ms);
        break;

    case ARB_BLACKOUT:
        apply_mode(prim, BEARER_MODE_LISTEN);
        apply_mode(fall, BEARER_MODE_LISTEN);
        a->sniff_open = true;
        link_stats_resume(&prim->stats, now_ms);
        break;
    }
}

static void sniff_tick(link_arbiter_t *a, uint32_t now_ms) {
    bearer_t *prim = &a->bearers[BEARER_PRIMARY];

    if (!a->sniff_open) {
        if ((int32_t)(now_ms - a->sniff_next_ms) >= 0) {
            a->sniff_open = true;
            link_stats_resume(&prim->stats, now_ms);
            apply_mode(prim, BEARER_MODE_LISTEN);
        }
    } else if ((int32_t)(now_ms - (a->sniff_next_ms + SNIFF_ON_MS)) >= 0) {
        a->sniff_open     = false;
        a->sniff_next_ms += SNIFF_PERIOD_MS;
        apply_mode(prim, BEARER_MODE_SLEEP);
    }
}

static void duplicate_critical(link_arbiter_t *a, const packet_t *pkt, uint32_t now_ms) {
    const bearer_id_t other = (a->active == BEARER_PRIMARY) ? BEARER_FALLBACK : BEARER_PRIMARY;
    bearer_t *b = &a->bearers[other];

    if (b->mode == BEARER_MODE_SLEEP) {
        return;   /* сплячий модуль не будимо заради копії */
    }
    if ((int32_t)(now_ms - b->next_free_ms) < 0) {
        return;   /* зайнятий передавач: копія не варта черги */
    }
    if (b->drv.raw_send(pkt, b->drv.ctx) < 0) {
        b->tx_errors++;
        return;
    }
    b->tx_frames++;
    b->next_free_ms = now_ms + b->drv.frame_air_ms;
}

void arbiter_init(link_arbiter_t *a, uint32_t now_ms) {
    memset(a, 0, sizeof(*a));
    a->state          = ARB_PRIMARY_OK;
    a->active         = BEARER_PRIMARY;
    a->state_since_ms = now_ms;

    tx_queue_init(&a->tx[PRIO_CRITICAL],  a->crit_slots, TX_SLOTS_CRITICAL,  TX_FULL_REJECT);
    tx_queue_init(&a->tx[PRIO_TELEMETRY], a->tlm_slots,  TX_SLOTS_TELEMETRY, TX_FULL_DROP_OLDEST);
    tx_queue_init(&a->tx[PRIO_VIDEO],     a->vid_slots,  TX_SLOTS_VIDEO,     TX_FULL_DROP_NEW);
}

void arbiter_bind(link_arbiter_t *a, bearer_id_t id, const bearer_driver_t *drv,
                  uint32_t now_ms) {
    if (id >= BEARER_COUNT || drv == NULL || drv->raw_send == NULL) {
        return;
    }
    bearer_t *b = &a->bearers[id];
    b->drv          = *drv;
    b->next_free_ms = now_ms;
    b->mode         = BEARER_MODE_SLEEP;   /* щоб перший перехід справді покликав драйвер */
    link_stats_init(&b->stats, drv->slot_ms, now_ms);
    apply_mode(b, (id == BEARER_PRIMARY) ? BEARER_MODE_ACTIVE : BEARER_MODE_LISTEN);
}

void arbiter_on_rx(link_arbiter_t *a, bearer_id_t id, uint16_t seq, int16_t rssi_dbm,
                   int8_t snr_db, uint32_t now_ms) {
    if (id >= BEARER_COUNT) {
        return;
    }
    bearer_t *b = &a->bearers[id];
    if (b->mode == BEARER_MODE_SLEEP) {
        return;   /* приймач спав — кадру бути не могло, це луна з кільця */
    }
    (void)link_stats_on_packet_rx(&b->stats, seq, rssi_dbm, snr_db, now_ms);
}

void arbiter_step(link_arbiter_t *a, uint32_t now_ms) {
    bearer_t *prim = &a->bearers[BEARER_PRIMARY];
    bearer_t *fall = &a->bearers[BEARER_FALLBACK];

    if (prim->mode != BEARER_MODE_SLEEP) {
        link_stats_on_tick(&prim->stats, now_ms);
    }
    if (fall->mode != BEARER_MODE_SLEEP) {
        link_stats_on_tick(&fall->stats, now_ms);
    }

    const bool prim_dead = (link_stats_silence_ms(&prim->stats, now_ms) > PRIMARY_SILENCE_MS)
                        || (prim->stats.per_percent >= FAILOVER_PER_PCT);
    const bool fall_dead = (link_stats_silence_ms(&fall->stats, now_ms) > FALLBACK_SILENCE_MS);

    switch (a->state) {
    case ARB_PRIMARY_OK:
        if (prim_dead) {
            enter_state(a, fall_dead ? ARB_BLACKOUT : ARB_FALLBACK_ACTIVE, now_ms);
        }
        break;

    case ARB_FALLBACK_ACTIVE:
        if (prim_dead && fall_dead) {
            enter_state(a, ARB_BLACKOUT, now_ms);
        } else if (link_stats_silence_ms(&prim->stats, now_ms) <= PRIMARY_SILENCE_MS) {
            /* Кадр, спійманий у вікні чергового прийому, — привід почати перевірку */
            enter_state(a, ARB_RECOVERY_EVAL, now_ms);
        } else {
            sniff_tick(a, now_ms);
        }
        break;

    case ARB_RECOVERY_EVAL:
        if (prim_dead) {
            /* Зрив під час перевірки: назад у резерв, витримка починається заново */
            enter_state(a, ARB_FALLBACK_ACTIVE, now_ms);
        } else if ((now_ms - a->state_since_ms) >= HYSTERESIS_DWELL_MS
                   && prim->stats.per_percent <= RECOVERY_PER_PCT) {
            enter_state(a, ARB_PRIMARY_OK, now_ms);
        }
        break;

    case ARB_BLACKOUT:
        if (!fall_dead) {
            enter_state(a, ARB_FALLBACK_ACTIVE, now_ms);
        } else if (!prim_dead) {
            enter_state(a, ARB_PRIMARY_OK, now_ms);
        }
        break;
    }
}

arb_status_t arbiter_send_packet(link_arbiter_t *a, packet_prio_t prio, const uint8_t *data,
                            uint16_t len, uint32_t now_ms) {
    if (len > QOS_MAX_PAYLOAD || data == NULL) {
        return ARB_ERR_TOO_LARGE;
    }
    if (a->state == ARB_BLACKOUT) {
        /* Ефіру немає взагалі. Тримати команди в черзі небезпечно: за секунди
           вони застаріють. Верхній рівень має вмикати автономне повернення. */
        return ARB_ERR_BLACKOUT;
    }
    if (prio == PRIO_VIDEO && a->active == BEARER_FALLBACK) {
        return ARB_ERR_NO_BANDWIDTH;   /* відкидаємо тут, а не в драйвері */
    }

    packet_t pkt;
    pkt.seq      = a->tx_seq++;
    pkt.len      = len;
    pkt.stamp_ms = now_ms;
    pkt.bearer   = (uint8_t)a->active;
    pkt.prio     = (uint8_t)prio;
    pkt.rssi_dbm = 0;
    pkt.snr_db   = 0;
    memcpy(pkt.payload, data, len);

    if (!tx_queue_push(&a->tx[prio], &pkt)) {
        return ARB_ERR_QUEUE_FULL;
    }
    return ARB_OK;
}

uint32_t arbiter_pump(link_arbiter_t *a, uint32_t now_ms) {
    if (a->state == ARB_BLACKOUT) {
        return 0u;   /* немає кому віддавати */
    }

    uint32_t sent = 0u;
    for (int p = 0; p < PRIO_COUNT; p++) {
        const packet_t *head = tx_queue_front(&a->tx[p]);
        while (head != NULL) {
            bearer_t *act = &a->bearers[a->active];
            if ((int32_t)(now_ms - act->next_free_ms) < 0) {
                return sent;   /* передавач ще в ефірі: черга чекає, ми не крутимось */
            }

            /* Копію беремо до pop: слот звільниться й може бути перезаписаний */
            const bool duplicate = (p == PRIO_CRITICAL && a->state == ARB_RECOVERY_EVAL);
            packet_t copy;
            if (duplicate) {
                copy = *head;
            }

            if (act->drv.raw_send(head, act->drv.ctx) < 0) {
                act->tx_errors++;
                return sent;   /* залізо захлинулось — спробуємо наступного разу */
            }
            act->tx_frames++;
            act->next_free_ms = now_ms + act->drv.frame_air_ms;
            tx_queue_pop_front(&a->tx[p]);
            sent++;

            /* Поки не впевнені в жодному носії, критичну команду шлемо обома */
            if (duplicate) {
                duplicate_critical(a, &copy, now_ms);
            }
            head = tx_queue_front(&a->tx[p]);
        }
    }
    return sent;
}

arbiter_state_t arbiter_state(const link_arbiter_t *a) {
    return a->state;
}

bearer_id_t arbiter_active(const link_arbiter_t *a) {
    return a->active;
}

const bearer_t *arbiter_bearer(const link_arbiter_t *a, bearer_id_t id) {
    return (id < BEARER_COUNT) ? &a->bearers[id] : NULL;
}

const tx_queue_t *arbiter_queue(const link_arbiter_t *a, packet_prio_t prio) {
    return (prio < PRIO_COUNT) ? &a->tx[prio] : NULL;
}

uint32_t arbiter_switches(const link_arbiter_t *a) {
    return a->switches;
}

const char *arbiter_state_name(arbiter_state_t st) {
    switch (st) {
    case ARB_PRIMARY_OK:      return "основний";
    case ARB_FALLBACK_ACTIVE: return "резерв";
    case ARB_RECOVERY_EVAL:   return "перевірка повернення";
    case ARB_BLACKOUT:        return "повний блекаут";
    default:                  return "?";
    }
}

const char *bearer_mode_name(bearer_mode_t mode) {
    switch (mode) {
    case BEARER_MODE_ACTIVE: return "передача+прийом";
    case BEARER_MODE_LISTEN: return "лише прийом";
    case BEARER_MODE_SLEEP:  return "сон";
    default:                 return "?";
    }
}
