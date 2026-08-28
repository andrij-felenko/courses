#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_IP_PACKET_SIZE 65535
#define MAX_IP_HEADER_SIZE 60
#define MAX_PAYLOAD_SIZE   (MAX_IP_PACKET_SIZE - 20)
#define REASSEMBLY_TIMEOUT_SEC 30

typedef struct {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t id;
    uint8_t  protocol;
} PacketKey;

typedef struct FragmentInterval {
    uint16_t start;
    uint16_t end;
    struct FragmentInterval *next;
} FragmentInterval;

typedef struct ReassemblyQueue {
    PacketKey key;
    uint8_t   buffer[MAX_PAYLOAD_SIZE];
    FragmentInterval *intervals;
    int32_t   expected_total_len; /* -1, поки не прийшов фрагмент з MF=0 */
    uint32_t  bytes_received;
    time_t    created_at;
    struct ReassemblyQueue *next;
} ReassemblyQueue;

typedef struct {
    ReassemblyQueue *head;
} Defragmenter;

Defragmenter* defrag_create(void) {
    Defragmenter *d = (Defragmenter*)malloc(sizeof(Defragmenter));
    if (d) d->head = NULL;
    return d;
}

static void free_intervals(FragmentInterval *inv) {
    while (inv) {
        FragmentInterval *tmp = inv->next;
        free(inv);
        inv = tmp;
    }
}

static void free_queue_entry(ReassemblyQueue *q) {
    if (!q) return;
    free_intervals(q->intervals);
    free(q);
}

void defrag_cleanup_expired(Defragmenter *d, time_t now) {
    ReassemblyQueue **curr = &d->head;
    while (*curr) {
        if (difftime(now, (*curr)->created_at) > REASSEMBLY_TIMEOUT_SEC) {
            ReassemblyQueue *to_free = *curr;
            *curr = (*curr)->next;
            free_queue_entry(to_free);
        } else {
            curr = &(*curr)->next;
        }
    }
}

static ReassemblyQueue* find_or_create_queue(Defragmenter *d, PacketKey key, time_t now) {
    for (ReassemblyQueue *q = d->head; q; q = q->next) {
        if (q->key.src_ip == key.src_ip && q->key.dst_ip == key.dst_ip &&
            q->key.id == key.id && q->key.protocol == key.protocol) {
            return q;
        }
    }
    ReassemblyQueue *q = (ReassemblyQueue*)calloc(1, sizeof(ReassemblyQueue));
    if (!q) return NULL;
    q->key = key;
    q->expected_total_len = -1;
    q->created_at = now;
    q->next = d->head;
    d->head = q;
    return q;
}

/* Перевірка відсутності шкідливого перекриття та реєстрація інтервалу */
static bool add_interval(ReassemblyQueue *q, uint16_t start, uint16_t end) {
    FragmentInterval *new_inv = (FragmentInterval*)malloc(sizeof(FragmentInterval));
    if (!new_inv) return false;
    new_inv->start = start;
    new_inv->end = end;
    new_inv->next = NULL;

    /* Вставляємо впорядковано за start */
    FragmentInterval **curr = &q->intervals;
    while (*curr && (*curr)->start < start) {
        curr = &(*curr)->next;
    }
    new_inv->next = *curr;
    *curr = new_inv;

    /* Об'єднуємо сусідні перекриття та перевіряємо безперервність */
    FragmentInterval *it = q->intervals;
    while (it && it->next) {
        if (it->end >= it->next->start) {
            if (it->next->end > it->end) it->end = it->next->end;
            FragmentInterval *dup = it->next;
            it->next = dup->next;
            free(dup);
        } else {
            it = it->next;
        }
    }
    return true;
}

/* Обробка отриманого фрагмента: 1 = дейтаграма повністю зібрана, 0 = очікуємо ще, -1 = помилка */
int defrag_process_fragment(Defragmenter *d, PacketKey key, uint16_t offset_8b,
                            bool more_fragments, const uint8_t *payload, uint16_t len,
                            uint8_t *out_buffer, uint16_t *out_len, time_t now) {
    if (!d || !payload || !out_buffer || !out_len) return -1;

    uint32_t byte_offset = (uint32_t)offset_8b * 8;
    uint32_t byte_end = byte_offset + len;

    /* Захист від Ping of Death: розмір не може перевищувати ліміт IPv4 */
    if (byte_end > MAX_PAYLOAD_SIZE) return -1;

    /* Захист від Teardrop / некоректних розмірів: проміжні фрагменти мусять бути кратні 8 */
    if (more_fragments && (len % 8 != 0)) return -1;

    ReassemblyQueue *q = find_or_create_queue(d, key, now);
    if (!q) return -1;

    /* Фіксація кінцевого розміру за останнім фрагментом (MF = 0) */
    if (!more_fragments) {
        if (q->expected_total_len != -1 && q->expected_total_len != (int32_t)byte_end) {
            return -1; /* Суперечливий фінальний фрагмент */
        }
        q->expected_total_len = (int32_t)byte_end;
    }

    /* Копіювання навантаження у буфер дейтаграми */
    memcpy(q->buffer + byte_offset, payload, len);
    if (!add_interval(q, (uint16_t)byte_offset, (uint16_t)byte_end)) return -1;

    /* Перевіряємо, чи зібрано весь діапазон [0, expected_total_len) */
    if (q->expected_total_len != -1 && q->intervals) {
        if (q->intervals->start == 0 && q->intervals->end == (uint16_t)q->expected_total_len) {
            memcpy(out_buffer, q->buffer, (size_t)q->expected_total_len);
            *out_len = (uint16_t)q->expected_total_len;

            /* Видаляємо завершену чергу */
            ReassemblyQueue **curr = &d->head;
            while (*curr && *curr != q) curr = &(*curr)->next;
            if (*curr) *curr = q->next;
            free_queue_entry(q);
            return 1;
        }
    }
    return 0;
}

void defrag_destroy(Defragmenter *d) {
    if (!d) return;
    ReassemblyQueue *q = d->head;
    while (q) {
        ReassemblyQueue *tmp = q->next;
        free_queue_entry(q);
        q = tmp;
    }
    free(d);
}
