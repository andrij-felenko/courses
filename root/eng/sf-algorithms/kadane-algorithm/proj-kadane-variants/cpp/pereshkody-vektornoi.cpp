#include <vector>
#include <span>
#include <algorithm>
#include <cstddef>

#ifdef _OPENMP
#include <omp.h>
#endif

[[nodiscard]] long long kadane_parallel_openmp(std::span<const int> arr, int num_threads) {
    if (arr.empty()) {
        return 0;
    }
    if (num_threads <= 1 || arr.size() < 10000) {
        return kadane_branchless(arr);
    }

    std::vector<SegmentNode> partial(num_threads);

    #pragma omp parallel num_threads(num_threads)
    {
        #ifdef _OPENMP
        const int tid = omp_get_thread_num();
        const int nthreads = omp_get_num_threads();
        #else
        const int tid = 0, nthreads = 1;
        #endif

        const std::size_t chunk = arr.size() / nthreads;
        const std::size_t l = tid * chunk;
        const std::size_t r = (tid == nthreads - 1) ? (arr.size() - 1) : (l + chunk - 1);

        if (l <= r) {
            long long tot = arr[l];
            long long pref = arr[l];
            long long cur_pref = arr[l];
            long long sub = arr[l];
            long long cur_sub = arr[l];

            for (std::size_t i = l + 1; i <= r; ++i) {
                const long long x = arr[i];
                tot += x;
                cur_pref += x;
                pref = std::max(pref, cur_pref);

                cur_sub = std::max<long long>(0, cur_sub) + x;
                sub = std::max(sub, cur_sub);
            }

            long long suff = arr[r];
            long long cur_suff = arr[r];
            for (std::size_t i = r; i > l; --i) {
                cur_suff += arr[i - 1];
                suff = std::max(suff, cur_suff);
            }

            partial[tid] = SegmentNode{
                .total_sum = tot,
                .max_prefix = pref,
                .max_suffix = suff,
                .max_subarray = sub
            };
        }
    }

    SegmentNode acc = partial[0];
    for (int t = 1; t < num_threads; ++t) {
        acc = SegmentNode::merge(acc, partial[t]);
    }

    return acc.max_subarray;
}
