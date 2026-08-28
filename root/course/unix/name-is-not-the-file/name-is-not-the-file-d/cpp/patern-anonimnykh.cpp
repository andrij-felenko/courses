#include <iostream>
#include <string_view>
#include <unistd.h>
#include <fcntl.h>

void use_anonymous_temp_file() {
    int fd = ::open("/tmp/scratchpad.tmp", O_RDWR | O_CREAT | O_EXCL, 0600);
    if (fd < 0) return;

    // Негайний розрив зв'язку з каталогом
    ::unlink("/tmp/scratchpad.tmp");

    std::string_view data = "secret data";
    ::write(fd, data.data(), data.size());

    // Файл гарантовано зникне після закриття дескриптора
    ::close(fd);
}
