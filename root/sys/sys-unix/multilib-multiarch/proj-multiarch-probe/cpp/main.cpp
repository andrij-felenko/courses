#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <memory>
#include <dlfcn.h>
#include <link.h>

namespace fs = std::filesystem;

// RAII обгортка для безпечного керування дескриптором dlopen
class DynamicLibrary {
private:
    void* handle_{nullptr};

public:
    explicit DynamicLibrary(std::string_view name) {
        handle_ = ::dlopen(name.data(), RTLD_LAZY);
    }

    ~DynamicLibrary() {
        if (handle_) {
            ::dlclose(handle_);
        }
    }

    DynamicLibrary(const DynamicLibrary&) = delete;
    DynamicLibrary& operator=(const DynamicLibrary&) = delete;

    DynamicLibrary(DynamicLibrary&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    DynamicLibrary& operator=(DynamicLibrary&& other) noexcept {
        if (this != &other) {
            if (handle_) ::dlclose(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] bool is_loaded() const noexcept {
        return handle_ != nullptr;
    }

    [[nodiscard]] void* raw_handle() const noexcept {
        return handle_;
    }

    [[nodiscard]] std::string last_error() const {
        const char* err = ::dlerror();
        return err ? std::string(err) : std::string("невідома помилка");
    }
};

static void check_directory(const fs::path& path, std::string_view description) {
    std::error_code ec;
    if (fs::exists(path, ec) && fs::is_directory(path, ec)) {
        std::cout << "  [+] Знайдено каталог: " << path.string();
        if (path.string().length() < 30) {
            std::cout << std::string(30 - path.string().length(), ' ');
        }
        std::cout << " -> " << description << "\n";
    } else {
        std::cout << "  [-] Відсутній каталог: " << path.string();
        if (path.string().length() < 29) {
            std::cout << std::string(29 - path.string().length(), ' ');
        }
        std::cout << " -> " << description << "\n";
    }
}

static void inspect_loaded_library(std::string_view lib_name) {
    DynamicLibrary lib(lib_name);
    if (!lib.is_loaded()) {
        std::cout << "  [!] Помилка dlopen(" << lib_name << "): " << lib.last_error() << "\n";
        return;
    }

    // Запит структури link_map через dlinfo
    struct link_map* map = nullptr;
    if (::dlinfo(lib.raw_handle(), RTLD_DI_LINKMAP, &map) == 0 && map && map->l_name) {
        std::string_view path_view = map->l_name[0] ? map->l_name : "[впроваджено в процес]";
        std::cout << "  [=>] " << lib_name << " (dlinfo link_map) -> " << path_view << "\n";
    } else {
        std::cout << "  [!] Не вдалося отримати link_map для " << lib_name << "\n";
    }

    // Аналіз карт пам'яті /proc/self/maps
    std::ifstream maps("/proc/self/maps");
    if (!maps.is_open()) {
        std::cout << "  [!] Помилка відкриття /proc/self/maps\n";
        return;
    }

    std::string line;
    bool found = false;
    while (std::getline(maps, line)) {
        if (line.find(lib_name) != std::string::npos && line.find(".so") != std::string::npos) {
            auto pos = line.find('/');
            if (pos != std::string::npos) {
                std::string path = line.substr(pos);
                std::cout << "  [=>] " << lib_name << " (/proc/self/maps) -> " << path << "\n";
                found = true;
                break;
            }
        }
    }

    if (!found) {
        std::cout << "  [?] " << lib_name << " не знайдено серед мапінгів procfs\n";
    }
}

int main() {
    std::cout << "=========================================================\n";
    std::cout << "   ДІАГНОСТИКА АРХІТЕКТУРНОЇ ІЄРАРХІЇ БІБЛІОТЕК (C++17)\n";
    std::cout << "=========================================================\n\n";

    std::cout << "Параметри поточного бінарного процесу:\n";
    std::cout << "  • Модель пам'яті: " << (sizeof(void*) == 8 ? "LP64 (64-біт)" : "ILP32 (32-біт)") << "\n";
    std::cout << "  • Розмір вказівника: " << sizeof(void*) << " байтів\n\n";

    std::cout << "1. Перевірка наявності каталогів Multilib (RPM-модель):\n";
    check_directory("/lib64", "64-бітні бібліотеки системи");
    check_directory("/usr/lib64", "64-бітні бібліотеки користувача");
    check_directory("/lib32", "32-бітні бібліотеки системи (альтернативні)");
    check_directory("/usr/lib32", "32-бітні бібліотеки користувача (альтернативні)");
    std::cout << "\n";

    std::cout << "2. Перевірка наявності каталогів Multiarch (Debian GNU Triplets):\n";
    check_directory("/usr/lib/x86_64-linux-gnu", "x86_64-linux-gnu (AMD64 / Intel 64)");
    check_directory("/usr/lib/i386-linux-gnu", "i386-linux-gnu (x86 32-bit)");
    check_directory("/usr/lib/aarch64-linux-gnu", "aarch64-linux-gnu (ARM64)");
    check_directory("/usr/lib/arm-linux-gnueabihf", "arm-linux-gnueabihf (ARMhf)");
    std::cout << "\n";

    std::cout << "3. Тестування реальних шляхів резолюції бібліотек системним ld.so:\n";
    inspect_loaded_library("libm.so.6");
    inspect_loaded_library("libc.so.6");
    std::cout << "\n=========================================================\n";

    return 0;
}
