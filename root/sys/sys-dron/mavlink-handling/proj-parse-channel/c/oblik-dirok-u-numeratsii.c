static void rx_account(rx_t *rx, const mavlink_message_t *msg)
{
    sender_t *s = NULL;
    for (unsigned i = 0; i < rx->senders; ++i) {
        if (rx->sender[i].sysid == msg->sysid && rx->sender[i].compid == msg->compid) {
            s = &rx->sender[i];
            break;
        }
    }

    if (s == NULL) {                        /* перша зустріч — це не втрата */
        if (rx->senders == RX_MAX_SENDERS) {
            return;
        }
        s = &rx->sender[rx->senders++];
        s->sysid    = msg->sysid;
        s->compid   = msg->compid;
        s->last_seq = msg->seq;
        return;
    }

    if (msg->seq == s->last_seq) {          /* дубль: два маршрути до станції */
        return;
    }

    const uint8_t expected = (uint8_t)(s->last_seq + 1);
    rx->lost   += (uint8_t)(msg->seq - expected);
    s->last_seq = msg->seq;
}
