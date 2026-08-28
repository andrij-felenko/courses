#include <sys/capsicum.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

void run_sandboxed(void) {
    /* 1. Відкриваємо файл у звичайному режимі */
    int fd = open("/tmp/output.dat", O_RDWR | O_CREAT, 0600);

    /* 2. Обмежуємо дескриптор лише правом читання та fstat */
    cap_rights_t rights;
    cap_rights_init(&rights, CAP_READ, CAP_FSTAT);
    cap_rights_limit(fd, &rights);

    /* 3. Входимо в режим повної ізоляції */
    cap_enter();

    /* Прямий open тепер неможливий: */
    int bad = open("/etc/passwd", O_RDONLY); /* Повертає -1, errno = ECAPMODE */

    /* Запис у fd заборонено на рівні дескриптора: */
    write(fd, "test", 4); /* Повертає -1, errno = ENOTCAPABLE */
}
