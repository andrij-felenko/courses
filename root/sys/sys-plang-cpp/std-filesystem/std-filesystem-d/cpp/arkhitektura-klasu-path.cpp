#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;

void parse_path_demo() {
    fs::path p = "/usr/local/bin/app.tar.gz";

    std::cout << "Повний шлях:       " << p << "\n";
    std::cout << "Кореневе ім'я:     " << p.root_name() << "\n";     // ""
    std::cout << "Кореневий каталог: " << p.root_directory() << "\n";// "/"
    std::cout << "Батьківський шлях: " << p.parent_path() << "\n";   // "/usr/local/bin"
    std::cout << "Ім'я файлу:        " << p.filename() << "\n";      // "app.tar.gz"
    std::cout << "Базове ім'я:       " << p.stem() << "\n";          // "app.tar"
    std::cout << "Розширення:        " << p.extension() << "\n";     // ".gz"
}
