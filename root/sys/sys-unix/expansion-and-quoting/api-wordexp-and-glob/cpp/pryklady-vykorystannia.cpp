#include <iostream>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <wordexp.h>

class WordExpander {
public:
    explicit WordExpander(std::string_view expr, bool allow_cmd = false) {
        int flags = WRDE_UNDEF;
        if (!allow_cmd) {
            flags |= WRDE_NOCMD;
        }

        std::string null_term_expr(expr);
        int res = wordexp(null_term_expr.c_str(), &p_, flags);
        if (res != 0) {
            handle_error(res);
        }
    }

    ~WordExpander() noexcept {
        wordfree(&p_);
    }

    WordExpander(const WordExpander&) = delete;
    WordExpander& operator=(const WordExpander&) = delete;
    WordExpander(WordExpander&& other) noexcept : p_(other.p_) {
        other.p_ = wordexp_t{};
    }
    WordExpander& operator=(WordExpander&& other) noexcept {
        if (this != &other) {
            wordfree(&p_);
            p_ = other.p_;
            other.p_ = wordexp_t{};
        }
        return *this;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return p_.we_wordc;
    }

    [[nodiscard]] std::string_view operator[](std::size_t idx) const {
        if (idx >= p_.we_wordc) {
            throw std::out_of_range("Індекс за межами масиву розгорнутих слів");
        }
        return p_.we_wordv[idx];
    }

    [[nodiscard]] char** data() noexcept {
        return p_.we_wordv;
    }

private:
    static void handle_error(int code) {
        switch (code) {
            case WRDE_CMDSUB:
                throw std::invalid_argument("Безпека: виконання команд у wordexp заборонено");
            case WRDE_BADVAL:
                throw std::invalid_argument("Невизначена змінна оточення");
            case WRDE_SYNTAX:
                throw std::invalid_argument("Синтаксична помилка у рядку");
            case WRDE_NOSPACE:
                throw std::bad_alloc();
            default:
                throw std::runtime_error("Помилка розгортання рядка");
        }
    }

    wordexp_t p_{};
};

int main() {
    try {
        WordExpander expander("$HOME/*.log \"file with space.txt\"");
        std::cout << "Отримано слів: " << expander.size() << '\n';
        for (std::size_t i = 0; i < expander.size(); ++i) {
            std::cout << "  [" << i << "] " << expander[i] << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
