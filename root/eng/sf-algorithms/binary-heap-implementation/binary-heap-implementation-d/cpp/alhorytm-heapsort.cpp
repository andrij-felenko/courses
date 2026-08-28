#include <vector>
#include <algorithm>
#include <span>

template <typename T, typename Compare = std::less<T>>
void heapsort(std::span<T> arr, Compare comp = Compare{}) {
    int n = static_cast<int>(arr.size());
    if (n <= 1) return;

    auto sift_down = [&](int root, int heap_size) {
        int curr = root;
        while (2 * curr + 1 < heap_size) {
            int left = 2 * curr + 1;
            int right = 2 * curr + 2;
            int best = left;

            if (right < heap_size && comp(arr[left], arr[right])) {
                best = right;
            }
            if (comp(arr[curr], arr[best])) {
                std::swap(arr[curr], arr[best]);
                curr = best;
            } else {
                break;
            }
        }
    };

    // Фаза 1: побудова Max-купи знизу-вгору за O(N)
    for (int i = (n / 2) - 1; i >= 0; --i) {
        sift_down(i, n);
    }

    // Фаза 2: сортування вилученням за O(N log N)
    for (int end = n - 1; end > 0; --end) {
        std::swap(arr[0], arr[end]);
        sift_down(0, end);
    }
}
