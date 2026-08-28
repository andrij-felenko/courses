// Поліморфізм через структури з покажчиками на функції (C)
typedef struct IHandler {
    int (*handle)(void* ctx, int event);
} IHandler;

typedef struct FastHandler {
    IHandler base;
    int multiplier;
} FastHandler;

static int fast_handle(void* ctx, int event) {
    FastHandler* self = (FastHandler*)ctx;
    return event * self->multiplier;
}

int dispatch_event(IHandler* handler, int event) {
    // Непрямий виклик через покажчик — дорожчий за прямий
    return handler->handle(handler, event);
}
