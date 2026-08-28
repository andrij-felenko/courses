#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <stdexcept>
#include <regex.h>

// Безпечна RAII-обгортка для керування ресурсами regex_t у C++20
class PosixRegex {
public:
    explicit PosixRegex(std::string_view pattern, int flags = REG_EXTENDED) {
        // POSIX C API вимагає нуль-термінованого рядка
        std::string null_terminated_pat(pattern);
        int ret = regcomp(&regex_, null_terminated_pat.c_str(), flags);
        if (ret != 0) {
            char err_buf[256];
            regerror(ret, &regex_, err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("Помилка компіляції regex: ") + err_buf);
        }
    }

    ~PosixRegex() noexcept {
        regfree(&regex_);
    }

    // Заборона копіювання для запобігання подвійному виклику regfree
    PosixRegex(const PosixRegex&) = delete;
    PosixRegex& operator=(const PosixRegex&) = delete;

    // Дозвіл семантики переміщення
    PosixRegex(PosixRegex&& other) noexcept {
        regex_ = other.regex_;
        other.regex_ = {};
    }

    PosixRegex& operator=(PosixRegex&& other) noexcept {
        if (this != &other) {
            regfree(&regex_);
            regex_ = other.regex_;
            other.regex_ = {};
        }
        return *this;
    }

    // Пошук з поверненням легких зрізів std::string_view без зайвих копіювань
    std::vector<std::string_view> match(std::string_view text, size_t max_groups = 8) const {
        std::vector<regmatch_t> pmatch(max_groups);
        std::string null_terminated_text(text);

        int ret = regexec(&regex_, null_terminated_text.c_str(), max_groups, pmatch.data(), 0);
        if (ret == REG_NOMATCH) {
            return {};
        }
        if (ret != 0) {
            char err_buf[256];
            regerror(ret, &regex_, err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("Помилка виконання regex: ") + err_buf);
        }

        std::vector<std::string_view> results;
        results.reserve(max_groups);

        for (size_t i = 0; i < max_groups; ++i) {
            if (pmatch[i].rm_so == -1) {
                results.emplace_back(""); // Група не брала участі у збігу
            } else {
                size_t start = static_cast<size_t>(pmatch[i].rm_so);
                size_t len = static_cast<size_t>(pmatch[i].rm_eo - pmatch[i].rm_so);
                results.emplace_back(text.substr(start, len));
            }
        }
        return results;
    }

private:
    regex_t regex_{};
};

int main() {
    try {
        PosixRegex re("^([A-Z]+) \\[([0-9]{4}-[0-9]{2}-[0-9]{2})\\] (.+)$");
        std::string_view log1 = "ERROR [2026-08-26] Disk array degraded on node-04";

        auto groups = re.match(log1, 4);
        if (!groups.empty()) {
            std::cout << "Повний збіг: " << groups[0] << "\n";
            std::cout << "Рівень: " << groups[1] << "\n";
            std::cout << "Дата: " << groups[2] << "\n";
            std::cout << "Повідомлення: " << groups[3] << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
    }
    return 0;
}
