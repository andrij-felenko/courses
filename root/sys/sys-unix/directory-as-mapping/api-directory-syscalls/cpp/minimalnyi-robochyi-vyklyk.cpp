#define _GNU_SOURCE
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>

#include <array>
#include <cstdio>

int main(int argc, char **argv)
{
    const char *path = (argc > 1) ? argv[1] : ".";

    int fd = open(path, O_RDONLY | O_DIRECTORY);
    if (fd < 0) {
        std::perror("open");
        return 1;
    }

    alignas(8) std::array<char, 64 * 1024> buf{};

    for (;;) {
        ssize_t n = getdents64(fd, buf.data(), buf.size());
        if (n < 0) {
            std::perror("getdents64");
            close(fd);
            return 1;
        }
        if (n == 0) break;

        for (ssize_t off = 0; off < n;) {
            auto *e = reinterpret_cast<struct dirent64 *>(buf.data() + off);
            std::printf("%-10llu тип %-3u %s\n",
                        static_cast<unsigned long long>(e->d_ino),
                        static_cast<unsigned>(e->d_type),
                        e->d_name);
            off += e->d_reclen;
        }
    }

    close(fd);
    return 0;
}
