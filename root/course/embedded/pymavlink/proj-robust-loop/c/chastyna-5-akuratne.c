static volatile sig_atomic_t g_stop = 0;
static void on_sigint(int sig) { (void)sig; g_stop = 1; }   // Ctrl+C → прапорець, а не миттєва смерть

static void send_disarm(int fd, const LinkState *st) {
    mavlink_message_t msg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_msg_command_long_pack(MY_SYSID, MY_COMPID, &msg,
        st->target_system, st->target_component,
        MAV_CMD_COMPONENT_ARM_DISARM, 0,
        0, 0, 0, 0, 0, 0, 0);   // param1 = 0 → disarm
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    write(fd, buf, len);
}

// Акуратно завершитись: роззброїти (ЛИШЕ на землі!) і закрити лінію.
static void shutdown_link(int fd, LinkState *st) {
    if (fd >= 0 && link_alive(st)) {
        // disarm тільки якщо апарат озброєний І на землі — інакше це падіння!
        if (st->armed && st->alt_m < 0.5) {
            printf("[EXIT] апарат на землі — роззброюю\n");
            send_disarm(fd, st);
        } else {
            printf("[EXIT] апарат у польоті або стан невідомий — НЕ чіпаю\n");
        }
    }
    if (fd >= 0) close(fd);      // завжди звільняємо лінію
    printf("[EXIT] з'єднання закрито\n");
}
