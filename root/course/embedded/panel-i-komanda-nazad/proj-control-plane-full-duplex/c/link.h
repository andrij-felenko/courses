#ifndef LINK_H
#define LINK_H

#include <stdbool.h>
#include <stdint.h>

#include "dedup.h"

/* Коди відмов, які врешті бачить оператор у панелі. */
#define ERR_NONE           0
#define ERR_TTL_EXPIRED    104
#define ERR_BUSY           105
#define ERR_BAD_PAYLOAD    106
#define ERR_HARDWARE_FAULT 301

/* Наказ, що прийшов темою devices/<id>/cmd/req. */
typedef struct {
    char     cmd_id[CMD_ID_MAX_LEN];
    int      target_pct;
    uint32_t issued_at_sec;
    uint32_t ttl_sec;
} downlink_cmd_t;

typedef enum {
    LINK_PARSE_OK = 0,
    LINK_PARSE_NOT_JSON,
    LINK_PARSE_NO_CMD_ID,
    LINK_PARSE_NO_TARGET,
    LINK_PARSE_TARGET_RANGE
} link_parse_t;

const char  *link_parse_reason(link_parse_t rc);
link_parse_t link_parse_downlink(const char *payload, downlink_cmd_t *out);

/* Фаза 1: квитанція прийому (ACK_RECEIVED / ACK_DUPLICATE). */
void link_publish_ack(const char *cmd_id, const char *status);

/* Проміжні звіти й фаза 2: STARTED / IN_PROGRESS / COMPLETED / FAILED / EXPIRED. */
void link_publish_status(const char *cmd_id, const char *state,
                         int progress_pct, int value_pct, int err);

/* Кадр, з якого не вдалося дістати навіть cmd_id. */
void link_publish_nack(const char *reason);

#endif /* LINK_H */
