struct input_event ev;
ssize_t n;

while ((n = read(fd, &ev, sizeof ev)) == sizeof ev) {
    if (ev.type == EV_SYN && ev.code == SYN_DROPPED) {
        resync = 1;              /* усе накопичене — сміття */
        continue;
    }
    if (ev.type == EV_SYN && ev.code == SYN_REPORT) {
        if (resync) {            /* кадр докрутили до кінця — тепер знімок */
            query_full_state(fd);
            resync = 0;
        } else {
            apply_frame(&pending);   /* застосувати кадр одним ривком */
        }
        continue;
    }
    if (!resync)
        accumulate(&pending, &ev);   /* поки що лише накопичуємо */
}
