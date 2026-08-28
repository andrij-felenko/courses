// 1. Проекція з фіксацією частини параметрів
template <typename Value>
using StringMap = std::unordered_map<std::string, Value>;

// 2. Спрощення доступу до асоційованих типів трансформацій
template <typename T>
using decay_t = typename std::decay<T>::type;

template <bool B, typename T = void>
using enable_if_t = typename std::enable_if<B, T>::type;

// Використання у коді:
StringMap<int> registry; // Еквівалентно std::unordered_map<std::string, int>
