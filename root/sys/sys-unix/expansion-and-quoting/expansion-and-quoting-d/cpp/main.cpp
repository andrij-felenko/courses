#include <iostream>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <wordexp.h>

class SafeWordExpander {
public:
    explicit SafeWordExpander(std::string_view pattern) {
        std::string null_terminated(pattern);
        int status = wordexp(null_terminated.c_str(), &p_, WRDE_NOCMD);
        if (status != 0) {
            if (status == WRDE_CMDSUB) {
                throw std::runtime_error("Спроба ін'єкції команд заборонена");
            }
            throw std::runtime_error("Помилка розгортання рядка");
        }
    }

    ~SafeWordExpander() noexcept {
        wordfree(&p_);
    }

    SafeWordExpander(const SafeWordExpander&) = delete;
    SafeWordExpander& operator=(const SafeWordExpander&) = delete;

    [[nodiscard]] std::size_t size() const noexcept { return p_.we_wordc; }
    [[nodiscard]] const char* operator[](std::size_t i) const noexcept { return p_.we_wordv[i]; }

private:
    wordexp_t p_{};
};

int main() {
    try {
        SafeWordExpander expander("$HOME/documents/*.txt \"проект 2026\"");
        for (std::size_t i = 0; i < expander.size(); ++i) {
            std::cout << "argv[" << i << "] = " << expander[i] << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
    }
    return 0;
}
