int main(void) {
    Counter c = { .value = 0, .threshold = 10 };
    int r;

    r = sd_bus_open_user(&c.bus);        /* під'єднуємось до сеансової шини */
    if (r < 0) goto fail;

    /* СПОЧАТКУ об'єкт, ЛИШЕ ПОТІМ ім'я — інакше клієнт побачить ім'я раніше за метод */
    r = sd_bus_add_object_vtable(c.bus, NULL, SVC_PATH, SVC_IFACE, counter_vtable, &c);
    if (r < 0) goto fail;

    r = sd_bus_request_name(c.bus, SVC_NAME, 0);   /* -EEXIST: ім'я вже зайняте */
    if (r < 0) goto fail;

    for (;;) {
        r = sd_bus_process(c.bus, NULL);  /* щонайбільше ОДНЕ повідомлення за виклик */
        if (r < 0) goto fail;
        if (r > 0) continue;              /* могло лишитися ще — не лягаємо спати */
        r = sd_bus_wait(c.bus, UINT64_MAX);
        if (r < 0) goto fail;
    }
fail:
    fprintf(stderr, "sd-bus: %s\n", strerror(-r));
    sd_bus_flush_close_unref(c.bus);
    return 1;
}
