#include <fstream>
#include <string>
#include <iterator>

std::string read_entire_file(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    // Читання всього файла в пам'ять за один виклик алгоритму
    return std::string(std::istreambuf_iterator<char>(file),
                       std::istreambuf_iterator<char>());
}
