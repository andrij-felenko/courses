#define _GNU_SOURCE
#include "pipeline.h"
#include "jobs.h"
#include "launch.h"
#include "spawn_stage.h"

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int run_pipeline(const struct pipeline_spec *spec)
{
    sigset_t saved;
    struct job *job;
    int in_fd = STDIN_FILENO;
    pid_t pgid = 0;
    int rc = 0;

    if (spec->nstages <= 0) {
        return 0;
    }

    /* Нащадок може завершитися раніше, ніж потрапить у таблицю завдань,
     * тому SIGCHLD блокуємо на весь час побудови конвеєра. */
    jobs_block_sigchld(&saved);

    job = job_new(spec->foreground, spec->text);
    if (job == NULL) {
        jobs_restore_mask(&saved);
        fprintf(stderr, "конвеєр: таблиця завдань переповнена\n");
        return 1;
    }

    for (int i = 0; i < spec->nstages; i++) {
        const bool last = (i == spec->nstages - 1);
        int pfd[2] = { -1, -1 };
        int file_fd = -1;
        int out_fd = STDOUT_FILENO;
        int closes[3];
        int nclose = 0;
        pid_t pid;

        if (!last) {
            /* O_CLOEXEC ставить саме ядро, у момент створення дескрипторів:
             * вікна між pipe() та fcntl(), крізь яке чужий execve()
             * успадкував би кінець запису, більше немає. */
            if (pipe2(pfd, O_CLOEXEC) < 0) {
                perror("pipe2");
                rc = 1;
                break;
            }
            out_fd = pfd[1];
        } else if (spec->outfile != NULL) {
            const int flags = O_WRONLY | O_CREAT | O_CLOEXEC
                            | (spec->append ? O_APPEND : O_TRUNC);
            file_fd = open(spec->outfile, flags, 0644);
            if (file_fd < 0) {
                perror(spec->outfile);
                rc = 1;
                break;
            }
            out_fd = file_fd;
        }

        if (in_fd != STDIN_FILENO) {
            closes[nclose++] = in_fd;
        }
        if (pfd[0] >= 0) {
            closes[nclose++] = pfd[0];
        }
        if (pfd[1] >= 0) {
            closes[nclose++] = pfd[1];
        }

        if (spec->use_spawn) {
            struct spawn_io io = { in_fd, out_fd, closes, nclose, pgid };
            pid = spawn_pipeline_stage(spec->stages[i][0], spec->stages[i], &io);
            if (pid < 0) {
                fprintf(stderr, "%s: %s\n", spec->stages[i][0], strerror(errno));
            }
        } else {
            struct launch_ctx ctx;
            memset(&ctx, 0, sizeof ctx);
            ctx.argv = spec->stages[i];
            ctx.in_fd = in_fd;
            ctx.out_fd = out_fd;
            ctx.close_fds = closes;
            ctx.nclose = nclose;
            ctx.pgid = pgid;
            ctx.foreground = spec->foreground;
            ctx.tty_fd = jobs_tty_fd();
            pid = launch_stage(&ctx);
        }

        /* Свої копії батько закриває ЗАВЖДИ: поки живий бодай один
         * дескриптор запису, читач наступної ланки не побачить EOF. */
        if (in_fd != STDIN_FILENO) {
            close(in_fd);
        }
        if (pfd[1] >= 0) {
            close(pfd[1]);
        }
        if (file_fd >= 0) {
            close(file_fd);
        }

        if (pid < 0) {
            if (pfd[0] >= 0) {
                close(pfd[0]);
            }
            rc = 1;
            break;
        }

        if (pgid == 0) {
            pgid = pid;            /* лідером групи стає перший процес конвеєра */
        }
        job_add_proc(job, pid);
        in_fd = (pfd[0] >= 0) ? pfd[0] : STDIN_FILENO;
    }

    if (in_fd != STDIN_FILENO) {
        close(in_fd);
    }

    if (job->nprocs == 0) {
        job_drop(job);
        jobs_restore_mask(&saved);
        return 1;
    }

    /* Шлях через posix_spawn не має батьківської половини launch_stage,
     * тож термінал завданню віддаємо тут. */
    if (spec->use_spawn && spec->foreground) {
        give_terminal_to(job->pgid);
    }
    jobs_restore_mask(&saved);

    if (spec->foreground) {
        const int code = job_wait_foreground(job);
        return (rc == 0) ? code : 1;
    }

    fprintf(stderr, "[%d] %ld\n", job->id, (long)job->pgid);
    return rc;
}
