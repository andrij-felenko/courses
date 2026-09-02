#include "termios_abi.h"

#include "termios2_baud.h"

#include <stddef.h>
#include <stdio.h>
#include <termios.h>
#include <unistd.h>

struct field_row {
    const char *name;
    size_t      offset;
    size_t      size;
    const char *role;
};

/* offsetof і sizeof питаємо в компілятора, а не переписуємо з документації:
   розкладка залежить від платформи, і саме її розбіжність із ядровою дає
   найдовші вечори з termios. */
#define FIELD(f, role) \
    { #f, offsetof(struct termios, f), sizeof(((struct termios *)0)->f), role }

static const struct field_row FIELDS[] = {
    FIELD(c_iflag,  "вхід: BREAK, парність, CR/NL, XON/XOFF"),
    FIELD(c_oflag,  "вихід: OPOST, ONLCR, телетайпні затримки"),
    FIELD(c_cflag,  "лінія: кадр даних, парність, поле CBAUD"),
    FIELD(c_lflag,  "дисципліна: ICANON, ECHO, ISIG, IEXTEN"),
#ifdef __linux__
    FIELD(c_line,   "номер лінійної дисципліни (0 = N_TTY)"),
#endif
    FIELD(c_cc,     "спецсимволи за індексами VINTR…VEOL2"),
    FIELD(c_ispeed, "швидкість прийому"),
    FIELD(c_ospeed, "швидкість передачі"),
};

int termios_abi_dump(void)
{
    struct termios2_layout k;
    int consistent = 1;

    printf("struct termios (простір користувача): %zu байтів, NCCS = %d\n",
           sizeof(struct termios), (int)NCCS);
    printf("  %-9s %8s %6s  %s\n", "поле", "зміщення", "розмір", "роль");
    for (size_t i = 0; i < sizeof FIELDS / sizeof FIELDS[0]; ++i)
        printf("  %-9s %8zu %6zu  %s\n",
               FIELDS[i].name, FIELDS[i].offset, FIELDS[i].size, FIELDS[i].role);
    printf("  типи: tcflag_t %zu Б, cc_t %zu Б, speed_t %zu Б; "
           "_POSIX_VDISABLE = 0x%02X\n",
           sizeof(tcflag_t), sizeof(cc_t), sizeof(speed_t),
           (unsigned)_POSIX_VDISABLE);

    if (termios2_layout(&k) != 0) {
        puts("\nstruct termios2: ядрового <asm/termbits.h> на цій системі немає");
        return 0;
    }

    printf("\nstruct termios2 (ядро): %lu байтів, NCCS = %lu\n", k.size, k.nccs);
    printf("  c_cc     +%lu\n", k.off_cc);
    printf("  c_ispeed +%lu\n", k.off_ispeed);
    printf("  c_ospeed +%lu\n", k.off_ospeed);
    printf("  CBAUD = 0%lo, BOTHER = 0%lo\n", k.cbaud, k.bother);

    /* Ось де ховається головна пастка ABI: ядро віддає 19 спецсимволів,
       а бібліотека розкладає їх у масив на 32. Тому struct termios ніколи
       не передають у TCGETS2 напряму — між двома розкладками перекладає
       glibc усередині tcgetattr(). */
    if (k.nccs != (unsigned long)NCCS) {
        printf("  УВАГА: у ядрі %lu спецсимволів, у бібліотеці %d —\n"
               "         struct termios у TCGETS2 віддавати не можна\n",
               k.nccs, (int)NCCS);
        consistent = 0;
    }
    if (k.size != sizeof(struct termios))
        printf("  розміри структур різні (%lu проти %zu), і це не поломка:\n"
               "         у termios2 швидкість лежить числом, а масив c_cc коротший\n",
               k.size, sizeof(struct termios));

    return consistent ? 0 : 1;
}
