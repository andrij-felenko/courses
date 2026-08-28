struct peer {
    uint8_t        id[16];
    uint32_t       incarnation;
    struct in_addr addr;
    uint16_t       port;
    uint16_t       caps;
    char           name[64];
    unsigned       ifindex;
    uint64_t       ttl_ms;          /* скільки життя дав сам вузол */
    uint64_t       expires_ms;      /* коли викинути */
    uint64_t       probe_ms;        /* коли перепитати */
    int            probe_step;      /* 0…3: 80 %, 85 %, 90 %, 95 % */
};

static struct peer peers[MAX_PEERS];
static int          npeers;

static struct peer *peer_find(const uint8_t id[16])
{
    for (int i = 0; i < npeers; i++)
        if (memcmp(peers[i].id, id, 16) == 0) return &peers[i];
    return NULL;
}

static void schedule_probe(struct peer *p)
{
    static const unsigned left[4] = { 20, 15, 10, 5 };     /* % життя, що лишилося */
    if (p->probe_step >= 4) { p->probe_ms = p->expires_ms; return; }
    p->probe_ms = p->expires_ms - p->ttl_ms * left[p->probe_step] / 100;
}
