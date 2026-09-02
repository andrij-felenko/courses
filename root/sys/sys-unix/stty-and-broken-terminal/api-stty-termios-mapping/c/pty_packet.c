#include "pty_packet.h"

#include "tty_input.h"
#include "tty_session.h"
#include "tty_signals.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

struct master_ctx {
    int master;
    int flow_stopped;   /* ведений сказав STOP — не пхаємо в нього ввід */
    int eof;
};

/* Геометрію ведучого термінала переносимо на ведений: без цього
   програма всередині PTY вважає, що екран 80x24. */
static void copy_winsize(int from, int to)
{
    struct winsize ws;

    if (ioctl(from, TIOCGWINSZ, &ws) == 0)
        (void)ioctl(to, TIOCSWINSZ, &ws);
}

static void report_queues(int master)
{
    int in = -1, out = -1;

    /* Скільки байтів можна прочитати без блокування і скільки ще
       не пішло в лінію — обидва лічильники ядрові. */
    if (ioctl(master, FIONREAD, &in) < 0)
        in = -1;
    if (ioctl(master, TIOCOUTQ, &out) < 0)
        out = -1;
    fprintf(stderr, "\r\n[pty] FIONREAD = %d, TIOCOUTQ = %d\r\n", in, out);
}

static void report_slave_termios(int master)
{
    struct termios t;

    /* На ведучому дескрипторі TCGETS віддає termios веденого боку —
       саме це й треба перечитати після пакета TIOCPKT_IOCTL. */
    if (tcgetattr(master, &t) < 0) {
        fprintf(stderr, "\r\n[pty] tcgetattr(master): %s\r\n", strerror(errno));
        return;
    }
    fprintf(stderr,
            "\r\n[pty] termios веденого змінено: iflag=0x%08lx oflag=0x%08lx "
            "lflag=0x%08lx (echo %s, icanon %s)\r\n",
            (unsigned long)t.c_iflag, (unsigned long)t.c_oflag,
            (unsigned long)t.c_lflag,
            (t.c_lflag & ECHO) ? "є" : "нема",
            (t.c_lflag & ICANON) ? "є" : "нема");
}

/* Кожен read() із ведучого дескриптора в пакетному режимі повертає
   пакет, і найперший його байт — байт стану. */
static void on_master_packet(const unsigned char *pkt, size_t len, void *user)
{
    struct master_ctx *m = user;
    unsigned char ctl;

    if (len == 0)
        return;
    ctl = pkt[0];

    if (ctl == TIOCPKT_DATA) {
        /* Нуль у першому байті — далі звичайні вихідні дані веденого. */
        if (len > 1 && tty_write_all(STDOUT_FILENO, pkt + 1, len - 1) < 0)
            perror("write(stdout)");
        return;
    }

    /* Ненульовий байт стану приходить сам-один: це подія лінії. */
    if (ctl & TIOCPKT_FLUSHREAD) {
        fprintf(stderr, "\r\n[pty] FLUSHREAD: вхідну чергу веденого скинуто\r\n");
        report_queues(m->master);
    }
    if (ctl & TIOCPKT_FLUSHWRITE)
        fprintf(stderr, "\r\n[pty] FLUSHWRITE: вихідну чергу веденого скинуто\r\n");
    if (ctl & TIOCPKT_STOP) {
        m->flow_stopped = 1;   /* ^S: далі не наливаємо в нього ввід */
        fprintf(stderr, "\r\n[pty] STOP: вивід зупинено (^S)\r\n");
    }
    if (ctl & TIOCPKT_START) {
        m->flow_stopped = 0;
        fprintf(stderr, "\r\n[pty] START: вивід поновлено (^Q)\r\n");
    }
    if (ctl & TIOCPKT_NOSTOP)
        fprintf(stderr, "\r\n[pty] NOSTOP: ^S/^Q більше не керують потоком\r\n");
    if (ctl & TIOCPKT_DOSTOP)
        fprintf(stderr, "\r\n[pty] DOSTOP: ^S/^Q знову стандартні\r\n");
#ifdef TIOCPKT_IOCTL
    if (ctl & TIOCPKT_IOCTL)
        report_slave_termios(m->master);
#endif
}

static void on_stdin_chunk(const unsigned char *chunk, size_t len, void *user)
{
    struct master_ctx *m = user;

    if (tty_write_all(m->master, chunk, len) < 0)
        perror("write(master)");
}

static int open_master(char *slave_name, size_t size)
{
    int master = posix_openpt(O_RDWR | O_NOCTTY);
    int mode = 1;

    if (master < 0) {
        perror("posix_openpt");
        return -1;
    }
    if (grantpt(master) < 0 || unlockpt(master) < 0) {
        perror("grantpt/unlockpt");
        close(master);
        return -1;
    }
    if (ptsname_r(master, slave_name, size) != 0) {
        perror("ptsname_r");
        close(master);
        return -1;
    }
    /* Пакетний режим — лише на ведучому дескрипторі. Без нього ведучий
       ніколи не дізнається про tcflush() чи ^S на тому боці. */
    if (ioctl(master, TIOCPKT, &mode) < 0) {
        perror("ioctl(TIOCPKT)");
        close(master);
        return -1;
    }
    return master;
}

static void run_child(const char *slave_name, char *const argv[])
{
    int slave;

    if (setsid() < 0)
        _exit(127);
    slave = open(slave_name, O_RDWR);
    if (slave < 0)
        _exit(127);
    /* Робимо ведений пристрій контрольним терміналом сесії — інакше
       не працюватимуть ні ^C, ні керування завданнями. */
    if (ioctl(slave, TIOCSCTTY, 0) < 0)
        _exit(127);

    if (dup2(slave, STDIN_FILENO) < 0 || dup2(slave, STDOUT_FILENO) < 0 ||
        dup2(slave, STDERR_FILENO) < 0)
        _exit(127);
    if (slave > STDERR_FILENO)
        close(slave);

    execvp(argv[0], argv);
    _exit(127);
}

int pty_run(char *const argv[])
{
    char slave_name[128];
    struct tty_session sess;
    struct master_ctx ctx;
    pid_t child;
    int status = 0;
    int rc = 1;

    int master = open_master(slave_name, sizeof slave_name);
    if (master < 0)
        return 1;

    copy_winsize(STDIN_FILENO, master);

    child = fork();
    if (child < 0) {
        perror("fork");
        close(master);
        return 1;
    }
    if (child == 0) {
        close(master);
        run_child(slave_name, argv);
    }

    /* Ведучий: власний термінал у сирий режим, бо всю обробку тепер
       робить лінійна дисципліна веденого. */
    if (tty_session_open(&sess, STDIN_FILENO) == 0 &&
        tty_session_enter_raw(&sess, 1, 0) == 0)
        tty_signals_install(&sess);
    else
        sess.active = 0;

    /* Обидва дескриптори неблокуючі: інакше другий read() у циклі
       дренажу зупинив би нас назавжди, а write() у повний буфер PTY
       дав би класичний дедлок «обидва чекають одне одного». */
    tty_set_nonblock(STDIN_FILENO, 1);
    tty_set_nonblock(master, 1);

    ctx.master = master;
    ctx.flow_stopped = 0;
    ctx.eof = 0;

    while (!ctx.eof) {
        struct pollfd pfd[2];
        int n;

        pfd[0].fd = STDIN_FILENO;
        pfd[0].events = ctx.flow_stopped ? 0 : POLLIN;
        pfd[0].revents = 0;
        pfd[1].fd = master;
        pfd[1].events = POLLIN;
        pfd[1].revents = 0;

        n = poll(pfd, 2, -1);
        if (n < 0) {
            if (errno == EINTR) {
                if (tty_signals_resized())
                    copy_winsize(STDIN_FILENO, master);
                continue;
            }
            perror("poll");
            break;
        }

        if (pfd[0].revents & (POLLIN | POLLHUP)) {
            ssize_t got = tty_drain(STDIN_FILENO, on_stdin_chunk, &ctx);
            if (got == TTY_READ_ERROR)
                perror("read(stdin)");
        }
        if (pfd[1].revents & (POLLIN | POLLHUP | POLLERR)) {
            ssize_t got = tty_drain(master, on_master_packet, &ctx);
            if (got == TTY_DRAIN_EOF)
                ctx.eof = 1;      /* ведений закрив останній дескриптор */
            else if (got == TTY_READ_ERROR && errno != EIO)
                perror("read(master)");
            else if (got == TTY_READ_ERROR)
                ctx.eof = 1;      /* EIO на master — теж кінець сеансу */
        }
    }

    tty_set_nonblock(STDIN_FILENO, 0);
    tty_session_restore(&sess);
    close(master);

    if (waitpid(child, &status, 0) == child && WIFEXITED(status))
        rc = WEXITSTATUS(status);
    return rc;
}
