#include "stream.h"

#include <errno.h>
#include <signal.h>
#include <string.h>

/* Обробник має право чіпати лише sig_atomic_t. */
static volatile sig_atomic_t g_pipe_broken = 0;

static void handle_sigpipe(int sig) {
    (void)sig;
    g_pipe_broken = 1;
}

static void install_sigpipe_handler(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = handle_sigpipe;
    sigemptyset(&sa.sa_mask);
    /* SA_RESTART навмисно не ставимо: write() мусить повернутись із EPIPE,
       щоб обірваний канал був звичайним кінцем роботи, а не аварією. */
    sigaction(SIGPIPE, &sa, NULL);
}

void sed_stream_setup_output(const SedStreamOpts *o, FILE *out) {
    static char block_buf[8192];
    if (o->unbuffered) {
        /* Затримка нуль, ціна — системний виклик write() на кожен запис. */
        setvbuf(out, NULL, _IONBF, 0);
    } else {
        /* За замовчуванням stdio і сам обрав би _IOFBF для каналу; робимо це
           явно, щоб розмір блоку не залежав від реалізації бібліотеки. */
        setvbuf(out, block_buf, _IOFBF, sizeof block_buf);
    }
}

void sed_stream_setup_input(const SedStreamOpts *o, FILE *in) {
    if (!o->unbuffered) return;
    /* З каналу read(2) і так віддає стільки, скільки вже прийшло. Вимкнення
       буфера прибирає жадібне попереднє зчитування цілого блока з РЕГУЛЯРНОГО
       файла — а з ним і зайві байти, прочитані перед раннім виходом за q. */
    setvbuf(in, NULL, _IONBF, 0);
}

int sed_stream_run(SedState *st, const SedSubst *subst, FILE *in, FILE *out,
                   const SedStreamOpts *o, bool *quit_requested) {
    install_sigpipe_handler();
    sed_stream_setup_input(o, in);
    st->line_number = 0;
    st->is_last_line = false;

    while (sed_read_record(st, in, o->record_sep)) {
        st->subst_success = subst ? sed_subst_apply(subst, &st->pattern_space) : false;

        if (!o->quiet) sed_print(st, out, o->record_sep);
        /* Прапорець p друкує ще раз — без -n рядок і справді виходить двічі. */
        if (st->subst_success && subst->print) sed_print(st, out, o->record_sep);
        if (o->unbuffered) fflush(out);

        if (ferror(out)) {
            if (g_pipe_broken || errno == EPIPE) return 141;
            fprintf(stderr, "mini-sed: помилка запису: %s\n", strerror(errno));
            return 2;
        }
        /* Команда q: запис уже надрукований, далі вхід не читаємо взагалі —
           виробник вище по конвеєру дістане SIGPIPE і теж зупиниться. */
        if (o->quit_after && st->line_number >= o->quit_after) {
            *quit_requested = true;
            break;
        }
    }

    if (ferror(in)) {
        fprintf(stderr, "mini-sed: помилка читання: %s\n", strerror(errno));
        return 2;
    }
    return g_pipe_broken ? 141 : 0;
}
