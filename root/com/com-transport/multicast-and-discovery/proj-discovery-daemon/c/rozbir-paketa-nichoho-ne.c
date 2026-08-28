static void on_packet(const uint8_t *b, size_t n, const struct in_addr *from, unsigned ifindex)
{
    if (n < HDR_LEN || memcmp(b, "DSC1", 4) != 0 || b[4] != PROTO_VER) return;

    uint8_t  type = b[5];
    uint32_t inc  = get_u32(b + 24);
    uint32_t ttl  = get_u32(b + 28);
    uint16_t port = get_u16(b + 32);
    uint16_t caps = get_u16(b + 34);
    size_t   nl   = get_u16(b + 36);
    size_t   kn   = get_u16(b + 38);

    if (nl > 63 || n < HDR_LEN + nl + kn * 20) return;   /* обрізаний або брехливий */

    if (memcmp(b + 8, me.id, 16) == 0) {                 /* пакет ПРО НАС */
        if (type != PKT_QUERY) answered_ms = now_ms();   /* наша відповідь уже в ефірі */
        return;
    }

    peer_update(b + 8, inc, from, port, caps, (const char *)b + HDR_LEN, nl, ttl, ifindex);

    if (type == PKT_QUERY) {
        const uint8_t *ka = b + HDR_LEN + nl;
        for (size_t i = 0; i < kn; i++)
            if (memcmp(ka + i * 20, me.id, 16) == 0 &&
                get_u32(ka + i * 20 + 16) == me.incarnation)
                return;                                  /* нас уже знають — мовчимо */
        schedule_answer(now_ms());
    }
}
