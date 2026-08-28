#include <stdio.h>

typedef struct {
    long long max_sum;
    int start;
    int end;
} SubarrayIndices;

SubarrayIndices kadane_track_bounds(const int* arr, int n) {
    SubarrayIndices res = {0, -1, -1};
    if (arr == NULL || n <= 0) return res;

    long long current_sum = arr[0];
    long long max_sum = arr[0];
    int current_start = 0;
    int best_start = 0;
    int best_end = 0;

    for (int i = 1; i < n; ++i) {
        if (current_sum < 0) {
            current_sum = arr[i];
            current_start = i;
        } else {
            current_sum += arr[i];
        }

        if (current_sum > max_sum) {
            max_sum = current_sum;
            best_start = current_start;
            best_end = i;
        }
    }

    res.max_sum = max_sum;
    res.start = best_start;
    res.end = best_end;
    return res;
}
