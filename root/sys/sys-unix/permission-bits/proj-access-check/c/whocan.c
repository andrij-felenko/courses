/* whocan.c — вердикт про доступ, зроблений так само, як його робить ядро.
   Збірка: cc -Wall -O2 -o whocan whocan.c        Виклик: ./whocan r ШЛЯХ */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <linux/capability.h>      /* CAP_DAC_OVERRIDE == 1, CAP_DAC_READ_SEARCH == 2 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define WANT_R 4u
#define WANT_W 2u
#define WANT_X 1u

struct ident {
    uid_t fsuid;
    gid_t fsgid;
    gid_t *groups;
    int ngroups;
    unsigned long long capeff;
};

static void who_am_i(struct ident *me)
{
    unsigned long r, e, s, fs;
    char line[256];
    FILE *f = fopen("/proc/self/status", "r");

    me->fsuid = geteuid();          /* запасний варіант, якщо /proc не змонтовано */
    me->fsgid = getegid();
    me->capeff = 0;
    while (f && fgets(line, sizeof line, f)) {
        if (sscanf(line, "Uid: %lu %lu %lu %lu", &r, &e, &s, &fs) == 4)
            me->fsuid = (uid_t)fs;
        else if (sscanf(line, "Gid: %lu %lu %lu %lu", &r, &e, &s, &fs) == 4)
            me->fsgid = (gid_t)fs;
        else
            sscanf(line, "CapEff: %llx", &me->capeff);
    }
    if (f)
        fclose(f);

    me->ngroups = getgroups(0, NULL);
    if (me->ngroups < 0)
        me->ngroups = 0;
    me->groups = calloc((size_t)me->ngroups + 1, sizeof *me->groups);
    if (!me->groups) {
        perror("calloc");
        exit(1);
    }
    if (me->ngroups)
        getgroups(me->ngroups, me->groups);
}
