#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "вжиток: %s ВУЗОЛ\n", argv[0]); return 2; }

    struct stat st;
    if (lstat(argv[1], &st) != 0) {
        fprintf(stderr, "lstat(%s): %s\n", argv[1], strerror(errno));
        return 1;
    }

    mode_t type = st.st_mode & S_IFMT;
    if (type != S_IFCHR && type != S_IFBLK) {
        fprintf(stderr, "%s — не вузол пристрою\n", argv[1]);
        return 1;
    }

    /* єдиний коректний розбір: зсуви руками дадуть сміття */
    unsigned maj = major(st.st_rdev), min = minor(st.st_rdev);
    printf("%s: %s %u:%u   (dev_t = 0x%llx)\n", argv[1],
           type == S_IFCHR ? "символьний" : "блоковий",
           maj, min, (unsigned long long)st.st_rdev);

    /* зворотний бік: складаємо ту саму пару під іншим іменем */
    char copy[64];
    snprintf(copy, sizeof copy, "/tmp/dev-%u-%u", maj, min);
    if (mknod(copy, type | 0600, makedev(maj, min)) != 0) {
        fprintf(stderr, "mknod(%s): %s\n", copy, strerror(errno));
        return errno == EPERM ? 3 : 1;      /* найімовірніше — немає CAP_MKNOD */
    }
    printf("створено %s — той самий пристрій\n", copy);
    return 0;
}
