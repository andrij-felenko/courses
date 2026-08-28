#include <vector>
#include <span>
#include <cstdint>
#include <cmath>

class IntegralImage {
public:
    IntegralImage(int width, int height)
        : width_(width), height_(height),
          sum_((width + 1) * (height + 1), 0.0),
          sqsum_((width + 1) * (height + 1), 0.0) {}

    void compute(std::span<const uint8_t> image, int stride) {
        const int stride_ii = width_ + 1;
        for (int y = 0; y < height_; ++y) {
            double row_sum = 0.0;
            double row_sqsum = 0.0;
            const uint8_t *img_row = image.data() + y * stride;
            double *sum_row = sum_.data() + (y + 1) * stride_ii + 1;
            const double *sum_prev = sum_.data() + y * stride_ii + 1;
            double *sqsum_row = sqsum_.data() + (y + 1) * stride_ii + 1;
            const double *sqsum_prev = sqsum_.data() + y * stride_ii + 1;

            for (int x = 0; x < width_; ++x) {
                const double val = static_cast<double>(img_row[x]);
                row_sum += val;
                row_sqsum += val * val;
                sum_row[x] = sum_prev[x] + row_sum;
                sqsum_row[x] = sqsum_prev[x] + row_sqsum;
            }
        }
    }

    struct WindowStats {
        double sum;
        double sqsum;
        double mean;
        double variance_energy; // Σ (I - I_mean)^2
    };

    [[nodiscard]] WindowStats query(int x, int y, int w, int h) const noexcept {
        const int stride = width_ + 1;
        const int x0 = x, y0 = y;
        const int x1 = x + w, y1 = y + h;

        const double s = sum_[y1 * stride + x1] - sum_[y0 * stride + x1]
                       - sum_[y1 * stride + x0] + sum_[y0 * stride + x0];
        const double sq = sqsum_[y1 * stride + x1] - sqsum_[y0 * stride + x1]
                        - sqsum_[y1 * stride + x0] + sqsum_[y0 * stride + x0];

        const double area = static_cast<double>(w * h);
        const double mean = s / area;
        const double var_energy = sq - (s * s) / area;

        return { s, sq, mean, (var_energy > 0.0) ? var_energy : 0.0 };
    }

private:
    int width_;
    int height_;
    std::vector<double> sum_;
    std::vector<double> sqsum_;
};
