#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SECTOR     4096u                 // розмір сектора Flash (типово 4 КБ)
#define N_SECTORS  16u                   // скільки секторів під лог
#define EMPTY_SEQ  0xFFFFFFFFu           // стерте слово = вільний сектор

typedef struct {                         // один запис = один сектор
    uint32_t seq;                        // наскрізний номер (лише росте)
    uint32_t crc;                        // мітка цілості над payload
    uint8_t  payload[SECTOR - 8];        // власне подія
} log_rec_t;

static uint32_t head;                    // індекс сектора-голови
static uint32_t next_seq;                // номер для наступного запису

// --- апаратні примітиви Flash (надає драйвер платформи) ---
extern void flash_read (uint32_t sector, void *dst);
extern void flash_erase(uint32_t sector);            // → усі біти в 0xFF
extern void flash_write(uint32_t sector, const void *src);
extern uint32_t crc32(const void *data, uint32_t len);

// Дописати подію. O(1): майже завжди це лише запис у голову.
void log_append(const void *event, uint32_t len) {
    if (len > sizeof(((log_rec_t *)0)->payload)) return;   // не влазить

    uint32_t ahead = (head + 1u) % N_SECTORS;    // сектор попереду голови
    flash_erase(ahead);                          // стираємо наперед — губимо найдавніше

    log_rec_t r;
    memset(&r, 0xFF, sizeof r);                  // лишок payload — як стертий
    r.seq = next_seq++;
    memcpy(r.payload, event, len);
    r.crc = crc32(r.payload, sizeof r.payload);  // мітка ставиться ОСТАННЬОЮ

    flash_write(head, &r);                       // запис у голову
    head = ahead;                                // голова посунулась по колу
}

// Відновлення при старті: знайти голову й продовжити нумерацію. O(n).
void log_init(void) {
    uint32_t best_seq = 0, best_idx = 0;
    bool found = false;

    for (uint32_t i = 0; i < N_SECTORS; i++) {
        log_rec_t r;
        flash_read(i, &r);
        if (r.seq == EMPTY_SEQ) continue;                    // вільний — пропустити
        if (r.crc != crc32(r.payload, sizeof r.payload))     // обірваний запис —
            continue;                                        // мітка не сходиться
        if (!found || r.seq > best_seq) {                    // шукаємо найбільший №
            best_seq = r.seq; best_idx = i; found = true;
        }
    }

    if (!found) {                       // чистий Flash: лог іще порожній
        head = 0; next_seq = 1;
    } else {                            // голова — одразу за найновішим записом
        head = (best_idx + 1u) % N_SECTORS;
        next_seq = best_seq + 1u;
    }
}
