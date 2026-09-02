/* main.c — mini-sed: навчальний потоковий редактор з однією командою s///.
 *
 * Збірка:  cc -std=c11 -O2 -Wall -Wextra -o mini-sed *.c
 *          (з мітками SELinux: cc -DSED_WITH_SELINUX … -lselinux)
 *
 * Виклик:  mini-sed [-n] [-u] [-z] [-E] [-i[СУФ]] [--follow-symlinks] [-q N]
 *                   's/RE/REP/ПРАПОРЦІ' [файл…]
 *
 * Коди виходу — ті самі, що в sed: 0 успіх · 1 синтаксис сценарію ·
 * 2 введення/виведення · 141 обірваний канал. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "inplace.h"
#include "sedbuf.h"
#include "stream.h"
#include "subst.h"

static void usage(void) {
    fputs("виклик: mini-sed [-n] [-u] [-z] [-E] [-i[СУФ]] [--follow-symlinks]"
          " [-q N] 's/RE/REP/ПРАПОРЦІ' [файл…]\n", stderr);
}

/* Режим -i збирає весь результат у пам'яті: писати у вхідний файл під час
   читання не можна, а тимчасова копія все одно потрібна для rename(). */
static int transform_to_buffer(FILE *in, SedState *st, const SedSubst *subst,
                               const SedStreamOpts *o, SedBuffer *out) {
    st->line_number = 0;
    st->is_last_line = false;
    while (sed_read_record(st, in, o->record_sep)) {
        bool changed = sed_subst_apply(subst, &st->pattern_space);
        if (!o->quiet) {
            sedbuf_append(out, st->pattern_space.data, st->pattern_space.len);
            sedbuf_append_byte(out, (char)o->record_sep);
        }
        if (changed && subst->print) {
            sedbuf_append(out, st->pattern_space.data, st->pattern_space.len);
            sedbuf_append_byte(out, (char)o->record_sep);
        }
        if (o->quit_after && st->line_number >= o->quit_after) break;
    }
    return ferror(in) ? 2 : 0;
}

int main(int argc, char **argv) {
    SedStreamOpts opts = { .unbuffered = false, .quiet = false,
                           .record_sep = '\n', .quit_after = 0 };
    bool extended = false, inplace = false, follow = false;
    const char *backup = NULL;
    int i = 1;

    for (; i < argc && argv[i][0] == '-' && argv[i][1]; ++i) {
        const char *a = argv[i];
        if (strcmp(a, "--") == 0) { ++i; break; }
        if (strcmp(a, "--follow-symlinks") == 0) { follow = true; continue; }
        if (strncmp(a, "-i", 2) == 0) {          /* суфікс пишеться злито: -i.bak */
            inplace = true;
            backup = a[2] ? a + 2 : NULL;
            continue;
        }
        if (strcmp(a, "-q") == 0) {
            if (++i >= argc) { usage(); return 1; }
            opts.quit_after = strtoul(argv[i], NULL, 10);
            continue;
        }
        if (a[1] == '-') {
            fprintf(stderr, "mini-sed: невідома опція %s\n", a);
            usage();
            return 1;
        }
        for (const char *f = a + 1; *f; ++f) {
            switch (*f) {
                case 'n': opts.quiet = true; break;
                case 'u': opts.unbuffered = true; break;
                case 'z': opts.record_sep = '\0'; break;
                case 'E': case 'r': extended = true; break;
                default:
                    fprintf(stderr, "mini-sed: невідома опція -%c\n", *f);
                    usage();
                    return 1;
            }
        }
    }
    if (i >= argc) { usage(); return 1; }

    SedSubst subst;
    char err[320];
    if (!sed_subst_compile(&subst, argv[i++], extended, err, sizeof err)) {
        fprintf(stderr, "mini-sed: %s\n", err);
        return 1;                                 /* синтаксична помилка сценарію */
    }

    SedState st;
    sed_state_init(&st);
    int status = 0;

    if (inplace) {
        if (i >= argc) {
            fprintf(stderr, "mini-sed: -i вимагає імені файла\n");
            status = 1;
        }
        for (; i < argc; ++i) {
            FILE *in = fopen(argv[i], "rb");
            if (!in) {
                fprintf(stderr, "mini-sed: %s: %s\n", argv[i], strerror(errno));
                status = 2;
                continue;
            }
            SedBuffer out;
            sedbuf_init(&out);
            int rc = transform_to_buffer(in, &st, &subst, &opts, &out);
            fclose(in);
            if (rc == 0) {
                SedInplaceOpts io = { backup, follow };
                if (sed_inplace_commit(argv[i], out.data ? out.data : "", out.len, &io) != 0) {
                    fprintf(stderr, "mini-sed: %s: %s\n", argv[i], strerror(errno));
                    rc = 2;
                }
            }
            sedbuf_free(&out);
            if (rc) status = rc;
        }
    } else {
        sed_stream_setup_output(&opts, stdout);
        bool quit = false;
        if (i >= argc) {
            status = sed_stream_run(&st, &subst, stdin, stdout, &opts, &quit);
        } else {
            for (; i < argc && !quit; ++i) {
                FILE *in = strcmp(argv[i], "-") ? fopen(argv[i], "rb") : stdin;
                if (!in) {
                    fprintf(stderr, "mini-sed: %s: %s\n", argv[i], strerror(errno));
                    status = 2;
                    continue;
                }
                int rc = sed_stream_run(&st, &subst, in, stdout, &opts, &quit);
                if (in != stdin) fclose(in);
                if (rc) { status = rc; break; }
            }
        }
        if (fflush(stdout) != 0 && status == 0)
            status = (errno == EPIPE) ? 141 : 2;
    }

    sed_state_free(&st);
    sed_subst_free(&subst);
    return status;
}
