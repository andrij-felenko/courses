/* Допоміжне порозрядне сортування пар рангів (Rank[i], Rank[i+k]) */
static void count_sort(int *sa, const int *rank, int n, int k) {
    int *cnt = (int*)calloc((size_t)(n + 256 + 2), sizeof(int));
    int *temp_sa = (int*)malloc((size_t)n * sizeof(int));
    if (!cnt || !temp_sa) {
        free(cnt);
        free(temp_sa);
        return;
    }

    /* 1. Сортування за другим ключем: Rank[i + k] */
    int max_val = 0;
    for (int i = 0; i < n; ++i) {
        int val = (i + k < n) ? rank[i + k] + 1 : 0;
        cnt[val]++;
        if (val > max_val) max_val = val;
    }
    for (int i = 1; i <= max_val; ++i) {
        cnt[i] += cnt[i - 1];
    }
    for (int i = n - 1; i >= 0; --i) {
        int val = (sa[i] + k < n) ? rank[sa[i] + k] + 1 : 0;
        temp_sa[--cnt[val]] = sa[i];
    }

    /* 2. Сортування за першим ключем: Rank[temp_sa[i]] */
    memset(cnt, 0, (size_t)(max_val + 2) * sizeof(int));
    max_val = 0;
    for (int i = 0; i < n; ++i) {
        int val = rank[temp_sa[i]] + 1;
        cnt[val]++;
        if (val > max_val) max_val = val;
    }
    for (int i = 1; i <= max_val; ++i) {
        cnt[i] += cnt[i - 1];
    }
    for (int i = n - 1; i >= 0; --i) {
        int val = rank[temp_sa[i]] + 1;
        sa[--cnt[val]] = temp_sa[i];
    }

    free(cnt);
    free(temp_sa);
}
