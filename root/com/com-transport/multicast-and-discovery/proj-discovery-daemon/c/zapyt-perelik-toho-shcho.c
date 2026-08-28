static void send_query(uint64_t t)
{
    uint8_t buf[PKT_MAX];
    size_t  len = build(buf, PKT_QUERY, REC_TTL_S);
    size_t  kn  = 0;

    for (int i = 0; i < npeers && len + 20 <= PKT_MAX && kn < 20; i++) {
        if (peers[i].probe_step != 0 || peers[i].probe_ms <= t) continue;  /* цих і питаємо */
        memcpy(buf + len, peers[i].id, 16);
        put_u32(buf + len + 16, peers[i].incarnation);
        len += 20;
        kn++;
    }
    put_u16(buf + 38, (uint16_t)kn);

    for (int i = 0; i < nifs; i++)
        send_on(ifs[i].index, buf, len);
}
