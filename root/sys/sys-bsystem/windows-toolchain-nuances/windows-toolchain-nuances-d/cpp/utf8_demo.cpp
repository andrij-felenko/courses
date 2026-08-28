// utf8_demo.cpp — коректний вивід UTF-8 у консоль Windows мовою C++
#include <windows.h>
#include <iostream>
#include <string_view>

class ScopedConsoleEncoding {
public:
    explicit ScopedConsoleEncoding(UINT target_cp = CP_UTF8) noexcept
        : previous_cp_(GetConsoleOutputCP()) {
        SetConsoleOutputCP(target_cp);
    }

    ~ScopedConsoleEncoding() noexcept {
        SetConsoleOutputCP(previous_cp_);
    }

    ScopedConsoleEncoding(const ScopedConsoleEncoding&) = delete;
    ScopedConsoleEncoding& operator=(const ScopedConsoleEncoding&) = delete;

private:
    UINT previous_cp_;
};

int main() {
    const ScopedConsoleEncoding encoding_guard;

    constexpr std::string_view message = "Український текст: Вітання зі світу системної збірки!";
    constexpr std::string_view symbols = "Спеціальні символи Unicode: ⚡ 🚀 🔧 [OK]";

    std::cout << message << "\n" << symbols << std::endl;
    return 0;
}
