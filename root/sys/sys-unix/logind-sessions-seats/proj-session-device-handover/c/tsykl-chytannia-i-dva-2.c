static int on_pause(sd_bus_message *m, void *userdata, sd_bus_error *e) {
    Ctx *c = userdata;
    uint32_t maj, min;
    const char *type;

    int r = sd_bus_message_read(m, "uus", &maj, &min, &type);
    if (r < 0 || maj != c->major || min != c->minor)
        return r < 0 ? r : 0;

    printf("PauseDevice(%s)\n", type);
    c->io = sd_event_source_unref(c->io);        /* більше не чекаємо на цьому fd */

    if (strcmp(type, "gone") == 0) {
        close(c->fd);
        c->fd = -1;
        return sd_event_exit(c->event, 0);
    }

    if (strcmp(type, "pause") == 0) {
        /* БЕЗ цієї відповіді перемикання місця не завершиться ніколи */
        r = sd_bus_call_method(c->bus, LOGIND, c->path, SES_IFACE,
                               "PauseDeviceComplete", NULL, NULL, "uu", maj, min);
        if (r < 0)
            return r;
    }

    unsigned char probe;                          /* показово: дескриптор уже мертвий */
    if (read(c->fd, &probe, 1) < 0)
        printf("  read() після паузи → %s\n", strerror(errno));
    return 0;
}
