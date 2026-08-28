#include <algorithm>
#include <vector>
using std::vector;

// Злиття БЕЗ переносу назад: читає зі src, пише в dst.
static void merge_into(const vector<int>& src, vector<int>& dst,
                       int lo, int mid, int hi) {
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi)
        dst[k++] = (src[i] <= src[j]) ? src[i++] : src[j++];
    while (i < mid) dst[k++] = src[i++];      // хвіст (сюди ж і поодинока купка,
    while (j < hi)  dst[k++] = src[j++];      // коли правої нема, — просто переносимо)
}

void merge_sort_pingpong(vector<int>& a) {
    int n = (int)a.size();
    vector<int> buf(a);                       // старт: копія масиву
    vector<int>* src = &buf;                  // читаємо з buf
    vector<int>* dst = &a;                    // пишемо в a
    for (int width = 1; width < n; width *= 2) {
        for (int lo = 0; lo < n; lo += 2 * width) {
            int mid = std::min(lo + width, n);
            int hi  = std::min(lo + 2 * width, n);
            merge_into(*src, *dst, lo, mid, hi);   // навіть поодиноку купку переносимо
        }
        std::swap(src, dst);                  // ролі міняються — жодного copy-back
    }
    if (src != &a) a = *src;                   // якщо результат осів у буфері — один перенос
}
