#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define EVQ_CAP        16       // місткість кільця — стеля накопичення
#define EVQ_PAYLOAD    24       // байтів корисних даних на подію

// Один запис у черзі критичних подій.
typedef struct {
    uint32_t seq;                    // наскрізний номер: 1, 2, 3, … (0 = порожньо)
    uint32_t ts;                     // коли сталося (unix-час або uptime, мс)
    uint8_t  type;                   // код події: 1=протік, 2=двері, 3=дим…
    uint8_t  len;                    // скільки байтів у payload насправді
    char     payload[EVQ_PAYLOAD];   // короткий опис/значення
} event_t;

// Саме кільце: масив + два покажчики + наскрізний лічильник.
typedef struct {
    event_t  buf[EVQ_CAP];
    uint16_t head;        // куди писати наступну
    uint16_t tail;        // найстаріша непідтверджена
    uint16_t count;       // скільки зараз у черзі (0..EVQ_CAP)
    uint32_t next_seq;    // який seq присвоїти наступній події
} event_queue_t;

static event_queue_t g_evq;
