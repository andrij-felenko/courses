/* Виклик із приймача на кожне розібране повідомлення MAVLink. */
void station_on_message(hb_watchdog_t *wd,
                        uint16_t msg_id,
                        uint8_t  src_sys,
                        uint8_t  src_comp,
                        const void *payload,
                        uint32_t now_ms)
{
    if (msg_id == MAVLINK_MSG_ID_HEARTBEAT) {   /* == 0 */
        heartbeat_msg_t hb;
        hb.sys       = src_sys;
        hb.comp      = src_comp;
        /* дістаємо потрібні поля з корисних даних (розбір — не наша тема) */
        mavlink_heartbeat_decode(payload, &hb.type, &hb.autopilot,
                                 &hb.base_mode, &hb.custom_mode);

        hb_event_t evt = hb_on_heartbeat(wd, &hb, now_ms);
        if (evt == HB_EVT_DISCOVERED)
            ui_add_vehicle_marker(hb.sys, hb.comp, hb.type, hb.autopilot);
        else if (evt == HB_EVT_RECOVERED)
            ui_mark_vehicle_alive(hb.sys, hb.comp);   /* мітку — повернути */
    }

    /* інші повідомлення — телеметрія, ACK, місія — своїм маршрутом */
    /* route_other_message(msg_id, src_sys, src_comp, payload); */
}

/* Колбек для hb_tick: реакція на смерть джерела. */
static void on_presence_event(const hb_source_t *s, hb_event_t evt, void *user)
{
    (void)user;
    if (evt == HB_EVT_LOST) {
        ui_mark_vehicle_dead(s->sys, s->comp);   /* мітку — згасити */
        alarm_raise(s->sys, s->comp);            /* сигнал тривоги */
    }
}
