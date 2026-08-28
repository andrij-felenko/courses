SuffixIndex* suffix_index_create(const char *src) {
    if (!src) return NULL;
    SuffixIndex *idx = (SuffixIndex*)malloc(sizeof(SuffixIndex));
    if (!idx) return NULL;

    idx->n = (int)strlen(src);
    idx->text = (char*)malloc((size_t)(idx->n + 1));
    idx->sa = (int*)malloc((size_t)idx->n * sizeof(int));
    idx->rank = (int*)malloc((size_t)idx->n * sizeof(int));
    idx->lcp = (int*)malloc((size_t)idx->n * sizeof(int));

    if (!idx->text || !idx->sa || !idx->rank || !idx->lcp) {
        suffix_index_destroy(idx);
        return NULL;
    }

    memcpy(idx->text, src, (size_t)idx->n + 1);
    int n = idx->n;

    for (int i = 0; i < n; ++i) {
        idx->sa[i] = i;
        idx->rank[i] = (unsigned char)src[i];
    }

    int *new_rank = (int*)malloc((size_t)n * sizeof(int));
    for (int k = 1; k < n; k <<= 1) {
        count_sort(idx->sa, idx->rank, n, k);

        new_rank[idx->sa[0]] = 0;
        int r = 0;
        for (int i = 1; i < n; ++i) {
            int prev = idx->sa[i - 1];
            int curr = idx->sa[i];
            int prev_r2 = (prev + k < n) ? idx->rank[prev + k] : -1;
            int curr_r2 = (curr + k < n) ? idx->rank[curr + k] : -1;

            if (idx->rank[prev] != idx->rank[curr] || prev_r2 != curr_r2) {
                r++;
            }
            new_rank[curr] = r;
        }
        memcpy(idx->rank, new_rank, (size_t)n * sizeof(int));
        if (r == n - 1) break;
    }
    free(new_rank);

    build_lcp_and_sparse_table(idx);
    return idx;
}

void suffix_index_destroy(SuffixIndex *idx) {
    if (!idx) return;
    if (idx->st) {
        for (int k = 0; k < idx->max_log; ++k) {
            free(idx->st[k]);
        }
        free(idx->st);
    }
    free(idx->text);
    free(idx->sa);
    free(idx->rank);
    free(idx->lcp);
    free(idx);
}

SearchResult suffix_index_search(const SuffixIndex *idx, const char *pattern) {
    SearchResult res = {-1, -1, 0};
    if (!idx || !pattern || idx->n == 0) return res;

    int m = (int)strlen(pattern);
    if (m == 0) return res;

    int low = 0, high = idx->n - 1;
    int first = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        int cmp = strncmp(idx->text + idx->sa[mid], pattern, (size_t)m);
        if (cmp >= 0) {
            first = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (first == -1 || strncmp(idx->text + idx->sa[first], pattern, (size_t)m) != 0) {
        return res;
    }

    low = first;
    high = idx->n - 1;
    int last = first;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        int cmp = strncmp(idx->text + idx->sa[mid], pattern, (size_t)m);
        if (cmp == 0) {
            last = mid;
            low = mid + 1;
        } else if (cmp < 0) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    res.left = first;
    res.right = last;
    res.count = last - first + 1;
    return res;
}

int suffix_index_longest_repeated(const SuffixIndex *idx, int *out_pos) {
    if (!idx || idx->n <= 1) return 0;
    int max_len = 0;
    int best_sa_idx = -1;

    for (int i = 1; i < idx->n; ++i) {
        if (idx->lcp[i] > max_len) {
            max_len = idx->lcp[i];
            best_sa_idx = idx->sa[i];
        }
    }

    if (out_pos && best_sa_idx != -1) {
        *out_pos = best_sa_idx;
    }
    return max_len;
}

long long suffix_index_distinct_substrings(const SuffixIndex *idx) {
    if (!idx || idx->n == 0) return 0;
    long long total = 0;
    for (int i = 0; i < idx->n; ++i) {
        total += (idx->n - idx->sa[i]) - idx->lcp[i];
    }
    return total;
}
