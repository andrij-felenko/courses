#include <vector>
#include <algorithm>
#include <utility>

template <typename T, typename Compare = std::less<T>>
void heapify_bottom_up(std::vector<T>& arr, Compare comp = Compare{}) {
    int n = static_cast<int>(arr.size());
    for (int i = (n / 2) - 1; i >= 0; --i) {
        int curr = i;
        while (2 * curr + 1 < n) {
            int left = 2 * curr + 1;
            int right = 2 * curr + 2;
            int best = left;

            if (right < n && comp(arr[right], arr[left])) {
                best = right;
            }
            if (comp(arr[best], arr[curr])) {
                std::swap(arr[curr], arr[best]);
                curr = best;
            } else {
                break;
            }
        }
    }
}
