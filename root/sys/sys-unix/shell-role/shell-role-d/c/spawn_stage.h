/* Запуск ланки конвеєра через posix_spawn(3) — без ручного fork(). */
#ifndef SPAWN_STAGE_H
#define SPAWN_STAGE_H

#include <sys/types.h>

struct spawn_io {
    int in_fd;
    int out_fd;
    const int *close_fds;
    int nclose;
    pid_t pgid;             /* 0 — нащадок стає лідером власної групи */
};

/* Повертає PID нащадка або -1, виставивши errno. */
pid_t spawn_pipeline_stage(const char *path, char *const argv[],
                           const struct spawn_io *io);

#endif /* SPAWN_STAGE_H */
