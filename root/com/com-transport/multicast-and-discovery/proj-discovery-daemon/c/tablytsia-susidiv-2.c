static void peer_update(const uint8_t *id, uint32_t inc, const struct in_addr *ip,
                        uint16_t port, uint16_t caps, const char *name, size_t nl,
                        uint32_t ttl_s, unsigned ifindex)
{
    struct peer *p = peer_find(id);

    if (ttl_s == 0) {                        /* прощання */
        if (p) { printf("— пішов %s\n", p->name); *p = peers[--npeers]; }
        return;
    }
    if (!p) {
        if (npeers == MAX_PEERS) return;     /* краще не взяти нового, ніж утратити всіх */
        p = &peers[npeers++];
        memset(p, 0, sizeof *p);
        memcpy(p->id, id, 16);
    }
    if (inc < p->incarnation) return;        /* пакет старіший за те, що ми вже знаємо */
    if (inc > p->incarnation) p->caps = 0;   /* вузол перезапустився: накопичене недійсне */

    p->incarnation = inc;
    p->addr    = *ip;
    p->port    = port;
    p->caps    = caps;
    p->ifindex = ifindex;
    memcpy(p->name, name, nl);
    p->name[nl] = '\0';

    uint64_t t   = now_ms();
    p->ttl_ms     = (uint64_t)ttl_s * 1000u;
    p->expires_ms = t + p->ttl_ms;
    p->probe_step = 0;
    schedule_probe(p);
}
