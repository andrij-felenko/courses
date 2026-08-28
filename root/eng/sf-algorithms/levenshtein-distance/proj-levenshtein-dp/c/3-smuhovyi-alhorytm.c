#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define INF (INT_MAX / 2)

int levenshtein_banded_ukkonen(const char* s1, const char* s2, int k) {
    int n = (int)strlen(s1);
    int m = (int)strlen(s2);

    if (abs(n - m) > k) return k + 1;

    int* prev = (int*)malloc((m + 1) * sizeof(int));
    int* curr = (int*)malloc((m + 1) * sizeof(int));
    if (!prev || !curr) {
        free(prev); free(curr);
        return -1;
    }

    for (int j = 0; j <= m; ++j) {
        prev[j] = (j <= k) ? j : INF;
    }

    for (int i = 1; i <= n; ++i) {
        int min_j = (i - k > 0) ? i - k : 0;
        int max_j = (i + k < m) ? i + k : m;

        for (int j = 0; j <= m; ++j) curr[j] = INF;
        if (min_j == 0) curr[0] = i;

        int row_min = curr[0];

        for (int j = (min_j > 1 ? min_j : 1); j <= max_j; ++j) {
            int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            int del = prev[j] + 1;
            int ins = curr[j - 1] + 1;
            int sub = prev[j - 1] + cost;

            int val = (del < ins) ? del : ins;
            if (sub < val) val = sub;

            curr[j] = val;
            if (val < row_min) row_min = val;
        }

        if (row_min > k) {
            free(prev); free(curr);
            return k + 1;
        }

        int* tmp = prev; prev = curr; curr = tmp;
    }

    int result = prev[m];
    free(prev); free(curr);
    return (result <= k) ? result : (k + 1);
}
