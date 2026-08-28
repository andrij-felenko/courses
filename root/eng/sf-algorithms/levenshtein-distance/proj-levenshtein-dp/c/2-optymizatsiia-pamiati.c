#include <stdlib.h>
#include <string.h>

int levenshtein_distance_fast(const char* s1, const char* s2) {
    size_t n = strlen(s1);
    size_t m = strlen(s2);

    if (n < m) {
        const char* tmp_s = s1; s1 = s2; s2 = tmp_s;
        size_t tmp_len = n; n = m; m = tmp_len;
    }

    int* dp = (int*)malloc((m + 1) * sizeof(int));
    if (!dp) return -1;

    for (size_t j = 0; j <= m; ++j) {
        dp[j] = (int)j;
    }

    for (size_t i = 1; i <= n; ++i) {
        int diag = dp[0];
        dp[0] = (int)i;
        char c1 = s1[i - 1];

        for (size_t j = 1; j <= m; ++j) {
            int temp = dp[j];
            int cost = (c1 == s2[j - 1]) ? 0 : 1;
            
            int del = dp[j] + 1;
            int ins = dp[j - 1] + 1;
            int sub = diag + cost;

            int val = (del < ins) ? del : ins;
            if (sub < val) val = sub;

            dp[j] = val;
            diag = temp;
        }
    }

    int res = dp[m];
    free(dp);
    return res;
}
