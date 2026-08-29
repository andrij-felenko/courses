#ifndef DEDUP_H
#define DEDUP_H

#include <stdbool.h>
#include <stdint.h>

#define CMD_ID_MAX_LEN     37   /* UUID у текстовому вигляді + '\0' */
#define DEDUP_STATE_MAX    16
#define DEDUP_HISTORY_SIZE 16

/* Один слот історії: ідентифікатор команди і останній відомий результат.
   Результат тримаємо саме тут — щоб на повтор відповісти правдою про залізо,
   а не смикати привід удруге. */
typedef struct {
    char     cmd_id[CMD_ID_MAX_LEN];
    uint32_t stamp_sec;
    char     state[DEDUP_STATE_MAX];
    int      progress_pct;
    int      value_pct;
    int      err;
} dedup_entry_t;

/* Скидання історії (виклик на старті: RAM після перезавантаження чиста). */
void dedup_reset(void);

/* NULL, якщо такої команди ще не бачили. */
const dedup_entry_t *dedup_find(const char *cmd_id);

/* Записати нову команду в кільце; найстаріший запис витісняється. */
void dedup_remember(const char *cmd_id, uint32_t now_sec);

/* Оновити відомий результат; невідомий cmd_id ігнорується. */
void dedup_update(const char *cmd_id, const char *state,
                  int progress_pct, int value_pct, int err);

#endif /* DEDUP_H */
