// монотонний час у секундах — не «стрибне» від корекції системного годинника
static double now_monotonic(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

// Одне місце, куди сходяться всі вхідні повідомлення.
static void handle_message(const mavlink_message_t *msg, LinkState *st) {
    switch (msg->msgid) {
    case MAVLINK_MSG_ID_HEARTBEAT: {                 // серцебиття апарата
        mavlink_heartbeat_t hb;
        mavlink_msg_heartbeat_decode(msg, &hb);
        st->last_heartbeat = now_monotonic();        // позначка «востаннє чули»
        st->armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;
        st->target_system = msg->sysid;              // адреса для власних команд
        st->target_component = msg->compid;
        break;
    }
    case MAVLINK_MSG_ID_GLOBAL_POSITION_INT: {
        mavlink_global_position_int_t p;
        mavlink_msg_global_position_int_decode(msg, &p);
        st->alt_m = p.relative_alt / 1000.0;         // мм → м
        st->lat = p.lat / 1e7;
        st->lon = p.lon / 1e7;
        break;
    }
    case MAVLINK_MSG_ID_SYS_STATUS: {
        mavlink_sys_status_t s;
        mavlink_msg_sys_status_decode(msg, &s);
        st->batt_v = s.voltage_battery / 1000.0;     // мВ → В
        break;
    }
    default: break;                                  // решту типів ігноруємо
    }
}

// Забрати ВСЕ, що накопичилось на лінії. Неблокуюче: read на O_NONBLOCK-fd
// повертає -1/EAGAIN, щойно черга порожня.
static void drain_link(int fd, LinkState *st) {
    uint8_t buf[512];
    for (;;) {
        ssize_t n = read(fd, buf, sizeof buf);
        if (n > 0) {
            for (ssize_t i = 0; i < n; i++) {
                mavlink_message_t msg;
                mavlink_status_t status;
                // parse_char сам МОВЧКИ ковтає пошкоджені кадри (bad CRC) і
                // повертає 0 — тож окрема гілка «BAD_DATA» тут не потрібна.
                if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status))
                    handle_message(&msg, st);
            }
            continue;                 // міг лишитись ще шматок — читаємо далі
        }
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK))
            break;                    // черга вичерпана — це НЕ помилка лінії
        break;                        // n==0 (EOF) чи інша помилка — розбереться детектор heartbeat
    }
}
