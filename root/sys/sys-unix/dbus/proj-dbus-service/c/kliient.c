static int on_threshold(sd_bus_message *m, void *ud, sd_bus_error *e) {
    int64_t v;
    if (sd_bus_message_read(m, "x", &v) < 0) return 0;   /* читаємо СТРОГО за сигнатурою */
    printf("поріг перетнуто на %lld\n", (long long)v);
    return 0;
}

static int on_reply(sd_bus_message *m, void *ud, sd_bus_error *e) {
    int64_t v;
    if (sd_bus_message_is_method_error(m, NULL)) {       /* відмова приходить сюди ж */
        const sd_bus_error *err = sd_bus_message_get_error(m);
        fprintf(stderr, "відмовила: %s: %s\n", err->name, err->message);
        return 0;
    }
    sd_bus_message_read(m, "x", &v);
    printf("асинхронно: %lld\n", (long long)v);
    return 0;
}

int main(void) {
    sd_bus *bus = NULL;
    sd_bus_error err = SD_BUS_ERROR_NULL;
    sd_bus_message *reply = NULL, *m = NULL;
    int64_t v;

    if (sd_bus_open_user(&bus) < 0) return 1;

    /* правило добору: NULL у полі означає «це поле не перевіряти» */
    sd_bus_match_signal(bus, NULL, SVC_NAME, SVC_PATH, SVC_IFACE, "Threshold",
                        on_threshold, NULL);

    /* синхронно: доречно в утиліті, небезпечно в циклі подій */
    if (sd_bus_call_method(bus, SVC_NAME, SVC_PATH, SVC_IFACE, "Add",
                           &err, &reply, "x", (int64_t)4) < 0) {
        fprintf(stderr, "%s: %s\n", err.name, err.message);
        sd_bus_error_free(&err);            /* рядки можуть бути з купи — звільняти обов'язково */
        return 1;
    }
    sd_bus_message_read(reply, "x", &v);
    printf("синхронно: %lld\n", (long long)v);
    sd_bus_message_unref(reply);

    /* асинхронно: відправили й пішли крутити цикл; 0 — типовий тайм-аут */
    sd_bus_message_new_method_call(bus, &m, SVC_NAME, SVC_PATH, SVC_IFACE, "Add");
    sd_bus_message_append(m, "x", (int64_t)7);
    sd_bus_call_async(bus, NULL, m, on_reply, NULL, 0);
    sd_bus_message_unref(m);

    for (;;) {                              /* той самий цикл, що й у службі */
        int r = sd_bus_process(bus, NULL);
        if (r < 0) break;
        if (r > 0) continue;
        if (sd_bus_wait(bus, UINT64_MAX) < 0) break;
    }
    sd_bus_flush_close_unref(bus);
    return 0;
}
