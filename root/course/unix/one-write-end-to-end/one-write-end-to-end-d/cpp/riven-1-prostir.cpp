#include <array>
#include <cstddef>
#include <fcntl.h>
#include <fstream>
#include <print>
#include <string_view>
#include <system_error>
#include <unistd.h>

void demo_write_mechanics() {
    /* 1. Рівень std::ofstream: буферизація через std::filebuf */
    {
        std::ofstream stream("app.log", std::ios::out | std::ios::app);
        if (stream.is_open()) {
            stream << "Рядок у буфері C++ stream\n";
            stream.flush(); /* Форсує виклик write() */
        }
    }

    /* 2. Прямий POSIX виклик: оминає бібліотечні потоки */
    int fd = ::open("app.log", O_WRONLY | O_APPEND);
    if (fd >= 0) {
        constexpr std::string_view msg = "Прямий системний виклик\n";
        const ssize_t ret = ::write(fd, msg.data(), msg.size());
        (void)ret;
        ::close(fd);
    }
}
