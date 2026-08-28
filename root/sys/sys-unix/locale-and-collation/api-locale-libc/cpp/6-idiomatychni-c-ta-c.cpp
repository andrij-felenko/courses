// C++17: Ідіоматичний підхід через std::locale, std::collate та RAII
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <locale>
#include <stdexcept>

class ThreadSafeCollator {
private:
    std::locale loc_;

public:
    explicit ThreadSafeCollator(const std::string& locale_name) 
        : loc_(locale_name) {}

    void sort_strings(std::vector<std::string>& strings) const {
        // Отримання фасету зіставлення std::collate з об'єкта локалі
        const auto& coll = std::use_facet<std::collate<char>>(loc_);

        // Кешування трансформаційних ключів через std::collate::transform
        struct KeyEntry {
            std::string original;
            std::string key;
        };

        std::vector<KeyEntry> entries;
        entries.reserve(strings.size());

        for (const auto& str : strings) {
            std::string key = coll.transform(str.data(), str.data() + str.size());
            entries.push_back({str, std::move(key)});
        }

        // Швидке порівняння преображених ключів
        std::sort(entries.begin(), entries.end(), 
            [](const KeyEntry& a, const KeyEntry& b) {
                return a.key < b.key;
            });

        for (size_t i = 0; i < strings.size(); ++i) {
            strings[i] = std::move(entries[i].original);
        }
    }
};
