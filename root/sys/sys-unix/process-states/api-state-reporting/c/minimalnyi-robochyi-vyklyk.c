#define _GNU_SOURCE
#include <dirent.h>
#include <stdio.h>
#include <string.h>

/* Читає перший рядок файлу; повертає довжину або -1. */
static int read_line(const char *path, char *buf, size_t cap)
{
    FILE *f = fopen(path, "re");
    if (!f)
        return -1;
    size_t n = fread(buf, 1, cap - 1, f);
    fclose(f);
    buf[n] = '\0';
    buf[strcspn(buf, "\n")] = '\0';
    return (int)n;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "вжиток: %s <pid>\n", argv[0]);
        return 2;
    }

    char dir[64], path[160], buf[4096], wchan[128];
    snprintf(dir, sizeof dir, "/proc/%s/task", argv[1]);

    DIR *d = opendir(dir);
    if (!d) {
        perror(dir);
        return 1;
    }

    for (struct dirent *e; (e = readdir(d)) != NULL; ) {
        if (e->d_name[0] == '.')
            continue;

        snprintf(path, sizeof path, "%s/%s/stat", dir, e->d_name);
        if (read_line(path, buf, sizeof buf) <= 0)
            continue;                      /* потік вийшов, поки ми читали */

        char *p = strrchr(buf, ')');       /* кінець поля 2 — ОСТАННЯ дужка */
        if (!p || p[1] != ' ')
            continue;
        char state = p[2];                 /* поле 3 — рівно один байт */

        snprintf(path, sizeof path, "%s/%s/wchan", dir, e->d_name);
        if (read_line(path, wchan, sizeof wchan) <= 0)
            strcpy(wchan, "0");            /* «0» = біжить або немає прав */

        printf("%-7s %c  %s\n", e->d_name, state, wchan);
    }

    closedir(d);
    return 0;
}
