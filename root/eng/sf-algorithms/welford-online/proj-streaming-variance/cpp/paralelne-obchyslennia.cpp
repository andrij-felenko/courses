#include <omp.h>

StreamingAccumulator<double> parallel_accumulate(std::span<const double> data) {
    StreamingAccumulator<double> global_acc;

    #pragma omp parallel
    {
        StreamingAccumulator<double> local_acc;

        #pragma omp for nowait
        for (size_t i = 0; i < data.size(); ++i) {
            local_acc.push(data[i]);
        }

        #pragma omp critical
        {
            global_acc += local_acc;
        }
    }

    return global_acc;
}
