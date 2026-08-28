#include <algorithm>
#include <vector>
using std::vector;

void merge_sort_bottomup(vector<int>& a) {
    int n = (int)a.size();
    vector<int> buf(n);                              // один раз
    for (int width = 1; width < n; width *= 2)       // ширина купок: 1, 2, 4, …
        for (int lo = 0; lo < n; lo += 2 * width) {
            int mid = std::min(lo + width, n);       // кінець лівої купки
            int hi  = std::min(lo + 2 * width, n);   // кінець правої купки
            if (mid < hi)                            // права непорожня
                merge(a, buf, lo, mid, hi);
        }
}
