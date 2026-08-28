#include <span>
#include <vector>
#include <numeric>
#include <algorithm>

struct HeavyRecordCpp {
    int id;
    double score;
    std::vector<char> payload;
};

/* Створення відсортованого індексного масиву без модифікації вихідних даних */
template <typename T, typename Compare>
std::vector<std::size_t> indirect_sort_indices(const std::vector<T>& items, Compare comp) {
    std::vector<std::size_t> indices(items.size());
    std::iota(indices.begin(), indices.end(), 0);

    for (std::size_t i = 1; i < indices.size(); ++i) {
        std::size_t key_idx = indices[i];
        std::size_t j = i;

        while (j > 0 && comp(items[key_idx], items[indices[j - 1]])) {
            indices[j] = indices[j - 1];
            --j;
        }
        indices[j] = key_idx;
    }

    return indices;
}
