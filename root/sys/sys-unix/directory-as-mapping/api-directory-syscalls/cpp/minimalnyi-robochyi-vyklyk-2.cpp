#include <dirent.h>
#include <cerrno>
#include <cstdio>
#include <iostream>

int main()
{
    DIR *d = opendir(".");
    if (!d) { std::perror("opendir"); return 1; }

    for (;;) {
        errno = 0;                       /* інакше кінець не відрізнити від збою */
        struct dirent *e = readdir(d);
        if (!e) break;
        std::cout << e->d_name << "\n";
    }
    if (errno != 0) std::perror("readdir");

    closedir(d);
    return 0;
}
