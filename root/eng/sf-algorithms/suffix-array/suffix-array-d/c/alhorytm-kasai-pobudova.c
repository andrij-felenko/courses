/* Побудова масиву LCP за алгоритмом Касаї за O(N) */
void build_lcp_kasai(const char *text, int n, const int *sa, const int *rank, int *lcp) {
    int h = 0;
    for (int i = 0; i < n; ++i) {
        if (rank[i] > 0) {
            int j = sa[rank[i] - 1];
            while (i + h < n && j + h < n && text[i + h] == text[j + h]) {
                h++;
            }
            lcp[rank[i]] = h;
            if (h > 0) h--;
        } else {
            lcp[0] = 0;
        }
    }
}
