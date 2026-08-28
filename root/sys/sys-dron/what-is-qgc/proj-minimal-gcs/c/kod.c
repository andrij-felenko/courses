/* Останній відомий стан: кожне поле оновлюється своїм повідомленням,
   у своєму темпі, незалежно від решти. */
struct snapshot {
    int      seen;                /* чи прийшло бодай одне серцебиття    */
    uint8_t  sysid, compid;       /* хто саме до нас говорить            */
    int      armed;
    uint32_t custom_mode;         /* число; назва режиму залежить від стеку */
    float    volts;               /* В   */
    int8_t   battery_pct;         /* %, −1 якщо борт не знає */
    double   lat, lon;            /* °   */
    float    alt_rel;             /* м над точкою зльоту */
};

/* Повертає result із COMMAND_ACK на нашу команду або −1, якщо це не вона. */
static int apply(const mavlink_message_t *m, struct snapshot *s) {
    switch (m->msgid) {
    case MAVLINK_MSG_ID_HEARTBEAT: {
        if (m->compid != MAV_COMP_ID_AUTOPILOT1)
            break;                /* камери й підвіси теж б'ють серцем */
        mavlink_heartbeat_t hb;
        mavlink_msg_heartbeat_decode(m, &hb);
        s->seen  = 1;
        s->sysid = m->sysid;  s->compid = m->compid;
        s->armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;
        s->custom_mode = hb.custom_mode;
        break;
    }
    case MAVLINK_MSG_ID_SYS_STATUS: {
        mavlink_sys_status_t st;
        mavlink_msg_sys_status_decode(m, &st);
        s->volts       = st.voltage_battery / 1000.0f;   /* мВ → В */
        s->battery_pct = st.battery_remaining;
        break;
    }
    case MAVLINK_MSG_ID_GLOBAL_POSITION_INT: {
        mavlink_global_position_int_t p;
        mavlink_msg_global_position_int_decode(m, &p);
        s->lat = p.lat / 1e7;  s->lon = p.lon / 1e7;      /* degE7 → ° */
        s->alt_rel = p.relative_alt / 1000.0f;            /* мм → м   */
        break;
    }
    case MAVLINK_MSG_ID_COMMAND_ACK: {
        mavlink_command_ack_t a;
        mavlink_msg_command_ack_decode(m, &a);
        if (a.command == MAV_CMD_SET_MESSAGE_INTERVAL) return a.result;
        break;
    }
    default: break;               /* решту потоку свідомо не чіпаємо */
    }
    return -1;
}
