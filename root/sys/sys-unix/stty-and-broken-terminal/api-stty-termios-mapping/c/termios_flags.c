#include "termios_flags.h"

#include <stdio.h>
#include <stddef.h>

/* Далі — та сама відповідність, що її друкує `stty -a`: ім'я аргументу
   й один біт. Прапорці поза POSIX закриті #ifdef, бо на BSD їх немає. */

static const struct tty_flag IFLAGS[] = {
    { "ignbrk", IGNBRK }, { "brkint", BRKINT }, { "ignpar", IGNPAR },
    { "parmrk", PARMRK }, { "inpck",  INPCK  }, { "istrip", ISTRIP },
    { "inlcr",  INLCR  }, { "igncr",  IGNCR  }, { "icrnl",  ICRNL  },
#ifdef IUCLC
    { "iuclc",  IUCLC  },
#endif
    { "ixon",   IXON   }, { "ixany",  IXANY  }, { "ixoff",  IXOFF  },
#ifdef IMAXBEL
    { "imaxbel", IMAXBEL },
#endif
#ifdef IUTF8
    { "iutf8",  IUTF8  },
#endif
    { NULL, 0 }
};

static const struct tty_flag OFLAGS[] = {
    { "opost",  OPOST  },
#ifdef OLCUC
    { "olcuc",  OLCUC  },
#endif
    { "onlcr",  ONLCR  }, { "ocrnl",  OCRNL  }, { "onocr",  ONOCR  },
    { "onlret", ONLRET },
#ifdef OFILL
    { "ofill",  OFILL  },
#endif
#ifdef OFDEL
    { "ofdel",  OFDEL  },
#endif
    { NULL, 0 }
};

/* CSIZE — не прапорець, а двобітове поле; його друкуємо окремо. */
static const struct tty_flag CFLAGS[] = {
    { "cstopb", CSTOPB }, { "cread",  CREAD  }, { "parenb", PARENB },
    { "parodd", PARODD }, { "hupcl",  HUPCL  }, { "clocal", CLOCAL },
#ifdef CRTSCTS
    { "crtscts", CRTSCTS },
#endif
#ifdef CMSPAR
    { "cmspar", CMSPAR },
#endif
    { NULL, 0 }
};

static const struct tty_flag LFLAGS[] = {
    { "isig",   ISIG   }, { "icanon", ICANON },
#ifdef XCASE
    { "xcase",  XCASE  },
#endif
    { "echo",   ECHO   }, { "echoe",  ECHOE  }, { "echok",  ECHOK  },
    { "echonl", ECHONL }, { "noflsh", NOFLSH }, { "tostop", TOSTOP },
#ifdef ECHOCTL
    { "echoctl", ECHOCTL },
#endif
#ifdef ECHOPRT
    { "echoprt", ECHOPRT },
#endif
#ifdef ECHOKE
    { "echoke", ECHOKE },
#endif
#ifdef FLUSHO
    { "flusho", FLUSHO },
#endif
#ifdef PENDIN
    { "pendin", PENDIN },
#endif
    { "iexten", IEXTEN },
#ifdef EXTPROC
    { "extproc", EXTPROC },
#endif
    { NULL, 0 }
};

static const struct tty_cchar CCHARS[] = {
    { "intr",  VINTR  }, { "quit",  VQUIT  }, { "erase", VERASE },
    { "kill",  VKILL  }, { "eof",   VEOF   }, { "eol",   VEOL   },
#ifdef VEOL2
    { "eol2",  VEOL2  },
#endif
    { "start", VSTART }, { "stop",  VSTOP  }, { "susp",  VSUSP  },
#ifdef VREPRINT
    { "rprnt", VREPRINT },
#endif
#ifdef VWERASE
    { "werase", VWERASE },
#endif
#ifdef VLNEXT
    { "lnext", VLNEXT },
#endif
#ifdef VDISCARD
    { "discard", VDISCARD },
#endif
#ifdef VSWTC
    { "swtch", VSWTC },
#endif
    { NULL, 0 }
};

struct baud_row {
    speed_t       code;
    unsigned long rate;
};

static const struct baud_row BAUDS[] = {
    { B0, 0 }, { B50, 50 }, { B75, 75 }, { B110, 110 }, { B134, 134 },
    { B150, 150 }, { B200, 200 }, { B300, 300 }, { B600, 600 },
    { B1200, 1200 }, { B1800, 1800 }, { B2400, 2400 }, { B4800, 4800 },
    { B9600, 9600 }, { B19200, 19200 }, { B38400, 38400 },
#ifdef B57600
    { B57600, 57600 },
#endif
#ifdef B115200
    { B115200, 115200 },
#endif
#ifdef B230400
    { B230400, 230400 },
#endif
#ifdef B460800
    { B460800, 460800 },
#endif
#ifdef B921600
    { B921600, 921600 },
#endif
#ifdef B1000000
    { B1000000, 1000000 },
#endif
#ifdef B2000000
    { B2000000, 2000000 },
#endif
#ifdef B4000000
    { B4000000, 4000000 },
#endif
};

unsigned long tty_flags_baud(const struct termios *t)
{
    speed_t code = cfgetospeed(t);

#ifdef BOTHER
    /* BOTHER: швидкість не кодом із CBAUD, а числом у c_ospeed —
       так задають 31250 бод для MIDI чи 250000 для DMX512. */
    if (code == BOTHER)
        return (unsigned long)t->c_ospeed;
#endif
    for (size_t i = 0; i < sizeof BAUDS / sizeof BAUDS[0]; ++i)
        if (BAUDS[i].code == code)
            return BAUDS[i].rate;
    return 0;
}

/* Витягує багатобітове поле (CRDLY, TABDLY…) як маленьке число:
   зсув рахуємо з самої маски, щоб не зашивати його руками. */
static unsigned field_value(tcflag_t value, tcflag_t mask)
{
    unsigned shift = 0;

    while (mask != 0 && (mask & 1u) == 0) {
        mask >>= 1;
        shift++;
    }
    return (unsigned)((value >> shift) & mask);
}

static void print_group(const struct tty_flag *table, tcflag_t value)
{
    int in_row = 0;

    fputs("  ", stdout);
    for (const struct tty_flag *f = table; f->stty_name != NULL; ++f) {
        if (in_row == 6) {
            fputs("\n  ", stdout);
            in_row = 0;
        }
        printf("%s%s ", (value & f->bit) ? "" : "-", f->stty_name);
        in_row++;
    }
    fputc('\n', stdout);
}

static const char *csize_name(tcflag_t c)
{
    switch (c & CSIZE) {
    case CS5: return "cs5";
    case CS6: return "cs6";
    case CS7: return "cs7";
    default:  return "cs8";
    }
}

static void print_cchar(const char *name, cc_t v)
{
    if (v == 0)
        printf("  %-8s <undef>\n", name);            /* _POSIX_VDISABLE */
    else if (v == 0x7F)
        printf("  %-8s ^?    (0x%02X)\n", name, v);
    else if (v < 0x20)
        printf("  %-8s ^%c    (0x%02X)\n", name, (char)(v + 64), v);
    else
        printf("  %-8s '%c'   (0x%02X)\n", name, (char)v, v);
}

void tty_flags_dump(const struct termios *t)
{
    printf("швидкість %lu бод; лінійна дисципліна %d\n\n",
           tty_flags_baud(t), (int)t->c_line);

    printf("c_iflag = 0x%08lx\n", (unsigned long)t->c_iflag);
    print_group(IFLAGS, t->c_iflag);

    printf("c_oflag = 0x%08lx\n", (unsigned long)t->c_oflag);
    print_group(OFLAGS, t->c_oflag);
    /* Затримки виводу — спадок телетайпів: поля, а не окремі біти. */
    printf("  затримки: nl%u cr%u tab%u bs%u vt%u ff%u\n",
           field_value(t->c_oflag, NLDLY), field_value(t->c_oflag, CRDLY),
           field_value(t->c_oflag, TABDLY), field_value(t->c_oflag, BSDLY),
           field_value(t->c_oflag, VTDLY), field_value(t->c_oflag, FFDLY));

    printf("c_cflag = 0x%08lx\n", (unsigned long)t->c_cflag);
    printf("  %s ", csize_name(t->c_cflag));
    print_group(CFLAGS, t->c_cflag);

    printf("c_lflag = 0x%08lx\n", (unsigned long)t->c_lflag);
    print_group(LFLAGS, t->c_lflag);

    puts("c_cc:");
    for (const struct tty_cchar *c = CCHARS; c->stty_name != NULL; ++c)
        print_cchar(c->stty_name, t->c_cc[c->index]);
    printf("  %-8s %u\n", "min", (unsigned)t->c_cc[VMIN]);
    printf("  %-8s %u  (× 0.1 с)\n", "time", (unsigned)t->c_cc[VTIME]);
}

int tty_flags_diagnose(const struct termios *t)
{
    int found = 0;

    if (!(t->c_lflag & ECHO)) {
        puts("\nсліпий термінал: знято ECHO — набране не видно  →  stty echo");
        found++;
    }
    if (!(t->c_lflag & ICANON)) {
        puts("немає редагування рядка: знято ICANON — Backspace друкується "
             "як ^? →  stty icanon");
        found++;
    }
    if (!(t->c_lflag & ISIG)) {
        puts("мертві Ctrl+C/Ctrl+Z: знято ISIG — байти йдуть як дані  →  stty isig");
        found++;
    }
    if (!(t->c_oflag & OPOST) || !(t->c_oflag & ONLCR)) {
        puts("ефект сходів: знято OPOST або ONLCR — \\n не розгортається "
             "в \\r\\n  →  stty opost onlcr");
        found++;
    }
    if (!(t->c_iflag & ICRNL) && !(t->c_iflag & IGNCR)) {
        puts("мертвий Enter: знято ICRNL — оболонка чекає \\n, а клавіша шле "
             "\\r  →  натисніть Ctrl+J, потім stty icrnl");
        found++;
    }
    if (t->c_iflag & IGNCR) {
        puts("мертвий Enter: стоїть IGNCR — усі \\r знищуються ядром  →  stty -igncr");
        found++;
    }
    if (t->c_iflag & ISTRIP) {
        puts("побитий UTF-8: стоїть ISTRIP — старший біт кожного байта "
             "відсікається  →  stty -istrip");
        found++;
    }
    if (!(t->c_cflag & CREAD)) {
        puts("лінія глуха: знято CREAD — приймач не бере байтів  →  stty cread");
        found++;
    }
    if ((t->c_lflag & ICANON) && t->c_cc[VMIN] == 0 && t->c_cc[VTIME] == 0)
        puts("(VMIN = VTIME = 0 у канонічному режимі ні на що не впливає)");

    return found;
}
