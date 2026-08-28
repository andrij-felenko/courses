#include <stdio.h>

typedef struct EventSinkOps {
    void (*on_event)(const char* text);
} EventSinkOps;

typedef struct EventSink {
    const EventSinkOps* ops;
} EventSink;

static void stdout_sink_impl(const char* text) {
    printf("[EVENT]: %s\n", text);
}

static void null_sink_impl(const char* text) {
    (void)text; // Порожня дія
}

static const EventSinkOps STDOUT_OPS = { .on_event = stdout_sink_impl };
static const EventSinkOps NULL_OPS   = { .on_event = null_sink_impl };

int main(void) {
    EventSink active_sink = { .ops = &STDOUT_OPS };
    EventSink silent_sink = { .ops = &NULL_OPS };

    // Виклики безпечні без жодної перевірки на NULL!
    active_sink.ops->on_event("З'єднання встановлено");
    silent_sink.ops->on_event("Ця подія тихо ігнорується");
    return 0;
}
