// Недетерміністичний підхід: використання макросів часу та системних шляхів
#include <iostream>
#include <source_location>

void log_module_info() {
    // Порушення 1: фіксація часу компіляції
    std::cout << "Build timestamp: " << __DATE__ << " " << __TIME__ << "\n";
    // Порушення 2: витік структури каталогів хоста
    const auto location = std::source_location::current();
    std::cout << "Compiled from source: " << location.file_name() << "\n";
}
