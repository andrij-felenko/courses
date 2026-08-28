#include <stdio.h>
#include <stdlib.h>

#ifdef _OPENMP
#include <omp.h>
#endif

long long kadane_parallel_openmp(const int* arr, int n, int num_threads) {
    if (arr == NULL || n <= 0) {
        return 0;
    }
    if (num_threads <= 1 || n < 10000) {
        return kadane_branchless(arr, n);
    }

    SegmentNode* partial_results = (SegmentNode*)malloc(sizeof(SegmentNode) * num_threads);
    if (partial_results == NULL) {
        return kadane_branchless(arr, n);
    }

    #pragma omp parallel num_threads(num_threads)
    {
        #ifdef _OPENMP
        int tid = omp_get_thread_num();
        int nthreads = omp_get_num_threads();
        #else
        int tid = 0, nthreads = 1;
        #endif

        int chunk_size = n / nthreads;
        int l = tid * chunk_size;
        int r = (tid == nthreads - 1) ? (n - 1) : (l + chunk_size - 1);

        if (l <= r) {
            long long tot = arr[l];
            long long pref = arr[l];
            long long cur_pref = arr[l];
            long long sub = arr[l];
            long long cur_sub = arr[l];

            for (int i = l + 1; i <= r; ++i) {
                long long x = arr[i];
                tot += x;
                cur_pref += x;
                if (cur_pref > pref) pref = cur_pref;

                cur_sub = (cur_sub > 0 ? cur_sub : 0) + x;
                if (cur_sub > sub) sub = cur_sub;
            }

            long long suff = arr[r];
            long long cur_suff = arr[r];
            for (int i = r - 1; i >= l; --i) {
                cur_suff += arr[i];
                if (cur_suff > suff) suff = cur_suff;
            }

            SegmentNode node;
            node.total_sum = tot;
            node.max_prefix = pref;
            node.max_suffix = suff;
            node.max_subarray = sub;
            partial_results[tid] = node;
        }
    }

    SegmentNode final_acc = partial_results[0];
    for (int t = 1; t < num_threads; ++t) {
        final_acc = merge_nodes(final_acc, partial_results[t]);
    }

    free(partial_results);
    return final_acc.max_subarray;
}
