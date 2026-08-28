#include <dirent.h>
#include <errno.h>
#include <stdio.h>

int main(void)
{
    DIR *d = opendir(".");
    if (!d) { perror("opendir"); return 1; }

    for (;;) {
        errno = 0;                       /* інакше кінець не відрізнити від збою */
        struct dirent *e = readdir(d);
        if (!e) break;
        printf("%s\n", e->d_name);
    }
    if (errno != 0) perror("readdir");

    closedir(d);
    return 0;
}
