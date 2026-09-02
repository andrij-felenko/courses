#define _GNU_SOURCE
#include "jobs.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <sys/wait.h>

static struct job g_jobs[JOBS_MAX];
static int   g_next_id = 1;
static int   g_tty = -1;
static pid_t g_shell_pgid = -1;
static struct termios g_shell_modes;
static bool  g_have_modes = false;

static void sigchld_handler(int sig)
{
    (void)sig;
    /* Обробник не має права зіпсувати errno основного потоку виконання. */
    const int saved_errno = errno;
    int status;
    pid_t pid;

    /* WNOHANG не дає заблокувати оболонку; WUNTRACED і WCONTINUED
     * приносять ще й зупинку (Ctrl+Z) та відновлення (SIGCONT). */
    while ((pid = waitpid(-1, &status, WNOHANG | WUNTRACED | WCONTINUED)) > 0) {
        update_job_status(pid, status);
    }
    errno = saved_errno;
}

void jobs_init(int tty_fd)
{
    struct sigaction sa;

    g_shell_pgid = getpgrp();

    /* Поки оболонка сама роздає термінал, ці сигнали зупинили б її саму:
     * tcsetpgrp() з фонової групи негайно повертає SIGTTOU. */
    signal(SIGTTOU, SIG_IGN);
    signal(SIGTTIN, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);
    signal(SIGINT,  SIG_IGN);
    signal(SIGQUIT, SIG_IGN);

    if (tty_fd >= 0 && isatty(tty_fd)) {
        g_tty = tty_fd;
        if (tcgetattr(g_tty, &g_shell_modes) == 0) {
            g_have_modes = true;
        }
        /* Оболонка мусить володіти терміналом, інакше tcsetpgrp()
         * для завдання поверне EPERM. */
        if (tcsetpgrp(g_tty, g_shell_pgid) < 0 && errno != ENOTTY) {
            perror("tcsetpgrp(оболонка)");
        }
    } else {
        g_tty = -1;                /* неінтерактивний запуск: завдань не ведемо */
    }

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;      /* SA_NOCLDSTOP не ставимо: зупинки нам потрібні */
    if (sigaction(SIGCHLD, &sa, NULL) < 0) {
        perror("sigaction(SIGCHLD)");
    }
}

int jobs_tty_fd(void)
{
    return g_tty;
}

struct job *job_new(bool foreground, const char *text)
{
    for (int i = 0; i < JOBS_MAX; i++) {
        if (g_jobs[i].used) {
            continue;
        }
        memset(&g_jobs[i], 0, sizeof g_jobs[i]);
        g_jobs[i].used = true;
        g_jobs[i].id = g_next_id++;
        g_jobs[i].foreground = foreground;
        if (text != NULL) {
            snprintf(g_jobs[i].text, sizeof g_jobs[i].text, "%s", text);
        }
        return &g_jobs[i];
    }
    return NULL;
}

void job_drop(struct job *j)
{
    if (j != NULL) {
        j->used = false;
    }
}

bool job_add_proc(struct job *j, pid_t pid)
{
    if (j->nprocs >= JOB_PROCS_MAX) {
        return false;
    }
    if (j->pgid == 0) {
        j->pgid = pid;             /* перший процес конвеєра — лідер групи */
    }
    j->procs[j->nprocs].pid = pid;
    j->procs[j->nprocs].state = PROC_RUNNING;
    j->procs[j->nprocs].status = 0;
    j->nprocs++;
    return true;
}

void update_job_status(pid_t pid, int status)
{
    for (int i = 0; i < JOBS_MAX; i++) {
        if (!g_jobs[i].used) {
            continue;
        }
        for (int k = 0; k < g_jobs[i].nprocs; k++) {
            struct proc *p = &g_jobs[i].procs[k];
            if (p->pid != pid) {
                continue;
            }
            p->status = status;
            if (WIFSTOPPED(status)) {
                p->state = PROC_STOPPED;
            } else if (WIFCONTINUED(status)) {
                p->state = PROC_RUNNING;
            } else {
                p->state = PROC_DONE;
            }
            return;
        }
    }
}

bool job_is_done(const struct job *j)
{
    for (int k = 0; k < j->nprocs; k++) {
        if (j->procs[k].state != PROC_DONE) {
            return false;
        }
    }
    return true;
}

bool job_is_stopped(const struct job *j)
{
    bool any_stopped = false;

    for (int k = 0; k < j->nprocs; k++) {
        if (j->procs[k].state == PROC_RUNNING) {
            return false;
        }
        if (j->procs[k].state == PROC_STOPPED) {
            any_stopped = true;
        }
    }
    return any_stopped;
}

void jobs_block_sigchld(sigset_t *saved)
{
    sigset_t mask;

    sigemptyset(&mask);
    sigaddset(&mask, SIGCHLD);
    sigprocmask(SIG_BLOCK, &mask, saved);
}

void jobs_restore_mask(const sigset_t *saved)
{
    sigprocmask(SIG_SETMASK, saved, NULL);
}

void give_terminal_to(pid_t pgid)
{
    if (g_tty >= 0 && pgid > 0) {
        tcsetpgrp(g_tty, pgid);
    }
}

void take_terminal_back(void)
{
    if (g_tty < 0) {
        return;
    }
    tcsetpgrp(g_tty, g_shell_pgid);
    /* Завдання могло лишити термінал у неканонічному режимі
     * (редактор, pager), тож режим оболонки відновлюємо явно. */
    if (g_have_modes) {
        tcsetattr(g_tty, TCSADRAIN, &g_shell_modes);
    }
}

int job_wait_foreground(struct job *j)
{
    sigset_t prev, idle;
    int status;

    jobs_block_sigchld(&prev);
    idle = prev;
    sigdelset(&idle, SIGCHLD);     /* sigsuspend має ПРОПУСКАТИ SIGCHLD */

    while (!job_is_done(j) && !job_is_stopped(j)) {
        sigsuspend(&idle);         /* атомарно: відпустити сигнал і заснути */
    }
    jobs_restore_mask(&prev);

    take_terminal_back();

    if (job_is_stopped(j)) {
        fprintf(stderr, "[%d]  Зупинено   %s\n", j->id, j->text);
        j->foreground = false;
        j->notified = true;
        return 128 + SIGTSTP;
    }

    status = j->procs[j->nprocs - 1].status;
    job_drop(j);
    if (WIFSIGNALED(status)) {
        return 128 + WTERMSIG(status);
    }
    return WIFEXITED(status) ? WEXITSTATUS(status) : 0;
}

bool jobs_any_active(void)
{
    for (int i = 0; i < JOBS_MAX; i++) {
        if (g_jobs[i].used && !job_is_done(&g_jobs[i])) {
            return true;
        }
    }
    return false;
}

void jobs_report(void)
{
    sigset_t prev;

    jobs_block_sigchld(&prev);
    for (int i = 0; i < JOBS_MAX; i++) {
        struct job *j = &g_jobs[i];

        if (!j->used || j->foreground) {
            continue;
        }
        if (job_is_done(j)) {
            int status = j->procs[j->nprocs - 1].status;
            int code = WIFEXITED(status) ? WEXITSTATUS(status)
                                         : 128 + WTERMSIG(status);
            fprintf(stderr, "[%d]  Завершено (%d)  %s\n", j->id, code, j->text);
            job_drop(j);
        } else if (job_is_stopped(j) && !j->notified) {
            fprintf(stderr, "[%d]  Зупинено   %s\n", j->id, j->text);
            j->notified = true;
        }
    }
    jobs_restore_mask(&prev);
}

void jobs_wait_all(void)
{
    sigset_t prev, idle;

    jobs_block_sigchld(&prev);
    idle = prev;
    sigdelset(&idle, SIGCHLD);
    while (jobs_any_active()) {
        sigsuspend(&idle);
    }
    jobs_restore_mask(&prev);
}
