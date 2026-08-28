/* journal-forward.c — читач журналу, що продовжує з того самого місця.
   cc journal-forward.c $(pkg-config --cflags --libs libsystemd) -o journal-forward */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <systemd/sd-journal.h>

#define STATE_FILE "/var/lib/journal-forward/cursor"
#define BACKLOG    100u          /* скільки минулих записів показати на першому запуску */

/* ── курсор на диску: спершу в сусідній файл, потім перейменування ────────── */
static int cursor_save(const char *cursor) {
        char tmp[] = STATE_FILE ".XXXXXX";
        int r = 0;

        int fd = mkostemp(tmp, O_CLOEXEC);
        if (fd < 0)
                return -errno;

        size_t len = strlen(cursor);
        if (write(fd, cursor, len) != (ssize_t) len || fsync(fd) < 0)
                r = -errno;
        close(fd);

        if (r == 0 && rename(tmp, STATE_FILE) < 0)
                r = -errno;
        if (r < 0)
                unlink(tmp);
        return r;
}

static char *cursor_load(void) {
        FILE *f = fopen(STATE_FILE, "re");
        if (!f)
                return NULL;

        char *line = NULL;
        size_t n = 0;
        ssize_t got = getline(&line, &n, f);
        fclose(f);

        if (got <= 0) {
                free(line);
                return NULL;
        }
        line[strcspn(line, "\n")] = '\0';
        return line;
}

/* ── добір: (nginx АБО postgresql) І (важливість 0…3) ─────────────────────── */
static int add_matches(sd_journal *j) {
        static const char *const units[] = {
                "_SYSTEMD_UNIT=nginx.service",
                "_SYSTEMD_UNIT=postgresql.service",
        };
        int r;

        for (size_t i = 0; i < sizeof units / sizeof *units; i++) {
                r = sd_journal_add_match(j, units[i], 0);   /* 0 — довжину візьме strlen */
                if (r < 0)
                        return r;
        }
        for (int prio = 0; prio <= 3; prio++) {
                char m[32];
                snprintf(m, sizeof m, "PRIORITY=%d", prio);
                r = sd_journal_add_match(j, m, 0);
                if (r < 0)
                        return r;
        }
        return 0;
}

/* ── значення поля КОПІЮЄМО: вказівник від get_data живе лише до
      наступного звертання до журналу ─────────────────────────────────────── */
static int field_copy(sd_journal *j, const char *name,
                      char *buf, size_t cap, size_t *len) {
        const void *d;
        size_t l, prefix = strlen(name) + 1;    /* бібліотека віддає «ІМ'Я=значення» */

        int r = sd_journal_get_data(j, name, &d, &l);
        if (r < 0)
                return r;                       /* -ENOENT — поля в записі просто немає */
        if (l < prefix)
                return -EBADMSG;

        l -= prefix;
        if (l > cap)
                l = cap;                        /* обрізаємо, а не псуємо пам'ять */
        memcpy(buf, (const char *) d + prefix, l);
        *len = l;
        return 0;
}

static int printable(const char *s, size_t n) {
        for (size_t i = 0; i < n; i++)
                if ((unsigned char) s[i] < 0x20 && s[i] != '\t')
                        return 0;
        return 1;
}

static void handle(sd_journal *j) {
        char unit[64] = "?", msg[8192], when[32] = "невідомо";
        size_t unit_len = 1, msg_len = 0;
        uint64_t usec = 0;

        if (sd_journal_get_realtime_usec(j, &usec) >= 0) {
                time_t t = (time_t) (usec / 1000000);
                struct tm tm;
                if (gmtime_r(&t, &tm))
                        strftime(when, sizeof when, "%Y-%m-%dT%H:%M:%S", &tm);
        }
        field_copy(j, "_SYSTEMD_UNIT", unit, sizeof unit, &unit_len);
        field_copy(j, "MESSAGE", msg, sizeof msg, &msg_len);

        if (printable(msg, msg_len))
                printf("%s.%06u  %.*s  %.*s\n", when, (unsigned) (usec % 1000000),
                       (int) unit_len, unit, (int) msg_len, msg);
        else
                printf("%s.%06u  %.*s  <%zu двійкових байтів>\n", when,
                       (unsigned) (usec % 1000000), (int) unit_len, unit, msg_len);
}

/* ── місце старту. on_entry == 1: покажчик УЖЕ стоїть на записі,
      який належить обробити, — тобто перший next() робити не треба ────────── */
static int position(sd_journal *j, const char *cursor, int *on_entry) {
        int r;

        *on_entry = 0;

        if (!cursor) {                                  /* перший запуск за життя */
                r = sd_journal_seek_tail(j);
                if (r < 0)
                        return r;
                r = sd_journal_previous_skip(j, BACKLOG);
                if (r < 0)
                        return r;
                *on_entry = r > 0;                      /* r — скільки реально відступили */
                return 0;
        }

        r = sd_journal_seek_cursor(j, cursor);
        if (r < 0)
                return r;
        r = sd_journal_next(j);                         /* seek навів, next ставить */
        if (r < 0)
                return r;
        if (r == 0)
                return 0;                               /* ставати нема на що — чекаємо */

        if (sd_journal_test_cursor(j, cursor) > 0)
                return 0;                               /* той самий запис, уже оброблений */

        fprintf(stderr, "збережений запис уже прибрано — можливий пропуск\n");
        *on_entry = 1;                                  /* стоїмо на необробленому */
        return 0;
}

int main(void) {
        sd_journal *j = NULL;
        char *cursor = cursor_load();
        int on_entry = 0, r;

        r = sd_journal_open(&j, SD_JOURNAL_LOCAL_ONLY | SD_JOURNAL_SYSTEM);
        if (r < 0)
                goto fail;

        sd_journal_set_data_threshold(j, 0);    /* інакше довгі значення мовчки обріже */

        r = add_matches(j);
        if (r < 0)
                goto fail;
        r = position(j, cursor, &on_entry);
        if (r < 0)
                goto fail;

        for (;;) {
                if (on_entry)
                        on_entry = 0;                   /* запис уже під пальцем */
                else {
                        r = sd_journal_next(j);
                        if (r < 0)
                                goto fail;
                        if (r == 0) {                   /* кінець — засинаємо до змін */
                                r = sd_journal_wait(j, (uint64_t) -1);
                                if (r < 0)
                                        goto fail;
                                if (r == SD_JOURNAL_INVALIDATE && cursor) {
                                        r = position(j, cursor, &on_entry);
                                        if (r < 0)
                                                goto fail;
                                }
                                continue;
                        }
                }

                handle(j);                              /* тут запис іде споживачеві */

                free(cursor);
                cursor = NULL;
                r = sd_journal_get_cursor(j, &cursor);  /* і лише ПІСЛЯ цього — курсор */
                if (r < 0)
                        goto fail;
                r = cursor_save(cursor);
                if (r < 0)
                        fprintf(stderr, "курсор не збережено: %s\n", strerror(-r));
        }

fail:
        fprintf(stderr, "журнал: %s\n", strerror(-r));
        sd_journal_close(j);
        free(cursor);
        return 1;
}
