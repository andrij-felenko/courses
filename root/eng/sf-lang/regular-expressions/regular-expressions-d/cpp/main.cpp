#include <iostream>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <regex.h>

// Безпечна RAII-обгортка над POSIX regex_t
class RegexEngine {
public:
    explicit RegexEngine(std::string_view pattern, int flags = REG_EXTENDED) {
        std::string null_terminated(pattern);
        int ret = regcomp(&reg_, null_terminated.c_str(), flags);
        if (ret != 0) {
            char buf[128];
            regerror(ret, &reg_, buf, sizeof(buf));
            throw std::runtime_error(std::string("regcomp failed: ") + buf);
        }
    }

    ~RegexEngine() noexcept {
        regfree(&reg_);
    }

    // Заборона небезпечного копіювання
    RegexEngine(const RegexEngine&) = delete;
    RegexEngine& operator=(const RegexEngine&) = delete;

    // Дозвіл переміщення ресурсу
    RegexEngine(RegexEngine&& other) noexcept {
        reg_ = other.reg_;
        other.reg_ = {};
    }

    RegexEngine& operator=(RegexEngine&& other) noexcept {
        if (this != &other) {
            regfree(&reg_);
            reg_ = other.reg_;
            other.reg_ = {};
        }
        return *this;
    }

    std::vector<std::string_view> search(std::string_view text, size_t max_groups = 4) const {
        std::vector<regmatch_t> pmatch(max_groups);
        std::string null_terminated(text);

        int ret = regexec(&reg_, null_terminated.c_str(), max_groups, pmatch.data(), 0);
        if (ret == REG_NOMATCH) {
            return {};
        }
        if (ret != 0) {
            char buf[128];
            regerror(ret, &reg_, buf, sizeof(buf));
            throw std::runtime_error(std::string("regexec failed: ") + buf);
        }

        std::vector<std::string_view> groups;
        groups.reserve(max_groups);

        for (size_t i = 0; i < max_groups; ++i) {
            if (pmatch[i].rm_so == -1) {
                groups.emplace_back("");
            } else {
                size_t start = static_cast<size_t>(pmatch[i].rm_so);
                size_t len = static_cast<size_t>(pmatch[i].rm_eo - pmatch[i].rm_so);
                groups.emplace_back(text.substr(start, len));
            }
        }
        return groups;
    }

private:
    regex_t reg_{};
};

int main() {
    try {
        RegexEngine re("^([a-zA-Z_][a-zA-Z0-9_]*)=([0-9]+)$");

        std::string_view line = "timeout_ms=5000";
        auto matches = re.search(line, 3);

        if (!matches.empty()) {
            std::cout << "Змінна: " << matches[1] << "\n";
            std::cout << "Значення: " << matches[2] << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Виняток: " << e.what() << "\n";
    }
    return 0;
}
