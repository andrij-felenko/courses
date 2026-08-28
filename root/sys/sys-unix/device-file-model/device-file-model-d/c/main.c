#define _GNU_SOURCE
#include <stdio.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>   /* major(), minor() */

int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        struct stat st;
        if (lstat(argv[i], &st) < 0) { perror(argv[i]); continue; }

        const char *kind = S_ISCHR(st.st_mode) ? "символьний"
                         : S_ISBLK(st.st_mode) ? "блоковий"
                         : "не пристрій";

        printf("%-14s %-12s розмір=%lld блоків=%lld",
               argv[i], kind, (long long)st.st_size, (long long)st.st_blocks);

        if (S_ISCHR(st.st_mode) || S_ISBLK(st.st_mode))
            printf("  вказує на %u:%u", major(st.st_rdev), minor(st.st_rdev));
        else
            printf("  лежить на %u:%u", major(st.st_dev), minor(st.st_dev));

        putchar('\n');
    }
    return 0;
}
