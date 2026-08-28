#include <vector>
#include <span>
#include <optional>
#include <cmath>
#include <algorithm>

struct MatchResult {
    int x{0};
    int y{0};
    float sub_x{0.0f};
    float sub_y{0.0f};
    double score{-2.0};
};

class PreparedTemplate {
public:
    PreparedTemplate(std::span<const uint8_t> tpl, int w, int h, int stride)
        : width_(w), height_(h), centered_(w * h) {
        double sum = 0.0;
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                sum += static_cast<double>(tpl[y * stride + x]);
            }
        }
        const double mean = sum / static_cast<double>(w * h);
        sum_ = sum;

        double var_energy = 0.0;
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                const double diff = static_cast<double>(tpl[y * stride + x]) - mean;
                centered_[y * w + x] = diff;
                var_energy += diff * diff;
            }
        }
        var_energy_ = var_energy;
        norm_factor_ = (var_energy > 1e-9) ? (1.0 / std::sqrt(var_energy)) : 0.0;
    }

    [[nodiscard]] int width() const noexcept { return width_; }
    [[nodiscard]] int height() const noexcept { return height_; }
    [[nodiscard]] double var_energy() const noexcept { return var_energy_; }
    [[nodiscard]] const std::vector<double>& centered() const noexcept { return centered_; }

private:
    int width_;
    int height_;
    double sum_{0.0};
    double var_energy_{0.0};
    double norm_factor_{0.0};
    std::vector<double> centered_;
};

MatchResult match_zncc(std::span<const uint8_t> img, int img_w, int img_h, int img_stride,
                       const PreparedTemplate &tpl, const IntegralImage &ii) {
    MatchResult best;
    const int max_x = img_w - tpl.width();
    const int max_y = img_h - tpl.height();
    const auto &t_data = tpl.centered();
    const double t_energy = tpl.var_energy();

    for (int y = 0; y <= max_y; ++y) {
        for (int x = 0; x <= max_x; ++x) {
            const auto stats = ii.query(x, y, tpl.width(), tpl.height());
            if (stats.variance_energy < 1e-9) continue;

            double cross_corr = 0.0;
            for (int ty = 0; ty < tpl.height(); ++ty) {
                const uint8_t *i_row = img.data() + (y + ty) * img_stride + x;
                const double *t_row = t_data.data() + ty * tpl.width();
                for (int tx = 0; tx < tpl.width(); ++tx) {
                    cross_corr += (static_cast<double>(i_row[tx]) - stats.mean) * t_row[tx];
                }
            }

            const double score = cross_corr / (std::sqrt(stats.variance_energy) * std::sqrt(t_energy));
            if (score > best.score) {
                best.score = score;
                best.x = x;
                best.y = y;
                best.sub_x = static_cast<float>(x);
                best.sub_y = static_cast<float>(y);
            }
        }
    }
    return best;
}
