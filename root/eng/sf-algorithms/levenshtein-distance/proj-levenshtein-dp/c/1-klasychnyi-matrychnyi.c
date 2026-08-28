#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int distance;
    char* aligned_s1;
    char* aligned_s2;
    char* cigar;
} alignment_result_t;

static int min3(int a, int b, int c) {
    int m = (a < b) ? a : b;
    return (m < c) ? m : c;
}

alignment_result_t align_levenshtein(const char* s1, const char* s2) {
    alignment_result_t res = {0, NULL, NULL, NULL};
    size_t n = strlen(s1);
    size_t m = strlen(s2);

    int** dp = (int**)malloc((n + 1) * sizeof(int*));
    if (!dp) return res;
    for (size_t i = 0; i <= n; ++i) {
        dp[i] = (int*)malloc((m + 1) * sizeof(int));
        if (!dp[i]) {
            for (size_t k = 0; k < i; ++k) free(dp[k]);
            free(dp);
            return res;
        }
    }

    for (size_t i = 0; i <= n; ++i) dp[i][0] = (int)i;
    for (size_t j = 0; j <= m; ++j) dp[0][j] = (int)j;

    for (size_t i = 1; i <= n; ++i) {
        for (size_t j = 1; j <= m; ++j) {
            int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            int del = dp[i - 1][j] + 1;
            int ins = dp[i][j - 1] + 1;
            int sub = dp[i - 1][j - 1] + cost;
            dp[i][j] = min3(del, ins, sub);
        }
    }

    res.distance = dp[n][m];

    size_t max_len = n + m + 1;
    char* out1 = (char*)malloc(max_len);
    char* out2 = (char*)malloc(max_len);
    char* cigar = (char*)malloc(max_len);

    size_t idx = 0;
    size_t ci = n, cj = m;

    while (ci > 0 || cj > 0) {
        if (ci > 0 && cj > 0 && dp[ci][cj] == dp[ci - 1][cj - 1] + ((s1[ci - 1] == s2[cj - 1]) ? 0 : 1)) {
            out1[idx] = s1[ci - 1];
            out2[idx] = s2[cj - 1];
            cigar[idx] = (s1[ci - 1] == s2[cj - 1]) ? 'M' : 'S';
            ci--; cj--;
        } else if (ci > 0 && dp[ci][cj] == dp[ci - 1][cj] + 1) {
            out1[idx] = s1[ci - 1];
            out2[idx] = '-';
            cigar[idx] = 'D';
            ci--;
        } else {
            out1[idx] = '-';
            out2[idx] = s2[cj - 1];
            cigar[idx] = 'I';
            cj--;
        }
        idx++;
    }

    out1[idx] = '\0';
    out2[idx] = '\0';
    cigar[idx] = '\0';

    for (size_t i = 0; i < idx / 2; ++i) {
        char t1 = out1[i]; out1[i] = out1[idx - 1 - i]; out1[idx - 1 - i] = t1;
        char t2 = out2[i]; out2[i] = out2[idx - 1 - i]; out2[idx - 1 - i] = t2;
        char tc = cigar[i]; cigar[i] = cigar[idx - 1 - i]; cigar[idx - 1 - i] = tc;
    }

    res.aligned_s1 = out1;
    res.aligned_s2 = out2;
    res.cigar = cigar;

    for (size_t i = 0; i <= n; ++i) free(dp[i]);
    free(dp);
    return res;
}
