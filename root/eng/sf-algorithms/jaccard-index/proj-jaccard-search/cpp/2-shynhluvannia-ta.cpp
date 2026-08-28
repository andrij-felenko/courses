#include <string_view>
#include <vector>
#include <algorithm>
#include <string>

// Ідіоматична C++ реалізація класу шинглування
class Shingler {
public:
    static std::vector<uint64_t> create_shingles(std::string_view text, size_t k) {
        if (text.size() < k) return {};

        size_t count = text.size() - k + 1;
        std::vector<uint64_t> shingles;
        shingles.reserve(count);

        std::hash<std::string_view> hasher;
        for (size_t i = 0; i < count; ++i) {
            shingles.push_back(hasher(text.substr(i, k)));
        }

        std::sort(shingles.begin(), shingles.end());
        shingles.erase(std::unique(shingles.begin(), shingles.end()), shingles.end());

        return shingles;
    }
};
