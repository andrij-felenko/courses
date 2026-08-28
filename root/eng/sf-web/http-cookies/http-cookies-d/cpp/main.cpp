#include <string>
#include <string_view>
#include <sstream>
#include <optional>
#include <unordered_map>

namespace backend {

class CookieUtility {
public:
    // Парсер значення за іменем
    static std::optional<std::string> get_cookie(std::string_view cookie_header, std::string_view name) {
        if (cookie_header.empty() || name.empty()) {
            return std::nullopt;
        }

        size_t start = 0;
        while (start < cookie_header.size()) {
            size_t end = cookie_header.find(';', start);
            if (end == std::string_view::npos) end = cookie_header.size();

            std::string_view token = cookie_header.substr(start, end - start);
            // Видалення пробілів
            while (!token.empty() && token.front() == ' ') token.remove_prefix(1);
            while (!token.empty() && token.back() == ' ') token.remove_suffix(1);

            size_t eq_pos = token.find('=');
            if (eq_pos != std::string_view::npos) {
                std::string_view k = token.substr(0, eq_pos);
                std::string_view v = token.substr(eq_pos + 1);

                if (k == name) {
                    return std::string(v);
                }
            }
            start = end + 1;
        }
        return std::nullopt;
    }

    // Формування захищеного Set-Cookie
    static std::string make_host_session_cookie(std::string_view sid, int max_age_seconds = 86400) {
        std::ostringstream ss;
        ss << "__Host-sid=" << sid
           << "; Path=/"
           << "; Max-Age=" << max_age_seconds
           << "; HttpOnly"
           << "; Secure"
           << "; SameSite=Lax";
        return ss.str();
    }

    // Заголовок скидання
    static std::string make_logout_cookie() {
        return "__Host-sid=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax";
    }
};

} // namespace backend
