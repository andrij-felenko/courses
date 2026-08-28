/* Кому призначено пакет. Зсуви полів target_* бере генератор з XML-опису. */
static void packet_target(const mavlink_message_t *m, uint8_t *tsys, uint8_t *tcomp)
{
    const mavlink_msg_entry_t *e = mavlink_get_msg_entry(m->msgid);

    *tsys = *tcomp = 0;                  /* немає адресата → оголошення для всіх */
    if (!e) return;
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM)
        *tsys  = _MAV_PAYLOAD(m)[e->target_system_ofs];
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT)
        *tcomp = _MAV_PAYLOAD(m)[e->target_component_ofs];
}

/* now — монотонний час у мілісекундах; from — номер каналу, звідки байти. */
void router_feed(uint8_t from, const uint8_t *in, size_t n, uint32_t now)
{
    mavlink_message_t msg;
    mavlink_status_t  st;

    for (size_t i = 0; i < n; i++) {
        /* from служить і номером каналу парсера: стан збирання в кожного свій */
        if (!mavlink_parse_char(from, in[i], &msg, &st))
            continue;                            /* кадр ще не зібрано або битий */

        route_learn(msg.sysid, msg.compid, from, now);

        uint8_t tsys, tcomp;
        packet_target(&msg, &tsys, &tcomp);

        uint8_t mask = target_mask(tsys, tcomp, now);
        mask &= (uint8_t)~(1u << from);                            /* не назад   */
        mask &= (uint8_t)~source_mask(msg.sysid, msg.compid, now); /* і не в коло */
        if (!mask) continue;

        uint8_t  out[MAVLINK_MAX_PACKET_LEN];
        uint16_t len = mavlink_msg_to_send_buffer(out, &msg);

        for (uint8_t c = 0; c < NCHAN; c++)
            if (mask & (1u << c))
                chan_write(c, out, len);
    }
}
