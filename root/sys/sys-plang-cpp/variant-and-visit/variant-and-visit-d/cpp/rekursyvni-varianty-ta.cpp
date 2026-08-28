#include <variant>
#include <vector>
#include <string>
#include <memory>
#include <iostream>

struct File {
    std::string name;
    size_t size_bytes;
};

struct Directory;

// Рекурсивний тип через unique_ptr
using FSEntry = std::variant<File, std::unique_ptr<Directory>>;

struct Directory {
    std::string name;
    std::vector<FSEntry> entries;
};

int main() {
    Directory root{"root", {}};
    root.entries.push_back(File{"config.txt", 1024});
    
    std::cout << "Створено рекурсивну файлову систему з розміром коріння: " << root.entries.size() << "\n";
}
