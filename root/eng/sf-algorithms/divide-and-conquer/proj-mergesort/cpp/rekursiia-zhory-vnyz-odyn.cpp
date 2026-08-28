#include <vector>
using std::vector;
static const int CUTOFF = 32;          // шматки ≤ 32 добиваємо вставками

static void insertion_sort(vector<int>& a, int lo, int hi) {
    for (int i = lo + 1; i < hi; ++i) {
        int key = a[i], j = i - 1;
        while (j >= lo && a[j] > key)  // > (не ≥) — стійкість
            a[j + 1] = a[j--];
        a[j + 1] = key;
    }
}

static void sort_rec(vector<int>& a, vector<int>& buf, int lo, int hi) {
    if (hi - lo <= CUTOFF) { insertion_sort(a, lo, hi); return; }
    int mid = lo + (hi - lo) / 2;      // НЕ (lo+hi)/2 — переповнення (про це нижче)
    sort_rec(a, buf, lo, mid);         // підкорити ліву
    sort_rec(a, buf, mid, hi);         // підкорити праву
    if (a[mid - 1] <= a[mid]) return;  // уже впорядковано → злиття зайве
    merge(a, buf, lo, mid, hi);        // поєднати
}

void merge_sort(vector<int>& a) {
    vector<int> buf(a.size());         // буфер розміру n, ОДИН раз
    sort_rec(a, buf, 0, (int)a.size());
}
