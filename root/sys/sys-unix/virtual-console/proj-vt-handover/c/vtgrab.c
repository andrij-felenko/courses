/* vtgrab.c — забрати вільну віртуальну консоль і коректно її віддати.
   Збірка: cc -O2 -Wall -o vtgrab vtgrab.c
   Запуск: sudo ./vtgrab   — краще по мережі, бо екран консолі буде порожній */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kd.h>
#include <linux/vt.h>

static volatile sig_atomic_t got_rel, got_acq, got_quit;

static int vtfd = -1, vtnum = -1, prev_vt = -1;
static int have_mode, have_gfx;

static void handler(int sig)
{
    if (sig == SIGRTMIN)          got_rel = 1;   /* «віддай екран» */
    else if (sig == SIGRTMIN + 1) got_acq = 1;   /* «екран знову твій» */
    else                          got_quit = 1;  /* SIGINT або SIGTERM */
}

/* Викликається з atexit(), тобто й на аварійному виході через die(). */
static void restore(void)
{
    if (vtfd < 0)
        return;
    if (have_gfx)                                /* спершу повертаємо текст… */
        ioctl(vtfd, KDSETMODE, KD_TEXT);
    if (have_mode) {                             /* …і тільки потім автомат */
        struct vt_mode m = { .mode = VT_AUTO };
        ioctl(vtfd, VT_SETMODE, &m);
    }
    if (prev_vt > 0)
        ioctl(vtfd, VT_ACTIVATE, prev_vt);
    close(vtfd);
    vtfd = -1;
}

static void die(const char *what)
{
    fprintf(stderr, "%s: %s\n", what, strerror(errno));
    exit(1);                                     /* atexit() поверне консоль */
}

int main(void)
{
    char path[32];
    struct vt_stat st;
    struct vt_mode vm;
    struct sigaction sa;
    sigset_t block, prev;
    int ctl;

    ctl = open("/dev/tty0", O_RDWR | O_NOCTTY);  /* «та консоль, що на екрані» */
    if (ctl < 0) die("open /dev/tty0");
    if (ioctl(ctl, VT_GETSTATE, &st) < 0) die("VT_GETSTATE");
    prev_vt = st.v_active;                       /* куди повертатися на виході */
    if (ioctl(ctl, VT_OPENQRY, &vtnum) < 0 || vtnum < 0) die("VT_OPENQRY");
    close(ctl);

    snprintf(path, sizeof path, "/dev/tty%d", vtnum);
    vtfd = open(path, O_RDWR | O_NOCTTY);
    if (vtfd < 0) die(path);
    atexit(restore);

    /* Блокуємо сигнали ДО того, як вони можуть прийти: прапорець і перевірку
       прапорця не можна лишати без захисту, інакше сигнал прослизне між ними. */
    sigemptyset(&block);
    sigaddset(&block, SIGRTMIN);
    sigaddset(&block, SIGRTMIN + 1);
    sigaddset(&block, SIGINT);
    sigaddset(&block, SIGTERM);
    if (sigprocmask(SIG_BLOCK, &block, &prev) < 0) die("sigprocmask");

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = handler;
    sa.sa_mask = block;              /* обробника не перерве інший обробник */
    sigaction(SIGRTMIN, &sa, NULL);
    sigaction(SIGRTMIN + 1, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    if (ioctl(vtfd, VT_ACTIVATE, vtnum) < 0) die("VT_ACTIVATE");
    if (ioctl(vtfd, VT_WAITACTIVE, vtnum) < 0) die("VT_WAITACTIVE");

    memset(&vm, 0, sizeof vm);
    vm.mode = VT_PROCESS;
    vm.waitv = 0;
    vm.relsig = SIGRTMIN;
    vm.acqsig = SIGRTMIN + 1;
    if (ioctl(vtfd, VT_SETMODE, &vm) < 0) die("VT_SETMODE");
    have_mode = 1;

    if (ioctl(vtfd, KDSETMODE, KD_GRAPHICS) < 0) die("KDSETMODE");
    have_gfx = 1;
    fprintf(stderr, "тримаю /dev/tty%d, Alt+F%d поверне назад\n", vtnum, prev_vt);

    for (;;) {
        while (!got_rel && !got_acq && !got_quit)
            sigsuspend(&prev);       /* сигнали розблоковано лише всередині */

        if (got_rel) {
            got_rel = 0;
            fprintf(stderr, "просять віддати\n");
            /* Тут — справжня робота: зняти з себе право розпоряджатися
               графічним пристроєм і дочекатися, поки залізо справді вільне. */
            if (ioctl(vtfd, VT_RELDISP, 1) < 0)          /* 1 — «віддаю» */
                perror("VT_RELDISP");
        }
        if (got_acq) {
            got_acq = 0;
            fprintf(stderr, "екран повернули\n");
            /* Забрати пристрій назад, поставити свій відеорежим, перемалювати. */
            if (ioctl(vtfd, VT_RELDISP, VT_ACKACQ) < 0)
                perror("VT_RELDISP ack");
        }
        if (got_quit)
            break;
    }
    return 0;                        /* restore() з atexit() зробить решту */
}
