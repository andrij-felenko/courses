#include <iostream>
#include <string_view>
#include <regex>
#include <system_error>
#include <regex.h>

class PosixRegexMatcher {
public:
    explicit PosixRegexMatcher(std::string_view pattern, bool extended = true) {
        int flags = REG_NOSUB;
        if (extended) {
            flags |= REG_EXTENDED;
        }

        // Копіюємо string_view у null-terminated рядок для POSIX C-API
        std::string pattern_str(pattern);
        int ret = ::regcomp(&compiled_regex_, pattern_str.c_str(), flags);
        if (ret != 0) {
            char err_buf[256];
            ::regerror(ret, &compiled_regex_, err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("Regex compilation error: ") + err_buf);
        }
        is_valid_ = true;
    }

    ~PosixRegexMatcher() noexcept {
        if (is_valid_) {
            ::regfree(&compiled_regex_);
        }
    }

    PosixRegexMatcher(const PosixRegexMatcher&) = delete;
    PosixRegexMatcher& operator=(const PosixRegexMatcher&) = delete;

    PosixRegexMatcher(PosixRegexMatcher&& other) noexcept
        : compiled_regex_(other.compiled_regex_), is_valid_(other.is_valid_) {
        other.is_valid_ = false;
    }

    PosixRegexMatcher& operator=(PosixRegexMatcher&& other) noexcept {
        if (this != &other) {
            if (is_valid_) {
                ::regfree(&compiled_regex_);
            }
            compiled_regex_ = other.compiled_regex_;
            is_valid_ = other.is_valid_;
            other.is_valid_ = false;
        }
        return *this;
    }

    [[nodiscard]] bool matches(std::string_view text) const noexcept {
        if (!is_valid_) return false;
        std::string text_str(text);
        return ::regexec(&compiled_regex_, text_str.c_str(), 0, nullptr, 0) == 0;
    }

private:
    regex_t compiled_regex_{};
    bool is_valid_{false};
};

int main() {
    try {
        PosixRegexMatcher matcher("^[0-9]{4}-[0-9]{2}-[0-9]{2}");
        std::string_view line = "2026-08-25 [INFO] Сервіс запущено";

        if (matcher.matches(line)) {
            std::cout << "Знайдено дату на початку рядка\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
