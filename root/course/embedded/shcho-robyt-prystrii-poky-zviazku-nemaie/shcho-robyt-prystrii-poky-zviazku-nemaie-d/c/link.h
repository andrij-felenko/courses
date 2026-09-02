#ifndef LINK_H
#define LINK_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Канал до пульта. Поки кадр не пройшов CRC, перевірку мітки автентичності,
// звірку сесії та захист від повтору — це НЕ команда: він не годує мертвої
// руки й не доходить до приводів.
#define LINK_FRAME_SIZE   24U
#define LINK_TYPE_HELLO   0x01U
#define LINK_TYPE_CMD     0x02U

// Наскільки застарілою може бути команда, щоб її ще мало сенс виконувати.
#define LINK_MAX_AGE_MS   500U

typedef enum {
    LINK_OK = 0,
    LINK_ERR_LENGTH,
    LINK_ERR_TYPE,
    LINK_ERR_CRC,
    LINK_ERR_AUTH,
    LINK_ERR_SESSION,
    LINK_ERR_REPLAY,
    LINK_ERR_STALE
} link_status_t;

typedef struct {
    uint8_t  type;
    uint32_t session_id;
    uint32_t seq;
    uint32_t t_ms;        // час відправника
    float    throttle;
    float    steering;
} link_command_t;

typedef struct {
    uint32_t key;          // спільний секрет
    uint32_t session_id;   // 0 — сесії немає
    uint32_t last_seq;
    int32_t  clock_bias;   // наскільки годинник пульта попереду нашого
    bool     established;

    uint32_t accepted;
    uint32_t rej_crc;
    uint32_t rej_auth;
    uint32_t rej_session;
    uint32_t rej_replay;
    uint32_t rej_stale;
} link_t;

void link_init(link_t *l, uint32_t key);
void link_drop_session(link_t *l);   // сесія й усі відкладені команди анульовані
bool link_established(const link_t *l);

link_status_t link_accept(link_t *l, const uint8_t *frame, size_t len,
                          uint32_t now_ms, link_command_t *out);

// Бік пульта — щоб сценарій справді збирав кадри, а не підсовував структуру.
size_t link_encode_hello(uint8_t *buf, size_t cap, uint32_t key,
                         uint32_t session_id, uint32_t t_ms);
size_t link_encode_command(uint8_t *buf, size_t cap, uint32_t key, uint32_t session_id,
                           uint32_t seq, uint32_t t_ms, float throttle, float steering);

const char *link_status_name(link_status_t st);

#endif /* LINK_H */
