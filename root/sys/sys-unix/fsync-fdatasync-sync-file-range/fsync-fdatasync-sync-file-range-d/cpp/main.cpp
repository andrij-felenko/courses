// Приклад атомарного запису конфігураційного файла на мові C++20
#include <iostream>
#include <fstream>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

namespace storage {

void save_config_atomic(std::string_view path, std::string_view data) {
    const std::string dest(path);
    const std::string tmp_path = dest + ".tmp";

    int fd = ::open(tmp_path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося створити тимчасовий файл");
    }

    if (::write(fd, data.data(), data.size()) != static_cast<ssize_t>(data.size())) {
        ::close(fd);
        ::unlink(tmp_path.c_str());
        throw std::system_error(errno, std::generic_category(), "Помилка запису даних");
    }

    if (::fdatasync(fd) < 0) {
        ::close(fd);
        ::unlink(tmp_path.c_str());
        throw std::system_error(errno, std::generic_category(), "Помилка fdatasync");
    }
    ::close(fd);

    if (::rename(tmp_path.c_str(), dest.c_str()) < 0) {
        ::unlink(tmp_path.c_str());
        throw std::system_error(errno, std::generic_category(), "Помилка атомарного перейменування");
    }

    const auto slash = dest.find_last_of('/');
    const std::string dir_path = (slash == std::string::npos) ? std::string(".") : dest.substr(0, slash);

    int dir_fd = ::open(dir_path.c_str(), O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        ::fsync(dir_fd);
        ::close(dir_fd);
    }
}

} // namespace storage
