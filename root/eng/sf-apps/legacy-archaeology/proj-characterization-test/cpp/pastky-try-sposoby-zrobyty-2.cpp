#include <unordered_map>
#include <map>
#include <algorithm>

// НЕ роби так: порядок обходу unordered_map не визначений ->
// знімок нестабільний -> хиткий golden-тест.
std::string renderBad(const std::unordered_map<std::string, double>& m) {
    std::ostringstream os;
    for (const auto& kv : m) os << kv.first << "=" << kv.second << "\n";  // ПАСТКА
    return os.str();
}

// Роби так: витягни ключі, ВІДСОРТУЙ, тоді серіалізуй у сталому порядку.
std::string renderStable(const std::unordered_map<std::string, double>& m) {
    std::vector<std::string> keys;
    keys.reserve(m.size());
    for (const auto& kv : m) keys.push_back(kv.first);
    std::sort(keys.begin(), keys.end());                 // детермінований порядок
    std::ostringstream os;
    os << std::fixed << std::setprecision(2);
    for (const auto& k : keys) os << k << "=" << m.at(k) << "\n";
    return os.str();
}
