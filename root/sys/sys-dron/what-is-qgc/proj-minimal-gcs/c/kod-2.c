int main(void) {
    int fd = open_udp(14550);
    struct sockaddr_in peer; socklen_t peer_len = 0;   /* звідки почули — туди й шлемо */
    struct snapshot s = { 0 };
    int ack = -1, tries = 0;
    uint64_t next_try = 0, last_print = 0;
    uint8_t buf[2048];

    for (;;) {
        struct sockaddr_in from; socklen_t from_len = sizeof from;
        ssize_t n = recvfrom(fd, buf, sizeof buf, 0,
                             (struct sockaddr *)&from, &from_len);

        for (ssize_t i = 0; i < n; i++) {              /* n < 0 на таймауті — цикл не виконається */
            mavlink_message_t msg;  mavlink_status_t st;
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &st)) {
                if (!peer_len) { peer = from; peer_len = from_len; }
                int r = apply(&msg, &s);
                if (r >= 0) ack = r;
            }
        }

        uint64_t t = now_ms();
        if (s.seen && ack < 0 && tries < 5 && t >= next_try) {
            mavlink_message_t out;
            mavlink_msg_command_long_pack(
                GCS_SYSID, GCS_COMPID, &out,
                s.sysid, s.compid,
                MAV_CMD_SET_MESSAGE_INTERVAL,
                tries,                                  /* confirmation: 0, 1, 2, … */
                MAVLINK_MSG_ID_GLOBAL_POSITION_INT,     /* param1: який потік       */
                500000,                                 /* param2: період, мкс → 2 Гц */
                0, 0, 0, 0, 0);
            uint8_t out_buf[MAVLINK_MAX_PACKET_LEN];
            uint16_t len = mavlink_msg_to_send_buffer(out_buf, &out);
            sendto(fd, out_buf, len, 0, (struct sockaddr *)&peer, peer_len);
            tries++;  next_try = t + 1000;
        }

        if (s.seen && t - last_print >= 1000) {
            last_print = t;
            printf("sys %u  %s  режим %u  %.1f В  %d%%  %.6f %.6f  %.1f м  ack=%d\n",
                   s.sysid, s.armed ? "ЗБРОЄНО" : "роззброєно", s.custom_mode,
                   s.volts, s.battery_pct, s.lat, s.lon, s.alt_rel, ack);
        }
    }
}
