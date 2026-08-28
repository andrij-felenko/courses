typedef struct {
    pt_t pt;
    int sum, i;                        // стан живе поза кадром — переживе паузи
} avg_ctx_t;

static int pt_average_OK(avg_ctx_t *c) {
    PT_BEGIN(&c->pt);
    c->sum = 0;
    for (c->i = 0; c->i < 10; c->i++) {
        c->sum += sensor_read();
        PT_WAIT_UNTIL(&c->pt, tick());
    }
    publish(c->sum / 10);
    PT_END(&c->pt);
}
