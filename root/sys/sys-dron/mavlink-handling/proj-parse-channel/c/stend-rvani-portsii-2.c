static mavlink_signing_t         g_signing;
static mavlink_signing_streams_t g_streams;

static void channel_require_signature(uint8_t chan, const uint8_t key[32])
{
    memcpy(g_signing.secret_key, key, 32);
    g_signing.link_id                  = 0;
    g_signing.flags                    = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
    g_signing.accept_unsigned_callback = NULL;   /* нічого непідписаного не пускати */

    mavlink_status_t *st = mavlink_get_channel_status(chan);
    st->signing         = &g_signing;
    st->signing_streams = &g_streams;
}

int main(void)
{
    const uint8_t tx_auto = channel_take();
    const uint8_t tx_cam  = channel_take();
    const uint8_t rx_chan = channel_take();

    if (tx_auto == RX_NO_CHANNEL || tx_cam == RX_NO_CHANNEL || rx_chan == RX_NO_CHANNEL) {
        fprintf(stderr, "слотів немає: MAVLINK_COMM_NUM_BUFFERS = %d\n",
                MAVLINK_COMM_NUM_BUFFERS);
        return 1;
    }

    rx_t rx;
    memset(&rx, 0, sizeof rx);
    rx.chan = rx_chan;

    /* шість кадрів автопілота (seq 0…5) і один кадр камери (seq 0) */
    uint8_t  air[6][MAVLINK_MAX_PACKET_LEN];
    uint16_t air_len[6];
    for (int i = 0; i < 6; ++i) {
        air_len[i] = frame_heartbeat(air[i], tx_auto, 1, MAV_COMP_ID_AUTOPILOT1);
    }
    uint8_t        cam[MAVLINK_MAX_PACKET_LEN];
    const uint16_t cam_len = frame_heartbeat(cam, tx_cam, 1, MAV_COMP_ID_CAMERA);

    /* 1. сміття на старті: жоден байт не є стартовим */
    static const uint8_t junk[3] = { 0x00, 0xA5, 0x37 };
    rx_feed(&rx, junk, sizeof junk);

    /* 2. перші 8 байтів кадру — решта прийде наступним читанням */
    rx_feed(&rx, air[0], 8);

    /* 3. хвіст першого кадру + цілий кадр seq 3 + початок кадру камери */
    uint8_t chunk3[64];
    size_t  n3 = 0;
    memcpy(chunk3 + n3, air[0] + 8, air_len[0] - 8); n3 += air_len[0] - 8;
    memcpy(chunk3 + n3, air[3], air_len[3]);         n3 += air_len[3];
    memcpy(chunk3 + n3, cam, 5);                     n3 += 5;
    rx_feed(&rx, chunk3, n3);

    /* 4. хвіст кадру камери + кадр із затертою контрольною сумою */
    uint8_t broken[MAVLINK_MAX_PACKET_LEN];
    memcpy(broken, air[4], air_len[4]);
    broken[air_len[4] - 2] = 0x00;
    broken[air_len[4] - 1] = 0x00;

    uint8_t chunk4[64];
    size_t  n4 = 0;
    memcpy(chunk4 + n4, cam + 5, cam_len - 5); n4 += cam_len - 5;
    memcpy(chunk4 + n4, broken, air_len[4]);   n4 += air_len[4];
    rx_feed(&rx, chunk4, n4);

    /* 5. кадр із повідомленням, якого немає в діалекті збірки */
    uint8_t alien[16];
    rx_feed(&rx, alien, frame_alien(alien));

    /* 6. вмикаємо підпис — і той самий цілий кадр стає «поганим підписом» */
    static const uint8_t key[32] = { 0 };
    channel_require_signature(rx.chan, key);
    rx_feed(&rx, air[5], air_len[5]);

    printf("INCOMPLETE      %u\n", rx.verdict[MAVLINK_FRAMING_INCOMPLETE]);
    printf("OK              %u\n", rx.verdict[MAVLINK_FRAMING_OK]);
    printf("BAD_CRC         %u\n", rx.verdict[MAVLINK_FRAMING_BAD_CRC]);
    printf("BAD_SIGNATURE   %u\n", rx.verdict[MAVLINK_FRAMING_BAD_SIGNATURE]);
    printf("цілих кадрів    %llu\n", (unsigned long long)rx.whole);
    printf("дірок у номерах %llu\n", (unsigned long long)rx.lost);
    printf("чужий діалект   %u\n", rx.alien);
    printf("відправників    %u\n", rx.senders);

    channel_give(tx_auto);
    channel_give(tx_cam);
    channel_give(rx_chan);
    return 0;
}
