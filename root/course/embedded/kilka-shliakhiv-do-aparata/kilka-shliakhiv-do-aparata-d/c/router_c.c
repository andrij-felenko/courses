/* router_c.c — Інтелектуальний маршрутизатор MAVLink каналів мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_LINKS 3
#define DEDUP_WINDOW_SIZE 256
#define HOLD_OFF_TIME_MS 5000
#define DROP_THRESHOLD_LQ 30.0f
#define RECOVERY_THRESHOLD_LQ 75.0f

typedef enum {
    LINK_ROLE_PRIMARY_RF = 0,
    LINK_ROLE_BACKUP_LTE = 1,
    LINK_ROLE_SATCOM     = 2
} LinkRole;

typedef enum {
    LINK_STATE_ACTIVE,
    LINK_STATE_STANDBY,
    LINK_STATE_DEAD
} LinkState;

typedef struct {
    uint8_t sysid;
    uint8_t compid;
    uint8_t msgid;
    uint8_t seq;
    uint32_t timestamp_ms;
} DedupEntry;

typedef struct {
    DedupEntry entries[DEDUP_WINDOW_SIZE];
    size_t head;
} DedupFilter;

typedef struct {
    const char* name;
    LinkRole role;
    LinkState state;
    uint8_t last_seq;
    uint32_t last_packet_time_ms;
    uint32_t packets_received;
    uint32_t packets_lost;
    float lq_smooth;
    uint32_t rtt_ms;
} LinkMetrics;

typedef struct {
    LinkMetrics links[MAX_LINKS];
    size_t active_link_idx;
    uint32_t recovery_start_time_ms;
    bool in_recovery_hold;
    DedupFilter dedup;
} MultiLinkRouter;

void dedup_init(DedupFilter* df) {
    memset(df, 0, sizeof(DedupFilter));
}

bool dedup_is_duplicate(DedupFilter* df, uint8_t sysid, uint8_t compid, uint8_t msgid, uint8_t seq, uint32_t now_ms) {
    for (size_t i = 0; i < DEDUP_WINDOW_SIZE; ++i) {
        if (df->entries[i].timestamp_ms > 0 &&
            (now_ms - df->entries[i].timestamp_ms) < 2000 &&
            df->entries[i].sysid == sysid &&
            df->entries[i].compid == compid &&
            df->entries[i].msgid == msgid &&
            df->entries[i].seq == seq) {
            return true; /* Знайдено дублікат */
        }
    }
    /* Додаємо новий унікальний пакет у кільцевий буфер */
    df->entries[df->head].sysid = sysid;
    df->entries[df->head].compid = compid;
    df->entries[df->head].msgid = msgid;
    df->entries[df->head].seq = seq;
    df->entries[df->head].timestamp_ms = now_ms;
    df->head = (df->head + 1) % DEDUP_WINDOW_SIZE;
    return false;
}

void router_init(MultiLinkRouter* r) {
    memset(r, 0, sizeof(MultiLinkRouter));
    r->links[0].name = "Point-to-Point 915MHz RF";
    r->links[0].role = LINK_ROLE_PRIMARY_RF;
    r->links[0].lq_smooth = 100.0f;

    r->links[1].name = "Cellular 4G/5G LTE VPN";
    r->links[1].role = LINK_ROLE_BACKUP_LTE;
    r->links[1].lq_smooth = 100.0f;

    r->links[2].name = "Iridium Satcom SBD";
    r->links[2].role = LINK_ROLE_SATCOM;
    r->links[2].lq_smooth = 100.0f;

    r->active_link_idx = 0; /* Стартуємо з основного RF */
    dedup_init(&r->dedup);
}

void router_on_packet_received(MultiLinkRouter* r, size_t link_idx, uint8_t sysid, uint8_t compid,
                               uint8_t msgid, uint8_t seq, uint32_t now_ms) {
    if (link_idx >= MAX_LINKS) return;
    LinkMetrics* lm = &r->links[link_idx];

    /* Оновлення лічильника втрат за послідовністю seq */
    if (lm->packets_received > 0) {
        uint8_t expected_seq = (uint8_t)(lm->last_seq + 1);
        if (seq != expected_seq) {
            uint8_t lost = (uint8_t)(seq - expected_seq);
            lm->packets_lost += lost;
        }
    }
    lm->last_seq = seq;
    lm->last_packet_time_ms = now_ms;
    lm->packets_received++;

    /* Миттєвий та згладжений розрахунок Link Quality */
    uint32_t total = lm->packets_received + lm->packets_lost;
    float lq_inst = total > 0 ? ((float)lm->packets_received / (float)total) * 100.0f : 100.0f;
    lm->lq_smooth = 0.2f * lq_inst + 0.8f * lm->lq_smooth;

    /* Перевірка дедуплікації */
    if (dedup_is_duplicate(&r->dedup, sysid, compid, msgid, seq, now_ms)) {
        /* Дублікат: ігноруємо для вихідного сокета */
        return;
    }

    /* Якщо пакет прийшов з активного лінка — пропускаємо до споживача */
    if (link_idx == r->active_link_idx) {
        /* Передати в QGroundControl або польотний стек */
    }
}

void router_update_fsm(MultiLinkRouter* r, uint32_t now_ms) {
    LinkMetrics* primary = &r->links[0];
    LinkMetrics* backup  = &r->links[1];

    /* Перевірка таймауту тиші на каналах */
    for (size_t i = 0; i < MAX_LINKS; ++i) {
        if (now_ms - r->links[i].last_packet_time_ms > 1500) {
            r->links[i].state = LINK_STATE_DEAD;
        } else {
            r->links[i].state = (i == r->active_link_idx) ? LINK_STATE_ACTIVE : LINK_STATE_STANDBY;
        }
    }

    /* Логіка FSM з гістерезисом */
    if (r->active_link_idx == 0) {
        /* Основний канал деградував: LQ < 30% або таймаут */
        if (primary->lq_smooth < DROP_THRESHOLD_LQ || primary->state == LINK_STATE_DEAD) {
            if (backup->state != LINK_STATE_DEAD) {
                r->active_link_idx = 1; /* Перемикання на LTE */
                r->in_recovery_hold = false;
                printf("[FAILOVER] Перемикання на резервний 4G LTE (LQ RF: %.1f%%)\n", primary->lq_smooth);
            }
        }
    } else if (r->active_link_idx == 1) {
        /* Ми на резервному LTE. Перевіряємо відновлення основного RF */
        if (primary->state != LINK_STATE_DEAD && primary->lq_smooth >= RECOVERY_THRESHOLD_LQ) {
            if (!r->in_recovery_hold) {
                r->in_recovery_hold = true;
                r->recovery_start_time_ms = now_ms;
                printf("[RECOVERY] RF перевищив 75%%. Запуск hold-off таймера на 5 с...\n");
            } else if (now_ms - r->recovery_start_time_ms >= HOLD_OFF_TIME_MS) {
                /* Таймер стабілізації сплив успішно */
                r->active_link_idx = 0; /* Повернення на RF */
                r->in_recovery_hold = false;
                printf("[FAILBACK] Повернення на основний RF-канал (LQ RF: %.1f%%)\n", primary->lq_smooth);
            }
        } else {
            /* Зрив під час очікування таймера */
            r->in_recovery_hold = false;
        }
    }
}
