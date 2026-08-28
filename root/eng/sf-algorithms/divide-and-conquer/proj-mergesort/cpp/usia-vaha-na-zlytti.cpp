#include <vector>
using std::vector;

// Зливає a[lo,mid) і a[mid,hi) через buf, переносить назад у a[lo,hi).
static void merge(vector<int>& a, vector<int>& buf, int lo, int mid, int hi) {
    int i = lo, j = mid, k = lo;        // i — по лівій, j — по правій, k — по buf
    while (i < mid && j < hi)
        buf[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];   // ≤ → з лівої на рівних
    while (i < mid) buf[k++] = a[i++];  // лівий хвіст
    while (j < hi)  buf[k++] = a[j++];  // правий хвіст
    for (int t = lo; t < hi; ++t) a[t] = buf[t];       // перенести назад
}
