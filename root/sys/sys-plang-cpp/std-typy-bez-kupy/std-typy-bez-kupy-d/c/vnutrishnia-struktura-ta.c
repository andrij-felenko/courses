#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EVENT_DATA,
    EVENT_ERROR,
    EVENT_PING
} EventType;

typedef struct {
    EventType type;
    union {
        struct { uint8_t payload[16]; } data;
        struct { uint32_t error_code; } error;
        struct { uint32_t sequence_id; } ping;
    } as;
} CEvent;

void handle_event_c(const CEvent* ev) {
    if (!ev) return;
    switch (ev->type) {
        case EVENT_DATA:
            // Немає компіляторного захисту від звернення до ev->as.error!
            break;
        case EVENT_ERROR:
            break;
        case EVENT_PING:
            break;
    }
}
