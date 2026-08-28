static const char *const TEMPL[5] = {
        "%05d  sshd[%d]: accepted publickey for andrij from 10.0.4.7",
        "%05d  kernel: usb 1-2: new high-speed device number %d",
        "%05d  cron[%d]: (root) CMD (/usr/lib/sysstat/sa1 1 1)",
        "%05d  systemd[1]: started session %d of user andrij",
        "%05d  nginx: GET /api/v1/status 200 %d bytes",
};

static void put_text(Screen *s, int y, int x, const char *t, int attr)
{
        for (int i = 0; t[i] && x + i < COLS; i++) {
                s->c[y][x + i].ch = (unsigned char) t[i];
                s->c[y][x + i].attr = (unsigned char) attr;
        }
}

static void build(Screen *s, int first, const char *clock, int hits)
{
        char buf[COLS + 1];

        for (int y = 0; y < ROWS; y++)
                for (int x = 0; x < COLS; x++) {
                        s->c[y][x].ch = ' ';
                        s->c[y][x].attr = 0;
                }
        for (int y = 0; y < ROWS - 1; y++) {
                int n = first + y;

                snprintf(buf, sizeof buf, TEMPL[n % 5], n, 4000 + n);
                put_text(s, y, 0, buf, n % 7 == 0 ? 9 : 0);
        }
        snprintf(buf, sizeof buf, " %s   lines %d   matches %-4d   q quits",
                 clock, first + ROWS - 2, hits);
        put_text(s, ROWS - 1, 0, buf, 4);
}

static void measure(const char *what, const Screen *cur, const Screen *ns)
{
        Wire w = { 0, 0, 0, -1, -1 };
        Screen tmp = *cur;              /* прокрутка міняє копію — вимір псувати не можна */
        Shift s;
        size_t full, diff, near, scrl;

        begin(&w); full = redraw_full(&w, ns);
        begin(&w); diff = redraw_diff(&w, cur, ns);
        begin(&w); near = redraw_near(&w, cur, ns);

        begin(&w);
        s = find_shift(&tmp, ns);
        if (s.d)
                scroll_lines(&w, &tmp, s);
        scrl = redraw_near(&w, &tmp, ns);

        printf("%s\n", what);
        printf("   повне перемальовування   %6zu\n", full);
        printf("   різниця по комірках      %6zu\n", diff);
        printf("   різниця з курсором       %6zu\n", near);
        if (s.d)
                printf("   + прокрутка (зсув %+d)    %6zu   смуга %d…%d\n",
                       s.d, scrl, s.top, s.bot);
        else
                printf("   прокрутки не видно\n");
        putchar('\n');
}

int main(void)
{
        static Screen a, b;

        puts("екран 80×24, ціна оновлення в байтах\n");

        build(&a, 100, "12:04:59", 41);
        build(&b, 100, "12:04:59", 42);
        measure("лічильник 41 → 42", &a, &b);

        build(&a, 100, "12:04:59", 41);
        build(&b, 100, "12:05:00", 41);
        measure("годинник 04:59 → 05:00", &a, &b);

        build(&a, 100, "12:04:59", 41);
        build(&b, 101, "12:04:59", 41);
        measure("список поїхав на рядок", &a, &b);
        return 0;
}
