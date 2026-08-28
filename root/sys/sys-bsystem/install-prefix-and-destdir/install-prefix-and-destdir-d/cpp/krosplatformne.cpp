#include <iostream>
#include <filesystem>
#include <string>
#include <unistd.h>

namespace fs = std::filesystem;

fs::path get_app_datadir() {
    char exe_path[1024];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len == -1) {
        // Fallback до зашитого префікса за замовчуванням
        return fs::path("/usr/local/share/myapp");
    }
    exe_path[len] = '\0';

    // Отримуємо каталог виконуваного файлу і будуємо шлях до share/
    fs::path bin_dir = fs::path(exe_path).parent_path();
    return bin_dir.parent_path() / "share" / "myapp";
}
