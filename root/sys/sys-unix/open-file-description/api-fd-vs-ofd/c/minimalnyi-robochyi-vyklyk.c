#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/kcmp.h>
#include <stdio.h>
#include <sys/syscall.h>
#include <unistd.h>

static int same_ofd(int a, int b) {
    pid_t me = getpid();
    return syscall(SYS_kcmp, me, me, KCMP_FILE,
                   (unsigned long)a, (unsigned long)b) == 0;
}

int main(void) {
    int fd  = open("probe.txt", O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    int cp  = dup(fd);                    /* той самий опис, новий номер */
    int own = open("probe.txt", O_RDWR);  /* власний опис */
    if (fd < 0 || cp < 0 || own < 0) { perror("open"); return 1; }

    /* поверх 1: у кожного дескриптора свій прапорець */
    printf("FD_CLOEXEC: fd=%d cp=%d\n",
           (fcntl(fd, F_GETFD) & FD_CLOEXEC) != 0,
           (fcntl(cp, F_GETFD) & FD_CLOEXEC) != 0);

    /* поверх 2: прапорці стану спільні — читай-зміни-запиши */
    int fl = fcntl(fd, F_GETFL);
    printf("режим доступу = %d, O_APPEND до = %d\n",
           fl & O_ACCMODE, (fl & O_APPEND) != 0);
    fcntl(fd, F_SETFL, fl | O_APPEND);
    printf("O_APPEND після: через cp = %d, через own = %d\n",
           (fcntl(cp,  F_GETFL) & O_APPEND) != 0,
           (fcntl(own, F_GETFL) & O_APPEND) != 0);

    /* спільність опису — питання до ядра */
    printf("fd~cp = %d, fd~own = %d\n", same_ofd(fd, cp), same_ofd(fd, own));
    return 0;
}
