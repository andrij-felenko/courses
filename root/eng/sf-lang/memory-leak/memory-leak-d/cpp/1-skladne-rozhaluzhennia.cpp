#include <fstream>
#include <memory>
#include <string>
#include <vector>

// Безпечний еквівалент на C++: пам'ять та файловий дескриптор
// гарантовано звільняються автоматично через деструктори (RAII)
int parse_config(const std::string &filename) {
    std::vector<char> header(128);
    std::vector<char> body(1024);

    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        return -2; // Ресурси header і body звільняються автоматично!
    }

    if (!file.read(header.data(), 128)) {
        return -3; // Ресурси та файл закриваються автоматично!
    }

    return 0;
}
