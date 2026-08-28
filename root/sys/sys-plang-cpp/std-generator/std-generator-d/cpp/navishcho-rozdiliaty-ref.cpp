#include <generator>
#include <string>
#include <vector>

class DatabaseReader {
    std::vector<std::string> cache_;
public:
    // Повертаємо константне посилання на елемент у кеші
    std::generator<const std::string&> stream_records() {
        for (const auto& record : cache_) {
            co_yield record; // Ніякого копіювання std::string!
        }
    }
};
