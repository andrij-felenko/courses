typedef struct { uint32_t epoch, seq; } hdr;

typedef struct {
    state_sink sink;
    uint32_t   epoch;
    int        have_epoch;
} peer;

void on_packet(peer *p, const hdr *h, const fix *f)
{
    if (!p->have_epoch || h->epoch != p->epoch) {   /* відправник перезапустився */
        arw_init(&p->sink.win);                     /* нумерація починається наново */
        p->epoch = h->epoch;
        p->have_epoch = 1;
    }
    on_datagram(&p->sink, h->seq, f);
}
