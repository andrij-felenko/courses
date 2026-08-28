typedef struct {
    Event *buffer;
    size_t capacity;
    volatile size_t head;
    volatile size_t tail;
    volatile size_t count;
    uint32_t overflow_drops;
} EventQueue;

void event_queue_init(EventQueue *q, Event *buffer, size_t capacity);
bool event_queue_post(EventQueue *q, const Event *ev);
bool event_queue_pop(EventQueue *q, Event *out_ev);
bool event_queue_peek(const EventQueue *q, Event *out_ev);
void event_queue_clear(EventQueue *q);
size_t event_queue_get_count(const EventQueue *q);
