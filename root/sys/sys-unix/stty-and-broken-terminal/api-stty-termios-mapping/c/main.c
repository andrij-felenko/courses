/* ttyx — розбір, псування й відновлення стану термінала.
 *
 *   ttyx dump             розбір поточного termios у словах stty + діагноз
 *   ttyx abi              розкладка struct termios і ядрової struct termios2
 *   ttyx sane | cooked    застосувати профіль (з перевіркою, що ядро його взяло)
 *   ttyx raw              сирий режим: показує коди клавіш, поки не натиснуто q
 *   ttyx pass             прихований ввід (профіль -echo)
 *   ttyx reset            escape-скидання модальних регістрів емулятора
 *   ttyx caps             можливості $TERM з бази terminfo
 *   ttyx baud <dev> [n]   швидкість лінії числом; із n — довільна через BOTHER
 *   ttyx pty <cmd> …      запуск команди під PTY у пакетному режимі TIOCPKT
 */
#include "pty_packet.h"
#include "readpass.h"
#include "terminfo_caps.h"
#include "termios2_baud.h"
#include "termios_abi.h"
#include "termios_flags.h"
#include "termios_profiles.h"
#include "tty_input.h"
#include "tty_session.h"
#include "tty_signals.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>

static int cmd_dump(void)
{
    struct termios t;
    if (tcgetattr(STDIN_FILENO, &t) < 0) {
        perror("tcgetattr(stdin)");
        return 1;
    }

    struct winsize ws;
    if (ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == 0)
        printf("вікно: %u рядків, %u стовпчиків, %u x %u пікселів\n",
               ws.ws_row, ws.ws_col, ws.ws_xpixel, ws.ws_ypixel);

    tty_flags_dump(&t);

    int broken = tty_flags_diagnose(&t);
    if (broken == 0)
        printf("\nдіагноз: жодної типової поломки не видно\n");
    return 0;
}

static int cmd_profile(const char *name)
{
    struct termios t;
    if (tcgetattr(STDIN_FILENO, &t) < 0) {
        perror("tcgetattr(stdin)");
        return 1;
    }

    if (strcmp(name, "sane") == 0)
        termios_make_sane(&t);
    else
        termios_make_cooked(&t);

    /* TCSADRAIN — як робить сама stty: спершу дати дописати те, що вже
       в черзі виводу, і аж тоді міняти правила під ним. */
    if (termios_apply_verified(STDIN_FILENO, TCSADRAIN, &t) < 0) {
        if (errno != 0 && errno != EINVAL)
            perror("tcsetattr");
        fprintf(stderr, "профіль %s застосовано не повністю (див. вище)\n", name);
        return 1;
    }
    printf("профіль %s застосовано\n", name);
    return 0;
}

/* У сирому режимі OPOST вимкнено, тож перевід рядка треба писати повністю:
   сам \n лише опустить курсор, не повернувши його до нульової колонки. */
static void show_byte(unsigned char c)
{
    char line[64];
    int n;

    if (c == 0x7F)
        n = snprintf(line, sizeof line, "0x%02X  ^?\r\n", c);
    else if (c < 0x20)
        n = snprintf(line, sizeof line, "0x%02X  ^%c\r\n", c, (char)(c + 64));
    else
        n = snprintf(line, sizeof line, "0x%02X  '%c'\r\n", c, (char)c);

    if (n > 0)
        tty_write_all(STDOUT_FILENO, line, (size_t)n);
}

static void show_winsize(void)
{
    struct winsize ws;
    char line[64];

    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) < 0)
        return;
    int n = snprintf(line, sizeof line, "SIGWINCH: %u x %u\r\n", ws.ws_col, ws.ws_row);
    if (n > 0)
        tty_write_all(STDOUT_FILENO, line, (size_t)n);
}

static int cmd_raw(void)
{
    struct tty_session s;

    if (tty_session_open(&s, STDIN_FILENO) < 0) {
        perror("stdin");
        return 1;
    }
    /* VMIN = 1, VTIME = 0 — квадрант чистого блокування: read() чекає
       рівно на один байт і ніколи не повертає 0 через таймер. */
    if (tty_session_enter_raw(&s, 1, 0) < 0) {
        perror("tcsetattr(raw)");
        return 1;
    }
    if (tty_signals_install(&s) < 0) {
        perror("sigaction");
        tty_session_restore(&s);
        return 1;
    }

    const char *hint = "сирий режим: показую коди клавіш; вихід — q\r\n";
    tty_write_all(STDOUT_FILENO, hint, strlen(hint));

    int rc = 0;
    for (;;) {
        unsigned char c;
        int got = tty_read_byte(STDIN_FILENO, &c);

        if (got == TTY_READ_INTERRUPTED) {
            /* read() перервано сигналом (типово SIGWINCH). Це не помилка:
               обробляємо подію й повторюємо виклик. */
            if (tty_signals_resized())
                show_winsize();
            continue;
        }
        if (got == TTY_READ_ERROR) {
            rc = 1;
            break;
        }
        if (got == 0)
            break;              /* дескриптор закрито з того боку */

        show_byte(c);
        if (c == 'q')
            break;
    }

    tty_session_restore(&s);
    return rc;
}

static int cmd_pass(void)
{
    char secret[256];
    ssize_t n = tty_read_password(STDIN_FILENO, "пароль: ", secret, sizeof secret);
    if (n < 0) {
        perror("tty_read_password");
        return 1;
    }
    /* Самого пароля не друкуємо — показуємо лише, що ввід дійшов цілим. */
    printf("прочитано %zd байтів\n", n);
    memset(secret, 0, sizeof secret);
    return 0;
}

static int cmd_reset(void)
{
    struct termios t;

    tty_emulator_reset(STDOUT_FILENO);
    if (tcgetattr(STDIN_FILENO, &t) == 0) {
        termios_make_sane(&t);
        termios_apply_verified(STDIN_FILENO, TCSANOW, &t);
    }
    printf("емулятор і termios скинуто\n");
    return 0;
}

/* Швидкість беремо з ПРИСТРОЮ, а не зі stdin: довільний бодрейт має сенс
   лише на справжньому UART — псевдотермінал проковтне будь-яке число
   мовчки, і перевірити нічого не вийде. */
static int cmd_baud(int argc, char *argv[])
{
    const char *dev = argv[2];
    long rate;
    int rc = 0;

    /* O_NONBLOCK на відкритті: без CLOCAL ядро тримало б open() доти,
       доки на лінії не з'явиться сигнал носія DCD. */
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        perror(dev);
        return 1;
    }

    if (argc >= 4) {
        char *end = NULL;
        unsigned long want = strtoul(argv[3], &end, 10);

        if (end == argv[3] || *end != '\0' || want == 0) {
            fprintf(stderr, "швидкість має бути додатним числом бод\n");
            rc = 2;
            goto out;
        }
        rate = termios2_set_baud(fd, want);
        if (rate < 0) {
            perror("ioctl(TCSETS2)");
            rc = 1;
            goto out;
        }
        printf("%s: просили %lu бод, ядро виставило %ld\n", dev, want, rate);
    } else {
        rate = termios2_get_baud(fd);
        if (rate < 0) {
            perror("ioctl(TCGETS2)");
            rc = 1;
            goto out;
        }
        printf("%s: %ld бод\n", dev, rate);
    }

out:
    close(fd);
    return rc;
}

static void usage(const char *argv0)
{
    fprintf(stderr,
            "вжиток: %s dump | abi | sane | cooked | raw | pass | reset | caps"
            " | baud <dev> [бод] | pty <cmd> …\n",
            argv0);
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }

    const char *cmd = argv[1];

    if (strcmp(cmd, "dump") == 0)
        return cmd_dump();
    if (strcmp(cmd, "abi") == 0)
        return termios_abi_dump();
    if (strcmp(cmd, "sane") == 0 || strcmp(cmd, "cooked") == 0)
        return cmd_profile(cmd);
    if (strcmp(cmd, "raw") == 0)
        return cmd_raw();
    if (strcmp(cmd, "pass") == 0)
        return cmd_pass();
    if (strcmp(cmd, "reset") == 0)
        return cmd_reset();
    if (strcmp(cmd, "caps") == 0)
        return terminfo_dump(STDOUT_FILENO) == 0 ? 0 : 1;
    if (strcmp(cmd, "baud") == 0) {
        if (argc < 3) {
            usage(argv[0]);
            return 2;
        }
        return cmd_baud(argc, argv);
    }
    if (strcmp(cmd, "pty") == 0) {
        if (argc < 3) {
            usage(argv[0]);
            return 2;
        }
        return pty_run(&argv[2]);
    }

    usage(argv[0]);
    return 2;
}
