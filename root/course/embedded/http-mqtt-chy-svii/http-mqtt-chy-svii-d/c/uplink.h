/* uplink.h — «постріл і сон»: одна UDP-датаграма, підтвердження, спул.
 *
 * Прикладний ARQ рівня stop-and-wait: надіслали кадр, чекаємо ACK
 * ARQ_TIMEOUT_MS, до ARQ_ATTEMPTS спроб. Не достукалися — кадр лягає
 * у спул і поїде наступного сеансу, а модем гасне негайно. */
#ifndef UPLINK_H
#define UPLINK_H

#include <sys/socket.h>

#include "frame.h"

#define ARQ_TIMEOUT_MS     500
#define ARQ_ATTEMPTS         3
#define SPOOL_MAX_FRAMES   256  /* 4 КБ — рівно сторінка Flash під відкладене */

typedef struct {
    int                     fd;
    struct sockaddr_storage peer;
    socklen_t               peer_len;
    uint16_t                seq;
    const char             *spool_path;
    long long               tx_ms;    /* сумарний час, коли передавач був потрібен */
} uplink_t;

/* Резолвить host:port і відкриває UDP-сокет. 0 — успіх, -1 — помилка. */
int uplink_open(uplink_t *up, const char *host, const char *port,
                const char *spool_path, uint16_t first_seq);

void uplink_close(uplink_t *up);

/* 0 — сервер підтвердив; -1 — не достукалися, кадр відкладено у спул. */
int uplink_send(uplink_t *up, const sensor_sample_t *sample);

/* Віддає відкладені кадри. Повертає, скільки з них підтверджено. */
int uplink_flush_spool(uplink_t *up);

#endif /* UPLINK_H */
