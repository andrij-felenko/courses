#define _GNU_SOURCE
#include <sys/quota.h>
#include <stdio.h>
#include <unistd.h>

int main(void)
{
    struct dqblk d;

    if (quotactl(QCMD(Q_GETQUOTA, USRQUOTA), "/dev/sda1",
                 getuid(), (caddr_t)&d) < 0) {
        perror("quotactl");          /* ESRCH — квоти тут не ввімкнені */
        return 1;
    }

    printf("ужито %llu КіБ, м'яка межа %llu КіБ, жорстка %llu КіБ\n",
           (unsigned long long)(d.dqb_curspace / 1024),   /* байти → КіБ */
           (unsigned long long)d.dqb_bsoftlimit,          /* уже в КіБ */
           (unsigned long long)d.dqb_bhardlimit);
    return 0;
}
