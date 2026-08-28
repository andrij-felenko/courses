#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>

static void show(const char *tag, const char *path)
{
    struct stat st;
    if (stat(path, &st) < 0) { perror(path); return; }
    printf("%-8s dev=%llu ino=%llu nlink=%lu\n", tag,
           (unsigned long long)st.st_dev,
           (unsigned long long)st.st_ino,
           (unsigned long)st.st_nlink);
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "потрібен шлях\n"); return 2; }

    show("до", argv[1]);

    int fd = open(argv[1], O_WRONLY);   /* сам факт відкриття тягне копіювання */
    if (fd < 0) { perror("open"); return 1; }
    close(fd);                          /* жодного байта не записано */

    show("після", argv[1]);
    return 0;
}
