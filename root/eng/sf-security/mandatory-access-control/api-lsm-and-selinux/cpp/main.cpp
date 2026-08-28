#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <format>
#include <selinux/selinux.h>
#include <selinux/context.h>

/* RAII-обгортка для рядків, виділених бібліотекою libselinux */
struct ContextDeleter {
    void operator()(char* ptr) const noexcept {
        if (ptr) {
            freecon(ptr);
        }
    }
};
using UniqueContextString = std::unique_ptr<char, ContextDeleter>;

/* RAII-обгортка для дескриптора структури context_t */
struct ContextHandleDeleter {
    void operator()(context_s_t* ptr) const noexcept {
        if (ptr) {
            context_free(ptr);
        }
    }
};
using UniqueContextHandle = std::unique_ptr<context_s_t, ContextHandleDeleter>;

struct SecurityLabel {
    std::string full_string;
    std::string user;
    std::string role;
    std::string type;
    std::string mls_range;
};

class SELinuxAPI {
public:
    [[nodiscard]] static bool is_active() noexcept {
        return is_selinux_enabled() == 1;
    }

    [[nodiscard]] static std::string get_mode_name() noexcept {
        const int mode = security_getenforce();
        if (mode == 1) return "Enforcing (блокування порушень)";
        if (mode == 0) return "Permissive (лише аудит)";
        return "Disabled (повністю вимкнено)";
    }

    [[nodiscard]] static std::expected<SecurityLabel, std::string> get_process_label() {
        char* raw_con = nullptr;
        if (getcon(&raw_con) < 0 || !raw_con) {
            return std::unexpected("Не вдалося отримати контекст процесу через getcon()");
        }
        UniqueContextString raw_guard(raw_con);

        UniqueContextHandle handle(context_new(raw_guard.get()));
        if (!handle) {
            return std::unexpected("Помилка розбору структури контексту через context_new()");
        }

        const char* range_ptr = context_range_get(handle.get());

        return SecurityLabel{
            .full_string = raw_guard.get(),
            .user = context_user_get(handle.get()) ? context_user_get(handle.get()) : "",
            .role = context_role_get(handle.get()) ? context_role_get(handle.get()) : "",
            .type = context_type_get(handle.get()) ? context_type_get(handle.get()) : "",
            .mls_range = range_ptr ? range_ptr : "s0"
        };
    }

    [[nodiscard]] static std::expected<std::string, std::string> get_file_label(std::string_view path) {
        char* raw_con = nullptr;
        if (getfilecon(path.data(), &raw_con) < 0 || !raw_con) {
            return std::unexpected("Не вдалося зчитати xattr security.selinux для " + std::string(path));
        }
        UniqueContextString raw_guard(raw_con);
        return std::string(raw_guard.get());
    }
};

int main() {
    if (!SELinuxAPI::is_active()) {
        std::cout << "Підсистема SELinux не активна в поточній операційній системі.\n";
        return 0;
    }

    std::cout << "Режим SELinux: " << SELinuxAPI::get_mode_name() << "\n";

    if (auto proc = SELinuxAPI::get_process_label(); proc.has_value()) {
        std::cout << "Контекст поточного процесу: " << proc->full_string << "\n"
                  << "  ├── Користувач: " << proc->user << "\n"
                  << "  ├── Роль:       " << proc->role << "\n"
                  << "  ├── Домен/Тип:  " << proc->type << "\n"
                  << "  └── Рівень MLS: " << proc->mls_range << "\n";
    } else {
        std::cerr << proc.error() << "\n";
        return 1;
    }

    if (auto file = SELinuxAPI::get_file_label("/etc/shadow"); file.has_value()) {
        std::cout << "Мітка безпеки [/etc/shadow]: " << *file << "\n";
    } else {
        std::cerr << file.error() << "\n";
        return 1;
    }

    return 0;
}
