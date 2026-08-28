static void resync(int ui, int src, unsigned long *held)
{
        unsigned long now[KEYWORDS] = { 0 };

        if (ioctl(src, EVIOCGKEY(sizeof now), now) < 0) return;
        for (unsigned c = 0; c <= KEY_MAX; c++)
                if (TESTBIT(held, c) != TESTBIT(now, c))
                        emit(ui, EV_KEY, remap(c), TESTBIT(now, c) ? 1 : 0);
        memcpy(held, now, sizeof now);
        emit(ui, EV_SYN, SYN_REPORT, 0);
}

int main(int argc, char **argv)
{
        unsigned long held[KEYWORDS] = { 0 };
        struct input_event ev;
        int src, ui;

        if (argc != 2) {
                fprintf(stderr, "потрібен шлях: %s /dev/input/eventN\n", argv[0]);
                return 2;
        }
        if ((src = open(argv[1], O_RDONLY)) < 0)      { perror(argv[1]);      return 1; }
        if ((ui = open("/dev/uinput", O_WRONLY)) < 0) { perror("/dev/uinput"); return 1; }
        if (build_device(ui, src) < 0)                { perror("створення");   return 1; }

        wait_for_node(ui);
        usleep(400 * 1000);      /* читачам на відкриття: спитати про це нікого не можна */

        if (ioctl(src, EVIOCGRAB, 1) < 0) { perror("EVIOCGRAB"); return 1; }

        while (read(src, &ev, sizeof ev) == (ssize_t)sizeof ev) {
                if (ev.type == EV_SYN && ev.code == SYN_DROPPED) {
                        resync(ui, src, held);        /* наша копія стану — брехня */
                        continue;
                }
                if (ev.type == EV_KEY) {
                        if (ev.value == 1)      SETBIT(held, ev.code);
                        else if (ev.value == 0) CLRBIT(held, ev.code);
                        ev.code = remap(ev.code);
                }
                if (write(ui, &ev, sizeof ev) != (ssize_t)sizeof ev) break;
        }

        ioctl(ui, UI_DEV_DESTROY);
        return 0;
}
