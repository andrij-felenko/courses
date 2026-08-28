#define _GNU_SOURCE
#include <sched.h>
#include <linux/sched/types.h>   /* struct sched_attr */
#include <sys/syscall.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

int main(void)
{
    struct sched_attr attr;

    memset(&attr, 0, sizeof attr);
    attr.size          = sizeof attr;
    attr.sched_policy  = SCHED_OTHER;   /* клас той самий, звичайний */
    attr.sched_nice    = 0;             /* частка часу теж та сама */
    attr.sched_runtime = 300000;        /* 0.3 мс замість типових 3 мс */

    if (syscall(SYS_sched_setattr, 0, &attr, 0u) != 0) {
        perror("sched_setattr");
        return 1;
    }

    /* успіх ще не означає, що прохання взяли: ядро до 6.12 це поле для
       звичайного класу просто ігнорує — перевіряють зворотним читанням
       через sched_getattr() */

    /* відтепер задача прокидається частіше, але щоразу ненадовго;
       сумарний відсоток процесора не змінився */
    return 0;
}
