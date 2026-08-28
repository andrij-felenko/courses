#include <iostream>
#include <fstream>
#include <string>
#include <format>
#include <system_error>
#include <cerrno>
#include <sched.h>
#include <unistd.h>
#include <sys/wait.h>

namespace sys {

void write_proc_file(const std::string& path, const std::string& content) {
    std::ofstream fs(path);
    if (!fs.is_open()) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + path);
    }
    fs << content;
    if (fs.fail()) {
        throw std::system_error(errno, std::generic_category(), "Помилка запису в " + path);
    }
}

} // namespace sys

int main() {
    try {
        uid_t host_uid = ::getuid();
        gid_t host_gid = ::getgid();

        // 1. Створення ізольованого User Namespace
        if (::unshare(CLONE_NEWUSER) < 0) {
            throw std::system_error(errno, std::generic_category(), "unshare(CLONE_NEWUSER) failed");
        }

        // 2. Блокування setgroups під вимоги безпеки GID
        sys::write_proc_file("/proc/self/setgroups", "deny");

        // 3. Запис прямого мапінгу ідентифікаторів
        sys::write_proc_file("/proc/self/uid_map", std::format("0 {} 1\n", host_uid));
        sys::write_proc_file("/proc/self/gid_map", std::format("0 {} 1\n", host_gid));

        std::cout << "[C++ UserNS] Новий статус ідентичності:\n"
                  << "  UID: " << ::getuid() << " (euid: " << ::geteuid() << ")\n"
                  << "  GID: " << ::getgid() << " (egid: " << ::getegid() << ")\n";

        ::execl("/bin/id", "id", nullptr);

    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
