/* Побудова конвеєра: канали, перенаправлення, спільна група процесів. */
#ifndef PIPELINE_H
#define PIPELINE_H

#include <stdbool.h>

struct pipeline_spec {
    char *const *const *stages;   /* масив NULL-термінованих argv */
    int nstages;
    const char *outfile;          /* NULL — stdout лишається терміналом */
    bool append;
    bool foreground;
    bool use_spawn;               /* posix_spawn замість fork+exec */
    const char *text;             /* підпис завдання для jobs */
};

/* Повертає код виходу конвеєра (для пріоритетного завдання). */
int run_pipeline(const struct pipeline_spec *spec);

#endif /* PIPELINE_H */
