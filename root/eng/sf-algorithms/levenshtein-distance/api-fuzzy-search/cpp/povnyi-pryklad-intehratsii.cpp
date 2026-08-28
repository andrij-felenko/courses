#include <iostream>
#include "fuzzy_matcher.hpp"

int main() {
    fuzzy::FuzzyMatcher<int> matcher;

    matcher.insert("kitten", 101);
    matcher.insert("sitting", 102);
    matcher.insert("kitchen", 103);
    matcher.insert("cat", 104);
    matcher.insert("caterpillar", 105);

    fuzzy::SearchOptions opts{
        .max_distance = 2,
        .prefix_freeze_len = 0,
        .allow_transposition = true,
        .max_results = 10
    };

    std::cout << "Пошук для запиту 'kiten':
";
    auto results = matcher.search("kiten", opts);

    for (const auto& res : results) {
        std::cout << "  -> Знайдено: " << res.word 
                  << " (відстань: " << res.distance 
                  << ", id: " << res.user_data << ")
";
    }

    return 0;
}
