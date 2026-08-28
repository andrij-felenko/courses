#include <fcntl.h>
#include <unistd.h>
#include <array>
#include <cstdio>
#include <iostream>
#include <string_view>

int main()
{
    int fd = open("/tmp/scratch", O_RDWR | O_CREAT | O_EXCL, 0600);
    if (fd < 0) {
        std::perror("open");
        return 1;
    }

    /* Імені більше немає: у /tmp його не побачить ніхто, зокрема й ми самі. */
    if (unlink("/tmp/scratch") < 0) {
        std::perror("unlink");
        close(fd);
        return 1;
    }

    constexpr std::string_view msg = "дані живуть, доки живе дескриптор\n";
    write(fd, msg.data(), msg.size());

    std::array<char, 64> buf{};
    lseek(fd, 0, SEEK_SET);
    ssize_t n = read(fd, buf.data(), buf.size() - 1);
    if (n > 0) {
        std::cout << "прочитано " << n << " байтів: "
                  << std::string_view(buf.data(), static_cast<size_t>(n));
    }

    close(fd);   /* аж тепер блоки звільняються */
    return 0;
}
