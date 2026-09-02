/* stream.h — конвеєрний прогін: буферизація вводу й виводу, SIGPIPE,
   ранній вихід за командою q. */
#ifndef STREAM_H
#define STREAM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

#include "sedbuf.h"
#include "subst.h"

typedef struct {
    bool   unbuffered;   /* -u: віддавати кожен запис негайно */
    bool   quiet;        /* -n */
    int    record_sep;   /* '\n' або '\0' для -z */
    size_t quit_after;   /* Nq: 0 — читати до кінця */
} SedStreamOpts;

/* Викликати ДО першого виводу: setvbuf після початку запису вже безсилий. */
void sed_stream_setup_output(const SedStreamOpts *o, FILE *out);
/* Викликати ДО першого читання. */
void sed_stream_setup_input(const SedStreamOpts *o, FILE *in);

/* Код виходу процесу: 0 — успіх, 2 — введення/виведення, 141 — обірваний
   канал (128 + SIGPIPE). quit_requested ставиться командою q. */
int sed_stream_run(SedState *st, const SedSubst *subst, FILE *in, FILE *out,
                   const SedStreamOpts *o, bool *quit_requested);

#endif /* STREAM_H */
