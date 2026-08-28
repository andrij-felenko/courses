#include <span>
#include <functional>

// Еквівалентний шаблон C++ без використання макросів препроцесора
template <typename T, auto LessThan = std::less<T>{}>
void static_insertion_sort(std::span<T> data) {
    if (data.size() <= 1) return;
    for (std::size_t i = 1; i < data.size(); ++i) {
        T key = std::move(data[i]);
        std::size_t j = i;
        while (j > 0 && LessThan(key, data[j - 1])) {
            data[j] = std::move(data[j - 1]);
            --j;
        }
        data[j] = std::move(key);
    }
}
