#include "dedup.h"

#include <string.h>

/* Кільце фіксованого розміру: динамічної пам'яті в прошивці немає. */
static dedup_entry_t s_dedup[DEDUP_HISTORY_SIZE];
static uint8_t       s_head;
static uint8_t       s_count;

static void copy_str(char *dst, size_t cap, const char *src)
{
    size_t n = 0;
    while (src[n] != '\0' && n + 1 < cap) {
        dst[n] = src[n];
        ++n;
    }
    dst[n] = '\0';
}

/* Історію читає мережевий колбек, а пише ще й воркер приводу.
   На FreeRTOS обидва доступи загортають у мьютекс; тут цикл один. */
static dedup_entry_t *locate(const char *cmd_id)
{
    for (uint8_t i = 0; i < s_count; ++i) {
        if (strncmp(s_dedup[i].cmd_id, cmd_id, CMD_ID_MAX_LEN) == 0) {
            return &s_dedup[i];
        }
    }
    return NULL;
}

void dedup_reset(void)
{
    memset(s_dedup, 0, sizeof s_dedup);
    s_head = 0;
    s_count = 0;
}

const dedup_entry_t *dedup_find(const char *cmd_id)
{
    return locate(cmd_id);
}

void dedup_remember(const char *cmd_id, uint32_t now_sec)
{
    dedup_entry_t *slot = &s_dedup[s_head];

    memset(slot, 0, sizeof *slot);
    copy_str(slot->cmd_id, sizeof slot->cmd_id, cmd_id);
    copy_str(slot->state, sizeof slot->state, "QUEUED");
    slot->stamp_sec = now_sec;

    s_head = (uint8_t)((s_head + 1u) % DEDUP_HISTORY_SIZE);
    if (s_count < DEDUP_HISTORY_SIZE) {
        ++s_count;
    }
}

void dedup_update(const char *cmd_id, const char *state,
                  int progress_pct, int value_pct, int err)
{
    dedup_entry_t *slot = locate(cmd_id);
    if (slot == NULL) {
        return;
    }
    copy_str(slot->state, sizeof slot->state, state);
    slot->progress_pct = progress_pct;
    slot->value_pct = value_pct;
    slot->err = err;
}
