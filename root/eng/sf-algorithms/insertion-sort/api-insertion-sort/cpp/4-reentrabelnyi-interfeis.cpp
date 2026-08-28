#include <cstddef>
#include <functional>

// У C++ контекст природно інкапсулюється через лямбда-захоплення (Closures)
template <typename T, typename Context, typename CompareWithContext>
void insertion_sort_context(std::span<T> data, Context& ctx, CompareWithContext comp) {
    if (data.size() <= 1) return;
    for (std::size_t i = 1; i < data.size(); ++i) {
        T key = std::move(data[i]);
        std::size_t j = i;
        while (j > 0 && comp(key, data[j - 1], ctx)) {
            data[j] = std::move(data[j - 1]);
            --j;
        }
        data[j] = std::move(key);
    }
}
