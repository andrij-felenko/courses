#include <iostream>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <glob.h>

class PathGlobber {
public:
    explicit PathGlobber(std::string_view pattern, int flags = GLOB_MARK | GLOB_TILDE) {
        std::string null_term_pat(pattern);
        int status = glob(null_term_pat.c_str(), flags, nullptr, &gstruct_);
        if (status != 0 && status != GLOB_NOMATCH) {
            throw std::runtime_error("Помилка виконання глобінгу шляхів");
        }
    }

    ~PathGlobber() noexcept {
        globfree(&gstruct_);
    }

    PathGlobber(const PathGlobber&) = delete;
    PathGlobber& operator=(const PathGlobber&) = delete;

    [[nodiscard]] std::size_t size() const noexcept {
        return gstruct_.gl_pathc;
    }

    [[nodiscard]] std::string_view operator[](std::size_t i) const {
        if (i >= gstruct_.gl_pathc) {
            throw std::out_of_range("Індекс шляху за межами масиву");
        }
        return gstruct_.gl_pathv[i];
    }

private:
    glob_t gstruct_{};
};

int main() {
    try {
        PathGlobber globber("/var/log/*.log");
        std::cout << "Знайдено шляхів: " << globber.size() << '\n';
        for (std::size_t i = 0; i < globber.size(); ++i) {
            std::cout << "  " << globber[i] << '\n';
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
