/* Бік пульта: складання запитів і пам'ять про поточну селекцію. */
#ifndef SBO_CLIENT_H
#define SBO_CLIENT_H

#include "sbo_proto.h"

struct sbo_client {
    uint8_t  source_id;
    uint8_t  seq;
    uint8_t  target_id;
    uint8_t  target_comp;
    uint16_t cmd_code;
    uint16_t window_ms;
    uint32_t token;
    bool     armed;        /* пульт вважає, що замок наш */
    uint8_t  last_error;   /* 0 — останній обмін пройшов чисто */
};

void sbo_client_init(struct sbo_client *c, uint8_t source_id);

size_t sbo_client_select(struct sbo_client *c, uint8_t target_id, uint8_t comp,
                         uint16_t cmd_code, uint16_t window_ms,
                         uint8_t *out, size_t cap);
size_t sbo_client_operate(struct sbo_client *c, const uint8_t *params,
                          uint8_t params_len, uint8_t *out, size_t cap);
size_t sbo_client_cancel(struct sbo_client *c, uint8_t *out, size_t cap);
size_t sbo_client_ping(struct sbo_client *c, uint8_t target_id,
                       uint8_t *out, size_t cap);

/* Оновлює уявлення пульта про замок за квитанцією борту. */
void sbo_client_on_reply(struct sbo_client *c, const struct sbo_frame *r);

#endif /* SBO_CLIENT_H */
