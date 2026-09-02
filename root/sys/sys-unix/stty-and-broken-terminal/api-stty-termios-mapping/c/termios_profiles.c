#include "termios_profiles.h"

#include <errno.h>
#include <stdio.h>

void termios_make_sane(struct termios *t)
{
    /* 1. Вхідні прапорці: лишаємо BREAK як переривання, Enter як \n
          і дзвінок при переповненні буфера. */
    t->c_iflag |= (BRKINT | ICRNL | IXON);
#ifdef IMAXBEL
    t->c_iflag |= IMAXBEL;
#endif
#ifdef IUTF8
    t->c_iflag |= IUTF8;
#endif
    t->c_iflag &= ~(tcflag_t)(IGNBRK | INLCR | IGNCR | IXOFF | IXANY |
                              IGNPAR | PARMRK | INPCK | ISTRIP);
#ifdef IUCLC
    t->c_iflag &= ~(tcflag_t)IUCLC;
#endif

    /* 2. Вихідні: обробка ввімкнена, \n розгортається в \r\n,
          усі телетайпні затримки зняті. */
    t->c_oflag |= (OPOST | ONLCR);
    t->c_oflag &= ~(tcflag_t)(OCRNL | ONOCR | ONLRET |
                              NLDLY | CRDLY | TABDLY | BSDLY | VTDLY | FFDLY);
#ifdef OLCUC
    t->c_oflag &= ~(tcflag_t)OLCUC;
#endif
#ifdef OFILL
    t->c_oflag &= ~(tcflag_t)(OFILL | OFDEL);
#endif

    /* 3. Лінія: 8 біт, без парності, приймач увімкнено, модемні лінії
          ігноруємо (інакше open() чекав би на DCD). */
    t->c_cflag |= (CREAD | CS8 | CLOCAL);
    t->c_cflag &= ~(tcflag_t)(PARENB | PARODD | CSTOPB);
    t->c_cflag = (t->c_cflag & ~(tcflag_t)CSIZE) | CS8;
#ifdef CRTSCTS
    t->c_cflag &= ~(tcflag_t)CRTSCTS;
#endif

    /* 4. Локальні: канонічний ввід, відлуння, сигнали, розширені спецсимволи. */
    t->c_lflag |= (ISIG | ICANON | IEXTEN | ECHO | ECHOE | ECHOK);
#ifdef ECHOCTL
    t->c_lflag |= ECHOCTL;
#endif
#ifdef ECHOKE
    t->c_lflag |= ECHOKE;
#endif
    t->c_lflag &= ~(tcflag_t)(ECHONL | NOFLSH | TOSTOP);
#ifdef ECHOPRT
    t->c_lflag &= ~(tcflag_t)ECHOPRT;
#endif
#ifdef XCASE
    t->c_lflag &= ~(tcflag_t)XCASE;
#endif

    /* 5. Спецсимволи — назад до заводських. */
    t->c_cc[VINTR]  = 0x03;   /* ^C  */
    t->c_cc[VQUIT]  = 0x1C;   /* ^\  */
    t->c_cc[VERASE] = 0x7F;   /* ^?  */
    t->c_cc[VKILL]  = 0x15;   /* ^U  */
    t->c_cc[VEOF]   = 0x04;   /* ^D  */
    t->c_cc[VSTART] = 0x11;   /* ^Q  */
    t->c_cc[VSTOP]  = 0x13;   /* ^S  */
    t->c_cc[VSUSP]  = 0x1A;   /* ^Z  */
    t->c_cc[VEOL]   = 0x00;   /* _POSIX_VDISABLE */
#ifdef VEOL2
    t->c_cc[VEOL2]  = 0x00;
#endif
#ifdef VREPRINT
    t->c_cc[VREPRINT] = 0x12; /* ^R  */
#endif
#ifdef VWERASE
    t->c_cc[VWERASE]  = 0x17; /* ^W  */
#endif
#ifdef VLNEXT
    t->c_cc[VLNEXT]   = 0x16; /* ^V  */
#endif
#ifdef VDISCARD
    t->c_cc[VDISCARD] = 0x0F; /* ^O  */
#endif
    t->c_cc[VMIN]  = 1;
    t->c_cc[VTIME] = 0;
}

void termios_make_cooked(struct termios *t)
{
    /* cooked (він же -raw) чіпає менше, ніж sane: повертає обробку,
       але не переписує спецсимволи, які користувач міг змінити свідомо. */
    t->c_iflag |= (ICRNL | IXON | BRKINT);
    t->c_oflag |= (OPOST | ONLCR);
    t->c_lflag |= (ICANON | ISIG | ECHO | ECHOE | ECHOK | IEXTEN);
    t->c_cc[VMIN]  = 1;
    t->c_cc[VTIME] = 0;
}

static int report_diff(const char *field, tcflag_t want, tcflag_t got, tcflag_t mask)
{
    tcflag_t diff = (want ^ got) & mask;

    if (diff == 0)
        return 0;
    fprintf(stderr,
            "%s: ядро не взяло біти 0x%08lx (просили 0x%08lx, маємо 0x%08lx)\n",
            field, (unsigned long)diff,
            (unsigned long)(want & mask), (unsigned long)(got & mask));
    return 1;
}

int termios_apply_verified(int fd, int optional_actions, const struct termios *want)
{
    struct termios got;
    int bad = 0;

    if (tcsetattr(fd, optional_actions, want) < 0)
        return -1;

    /* Ось заради чого все: tcsetattr щойно повернув 0, і це ще нічого
       не означає — стандарт вважає успіхом і часткове застосування. */
    if (tcgetattr(fd, &got) < 0)
        return -1;

    bad += report_diff("c_iflag", want->c_iflag, got.c_iflag, ~(tcflag_t)0);
    bad += report_diff("c_oflag", want->c_oflag, got.c_oflag, ~(tcflag_t)0);
    bad += report_diff("c_lflag", want->c_lflag, got.c_lflag, ~(tcflag_t)0);
    /* c_cflag звіряємо лише за кадром даних: швидкість, CRTSCTS і модемні
       лінії на псевдотерміналі ядро мовчки ігнорує, і це не поломка. */
    bad += report_diff("c_cflag", want->c_cflag, got.c_cflag,
                       (tcflag_t)(CSIZE | PARENB | PARODD | CSTOPB | CREAD));

    for (int i = 0; i < NCCS; ++i) {
        if (want->c_cc[i] != got.c_cc[i]) {
            fprintf(stderr, "c_cc[%d]: просили 0x%02X, маємо 0x%02X\n",
                    i, want->c_cc[i], got.c_cc[i]);
            bad++;
        }
    }

    if (bad != 0) {
        errno = EINVAL;
        return -1;
    }
    return 0;
}
