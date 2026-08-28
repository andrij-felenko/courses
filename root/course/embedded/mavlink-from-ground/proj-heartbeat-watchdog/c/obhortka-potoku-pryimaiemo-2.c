void station_loop(void)
{
    hb_watchdog_t wd;
    hb_init(&wd);

    for (;;) {
        uint32_t now = millis();   /* монотонний час, мс */

        /* 1) з'їдаємо всі готові вхідні пакети (кожен HEARTBEAT освіжає час) */
        mavlink_message_t msg;
        while (link_poll(&msg))
            station_on_message(&wd, msg.msgid, msg.sysid, msg.compid,
                               msg.payload, now);

        /* 2) перевіряємо, хто замовк (це і ловить смерть — за часом, не за подією) */
        hb_tick(&wd, now, on_presence_event, NULL);

        /* 3) решта роботи станції: малюємо екран, шлемо команди... */
        ui_render();
    }
}
