static void build_lcp_and_sparse_table(SuffixIndex *idx) {
    int n = idx->n;
    const char *text = idx->text;
    const int *sa = idx->sa;
    const int *rank = idx->rank;
    int *lcp = idx->lcp;

    /* 1. Алгоритм Касаї: побудова LCP за O(N) */
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

    /* 2. Побудова Sparse Table для RMQ на LCP */
    int max_log = 0;
    while ((1 << max_log) <= n) max_log++;
    idx->max_log = max_log;

    idx->st = (int**)malloc((size_t)max_log * sizeof(int*));
    for (int k = 0; k < max_log; ++k) {
        idx->st[k] = (int*)malloc((size_t)n * sizeof(int));
    }

    for (int i = 0; i < n; ++i) {
        idx->st[0][i] = lcp[i];
    }

    for (int k = 1; k < max_log; ++k) {
        int span = 1 << (k - 1);
        for (int i = 0; i + (1 << k) <= n; ++i) {
            int a = idx->st[k - 1][i];
            int b = idx->st[k - 1][i + span];
            idx->st[k][i] = (a < b) ? a : b;
        }
    }
}

int suffix_index_query_lcp(const SuffixIndex *idx, int sa_a, int sa_b) {
    if (!idx || sa_a == sa_b) return idx ? idx->n - idx->sa[sa_a] : 0;
    if (sa_a > sa_b) {
        int tmp = sa_a; sa_a = sa_b; sa_b = tmp;
    }
    int l = sa_a + 1;
    int r = sa_b;
    int len = r - l + 1;
    int k = 31 - __builtin_clz((unsigned int)len);
    int a = idx->st[k][l];
    int b = idx->st[k][r - (1 << k) + 1];
    return (a < b) ? a : b;
}
