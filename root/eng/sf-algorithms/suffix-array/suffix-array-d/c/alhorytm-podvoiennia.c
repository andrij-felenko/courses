/* Алгоритм побудови SA подвоєнням префіксів за O(N log N) */
void build_suffix_array(const char *text, int n, int *sa, int *rank) {
    int *cnt = (int*)calloc((size_t)(n + 256 + 2), sizeof(int));
    int *temp_sa = (int*)malloc((size_t)n * sizeof(int));
    int *new_rank = (int*)malloc((size_t)n * sizeof(int));

    /* 1. Ініціалізація рангами одиничних символів */
    for (int i = 0; i < n; ++i) {
        sa[i] = i;
        rank[i] = (unsigned char)text[i];
    }

    /* 2. Подвоєння k = 1, 2, 4, 8... */
    for (int k = 1; k < n; k <<= 1) {
        /* Двопрохідний Counting Sort за парою (rank[i], rank[i+k]) */
        for (int step = 1; step >= 0; --step) {
            int offset = (step == 1) ? k : 0;
            int max_val = 0;
            for (int i = 0; i < n; ++i) {
                int val = (i + offset < n) ? rank[i + offset] + 1 : 0;
                if (val > max_val) max_val = val;
            }
            memset(cnt, 0, (size_t)(max_val + 2) * sizeof(int));
            for (int i = 0; i < n; ++i) {
                int val = (i + offset < n) ? rank[i + offset] + 1 : 0;
                cnt[val]++;
            }
            for (int i = 1; i <= max_val + 1; ++i) cnt[i] += cnt[i - 1];
            for (int i = n - 1; i >= 0; --i) {
                int val = (sa[i] + offset < n) ? rank[sa[i] + offset] + 1 : 0;
                temp_sa[--cnt[val]] = sa[i];
            }
            memcpy(sa, temp_sa, (size_t)n * sizeof(int));
        }

        /* Перерахунок нових рангів */
        new_rank[sa[0]] = 0;
        int r = 0;
        for (int i = 1; i < n; ++i) {
            int prev = sa[i - 1];
            int curr = sa[i];
            int prev_r2 = (prev + k < n) ? rank[prev + k] : -1;
            int curr_r2 = (curr + k < n) ? rank[curr + k] : -1;
            if (rank[prev] != rank[curr] || prev_r2 != curr_r2) {
                r++;
            }
            new_rank[curr] = r;
        }
        memcpy(rank, new_rank, (size_t)n * sizeof(int));
        if (r == n - 1) break; /* Усі ранги унікальні — сортування завершено */
    }

    free(cnt);
    free(temp_sa);
    free(new_rank);
}
