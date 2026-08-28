#include <stdint.h>
#include <stddef.h>
#include <assert.h>

struct Header {           /* внутрішнє подання, НЕ те, що йде в мережу */
    uint16_t magic;
    uint8_t  ver;
    uint8_t  flags;
    uint16_t len;
    uint16_t rsv;
    uint64_t time_us;
};

static_assert(offsetof(struct Header, len)     == 4,  "зсув len поїхав");
static_assert(offsetof(struct Header, time_us) == 8,  "зсув time_us поїхав");
static_assert(sizeof(struct Header)            == 16, "розмір заголовка поїхав");
