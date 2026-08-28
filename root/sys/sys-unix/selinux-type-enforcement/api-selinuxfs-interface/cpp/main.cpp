// C++: Ідіоматична RAII-обгортка над libselinux з використанням std::unique_ptr
#include <iostream>
#include <memory>
#include <system_error>
#include <cerrno>
#include <selinux/selinux.h>

namespace selinux {

// RAII-делетор для автоматичного викликання freecon при виході з області видимості
struct context_deleter {
    void operator()(char* ptr) const noexcept {
        if (ptr) {
            freecon(ptr);
        }
    }
};

using scoped_context = std::unique_ptr<char, context_deleter>;

class security_context {
public:
    static bool is_enabled() {
        int res = is_selinux_enabled();
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), "is_selinux_enabled failed");
        }
        return res > 0;
    }

    static int get_enforce_mode() {
        int mode = security_getenforce();
        if (mode < 0) {
            throw std::system_error(errno, std::generic_category(), "security_getenforce failed");
        }
        return mode;
    }

    static scoped_context get_current_process() {
        char* raw_con = nullptr;
        if (getcon(&raw_con) < 0) {
            throw std::system_error(errno, std::generic_category(), "getcon failed");
        }
        return scoped_context(raw_con);
    }

    static scoped_context get_file(const char* path) {
        char* raw_con = nullptr;
        if (getfilecon(path, &raw_con) < 0) {
            throw std::system_error(errno, std::generic_category(), "getfilecon failed");
        }
        return scoped_context(raw_con);
    }
};

} // namespace selinux

int main(int argc, char* argv[]) {
    try {
        if (!selinux::security_context::is_enabled()) {
            std::cout << "SELinux вимкнено або не підтримується.\n";
            return 0;
        }

        std::cout << "SELinux активний. Статус Enforcing: " 
                  << selinux::security_context::get_enforce_mode() << "\n";

        auto proc_con = selinux::security_context::get_current_process();
        std::cout << "Контекст процесу: " << proc_con.get() << "\n";

        const char* target_path = (argc > 1) ? argv[1] : "/etc/passwd";
        auto file_con = selinux::security_context::get_file(target_path);
        std::cout << "Контекст файлу (" << target_path << "): " << file_con.get() << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка SELinux: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
