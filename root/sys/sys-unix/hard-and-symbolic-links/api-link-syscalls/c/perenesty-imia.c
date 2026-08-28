#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>

/* У glibc до 2.28 константи немає в жодному з цих заголовків. */
#ifndef RENAME_NOREPLACE
#define RENAME_NOREPLACE (1 << 0)
#endif

/* Перейменувати, НЕ витісняючи ціль. 0 — успіх, -1 і errno — ні. */
int rename_noreplace(const char *old, const char *new)
{
#ifdef SYS_renameat2
    if (syscall(SYS_renameat2, AT_FDCWD, old, AT_FDCWD, new,
                RENAME_NOREPLACE) == 0)
        return 0;
    if (errno != ENOSYS && errno != EINVAL && errno != EOPNOTSUPP)
        return -1;              /* справжня помилка, не брак підтримки */
#endif
    /* Запасний шлях без renameat2: жорстке посилання не витісняє ніколи,
       тож EEXIST від link() дає рівно ту саму відмову. Не атомарно
       як ціле — між link і unlink файл видно під двома іменами, —
       але цілі під іменем new не підміняє. */
    if (link(old, new) < 0)
        return -1;              /* EEXIST, якщо ім'я зайняте */
    return unlink(old);
}
