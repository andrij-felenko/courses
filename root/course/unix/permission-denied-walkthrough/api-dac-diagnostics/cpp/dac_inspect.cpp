// dac_inspect.cpp — Діагностика ідентичності та перевірка прав доступу на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>

struct Credentials {
    uid_t ruid{}, euid{}, suid{};
    gid_t rgid{}, egid{}, sgid{};
    std::vector<gid_t> groups;
};

Credentials get_current_credentials() {
    Credentials cred;
    if (getresuid(&cred.ruid, &cred.euid, &cred.suid) != 0 ||
        getresgid(&cred.rgid, &cred.egid, &cred.sgid) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося отримати UID/GID");
    }

    int count = getgroups(0, nullptr);
    if (count > 0) {
        cred.groups.resize(count);
        if (getgroups(count, cred.groups.data()) < 0) {
            cred.groups.clear();
        }
    }
    return cred;
}

std::string check_permission(std::string_view path, int mode) {
    if (faccessat(AT_FDCWD, path.data(), mode, AT_EACCESS) == 0) {
        return "ДОЗВОЛЕНО";
    }
    return std::generic_category().message(errno);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файлу>\n";
        return 1;
    }

    try {
        const auto cred = get_current_credentials();
        std::cout << "Ідентичність процесу [PID " << getpid() << "]:\n"
                  << "  UID: real=" << cred.ruid << ", effective=" << cred.euid << ", saved=" << cred.suid << "\n"
                  << "  GID: real=" << cred.rgid << ", effective=" << cred.egid << ", saved=" << cred.sgid << "\n"
                  << "  Додаткові групи (" << cred.groups.size() << "): ";
        for (gid_t g : cred.groups) {
            std::cout << g << " ";
        }
        std::cout << "\n\n";

        const std::string target = argv[1];
        std::cout << "Перевірка доступу до '" << target << "':\n"
                  << "  Читання (R_OK):   " << check_permission(target, R_OK) << "\n"
                  << "  Запис (W_OK):     " << check_permission(target, W_OK) << "\n"
                  << "  Виконання (X_OK): " << check_permission(target, X_OK) << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
