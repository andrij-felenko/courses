#include <stddef.h>
#include <math.h>

typedef struct {
    double time;
    double value;
} data_point_t;

size_t lttb_downsample_c(const data_point_t *input, size_t input_len,
                         data_point_t *output, size_t threshold) {
    if (input == NULL || output == NULL || input_len == 0) return 0;
    if (threshold >= input_len || threshold < 3) {
        for (size_t i = 0; i < input_len; ++i) output[i] = input[i];
        return input_len;
    }

    output[0] = input[0];
    size_t out_idx = 1;
    size_t a_idx = 0;
    double bucket_size = (double)(input_len - 2) / (double)(threshold - 2);

    for (size_t i = 0; i < threshold - 2; ++i) {
        size_t curr_start = (size_t)(i * bucket_size) + 1;
        size_t curr_end = (size_t)((i + 1) * bucket_size) + 1;
        if (curr_end > input_len) curr_end = input_len;

        size_t next_start = (size_t)((i + 1) * bucket_size) + 1;
        size_t next_end = (size_t)((i + 2) * bucket_size) + 1;
        if (next_end > input_len) next_end = input_len;

        double avg_t = 0.0, avg_v = 0.0;
        size_t next_count = next_end - next_start;

        if (next_count > 0) {
            for (size_t j = next_start; j < next_end; ++j) {
                avg_t += input[j].time;
                avg_v += input[j].value;
            }
            avg_t /= (double)next_count;
            avg_v /= (double)next_count;
        } else {
            avg_t = input[input_len - 1].time;
            avg_v = input[input_len - 1].value;
        }

        double a_t = input[a_idx].time;
        double a_v = input[a_idx].value;
        double max_area = -1.0;
        size_t max_idx = curr_start;

        for (size_t p = curr_start; p < curr_end; ++p) {
            double p_t = input[p].time;
            double p_v = input[p].value;
            double area = fabs((a_t - avg_t) * (p_v - a_v) - (a_t - p_t) * (avg_v - a_v));
            if (area > max_area) {
                max_area = area;
                max_idx = p;
            }
        }

        output[out_idx++] = input[max_idx];
        a_idx = max_idx;
    }

    output[out_idx++] = input[input_len - 1];
    return out_idx;
}
