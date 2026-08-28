#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/uio.h>

enum {
    HDR       = 4,          /* ширина поля довжини */
    MAX_FRAME = 1 << 20,    /* 1 МіБ — стеля тіла; належить специфікації */
    BUF_MIN   = 4096,       /* з чого починає накопичувач */
};

typedef enum {
    FR_OK = 0,      /* порція оброблена — чекаємо наступної події */
    FR_EOF,         /* потік скінчився РІВНО на межі кадру */
    FR_TRUNCATED,   /* потік обірвано ПОСЕРЕД кадру */
    FR_PROTO,       /* порушення кадрування або відмова обробника */
    FR_NOMEM,
    FR_IO,
} fr_status;

struct conn {
    int       fd;
    uint8_t  *buf;    /* накопичувач; NULL до першого читання */
    size_t    cap;    /* скільки байтів виділено */
    size_t    have;   /* скільки байтів лежить; завжди have <= cap */
    int     (*on_frame)(void *user, const uint8_t *body, uint32_t len);
    void     *user;
};
