#include <string_view>
#include <optional>

struct UserContext {
    bool is_authenticated{false};
    bool is_banned{false};
};

/* БЕЗПЕЧНО: C++20 ідіоматичний підхід із Default Deny за замовчуванням */
[[nodiscard]] bool check_access_secure(const UserContext& user, 
                                       std::string_view resource, 
                                       std::string_view client_ip) noexcept {
    if (!user.is_authenticated || user.is_banned) {
        return false;
    }

    // Дозвіл вимагає явного виконання всіх критеріїв безпеки
    const bool has_permission = (resource == "/public/status");
    const bool is_allowed_ip = (client_ip == "127.0.0.1");

    return has_permission && is_allowed_ip;
}
