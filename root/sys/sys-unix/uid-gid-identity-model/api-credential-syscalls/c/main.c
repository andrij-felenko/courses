#define _GNU_SOURCE
#include <unistd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    uid_t r, e, s;  gid_t rg, eg, sg;
    if (getresuid(&r, &e, &s) || getresgid(&rg, &eg, &sg))
        return 1;
    printf("uid %u/%u/%u  gid %u/%u/%u\n", r, e, s, rg, eg, sg);

    int n = getgroups(0, NULL);            /* спершу питаємо, скільки їх */
    if (n < 0) return 1;
    gid_t *g = calloc(n ? n : 1, sizeof *g);
    if (!g) return 1;
    n = getgroups(n, g);                   /* і аж тоді читаємо */
    for (int i = 0; i < n; i++)
        printf("%s%u", i ? " " : "groups ", g[i]);
    putchar('\n');
    free(g);
    return 0;
}
