#include <iostream>
#include <string_view>
#include <memory>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

struct FileCloser {
    void operator()(int* fd) const {
        if (fd && *fd >= 0) {
            ::close(*fd);
            delete fd;
        }
    }
};
using UniqueFd = std::unique_ptr<int, FileCloser>;

void process_user_report_cpp(std::string_view filepath, std::string_view data) {
    // ВРАЗЛИВІСТЬ (TOC): попередня перевірка за рядковим шляхом
    if (::access(filepath.data(), W_OK) != 0) {
        std::cerr << "Access denied\n";
        return;
    }

    // ВІКНО ГОНКИ (Δt): планувальник перемикає контекст на зловмисника

    // ВРАЗЛИВІСТЬ (TOU): повторне розв'язання шляху з правами root
    UniqueFd fd(new int(::open(filepath.data(), O_WRONLY | O_TRUNC)));
    if (*fd >= 0) {
        ::write(*fd, data.data(), data.size());
    }
}
