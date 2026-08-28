#include <algorithm>
#include <array>
#include <concepts>
#include <cstdint>
#include <numeric>
#include <span>
#include <vector>

struct alignas(16) NmsBoxCpp {
    int32_t x1{0};
    int32_t y1{0};
    int32_t x2{0};
    int32_t y2{0};
    int32_t score{0};
    int16_t class_id{0};

    [[nodiscard]] constexpr int32_t area() const noexcept {
        const int32_t w = x2 - x1;
        const int32_t h = y2 - y1;
        return (w > 0 && h > 0) ? (w * h) : 0;
    }
};

struct NmsConfigCpp {
    int32_t score_threshold{16384}; // 0.25 у масштабі Q16
    int32_t iou_num{1};
    int32_t iou_den{2};              // Поріг 0.5
    size_t max_output{64};
};

template <size_t MaxInput = 1024, size_t MaxOutput = 64>
class EmbeddedNmsEngine {
public:
    EmbeddedNmsEngine() noexcept = default;

    [[nodiscard]] size_t execute(
        std::span<const NmsBoxCpp> input_boxes,
        const NmsConfigCpp& config,
        std::span<NmsBoxCpp> output_boxes) noexcept
    {
        if (input_boxes.empty() || output_boxes.empty()) {
            return 0;
        }

        count_ = 0;
        const size_t limit = std::min(input_boxes.size(), MaxInput);

        // 1. Завантаження та фільтрація за скором
        for (size_t i = 0; i < limit; ++i) {
            if (input_boxes[i].score >= config.score_threshold) {
                x1_[count_] = input_boxes[i].x1;
                y1_[count_] = input_boxes[i].y1;
                x2_[count_] = input_boxes[i].x2;
                y2_[count_] = input_boxes[i].y2;
                score_[count_] = input_boxes[i].score;
                class_id_[count_] = input_boxes[i].class_id;
                area_[count_] = input_boxes[i].area();
                indices_[count_] = static_cast<uint16_t>(count_);
                count_++;
            }
        }

        if (count_ == 0) {
            return 0;
        }

        // 2. QuickSelect Top-K
        const size_t k = std::min({config.max_output, output_boxes.size(), count_, MaxOutput});
        std::nth_element(
            indices_.begin(),
            indices_.begin() + k,
            indices_.begin() + count_,
            [this](uint16_t a, uint16_t b) noexcept {
                return score_[a] > score_[b];
            });

        // 3. Точне впорядкування перших K елементів
        std::sort(
            indices_.begin(),
            indices_.begin() + k,
            [this](uint16_t a, uint16_t b) noexcept {
                return score_[a] > score_[b];
            });

        // 4. Придушення перекриттів
        std::array<bool, MaxOutput> suppressed{};
        size_t out_count = 0;

        for (size_t i = 0; i < k; ++i) {
            if (suppressed[i]) {
                continue;
            }

            const uint16_t lead_idx = indices_[i];
            output_boxes[out_count++] = NmsBoxCpp{
                .x1 = x1_[lead_idx],
                .y1 = y1_[lead_idx],
                .x2 = x2_[lead_idx],
                .y2 = y2_[lead_idx],
                .score = score_[lead_idx],
                .class_id = class_id_[lead_idx]
            };

            if (out_count >= output_boxes.size()) {
                break;
            }

            const int32_t lx1 = x1_[lead_idx];
            const int32_t ly1 = y1_[lead_idx];
            const int32_t lx2 = x2_[lead_idx];
            const int32_t ly2 = y2_[lead_idx];
            const int32_t l_area = area_[lead_idx];
            const int16_t l_class = class_id_[lead_idx];

            for (size_t j = i + 1; j < k; ++j) {
                if (suppressed[j] || class_id_[indices_[j]] != l_class) {
                    continue;
                }

                const uint16_t cand_idx = indices_[j];
                const int32_t ix1 = std::max(lx1, x1_[cand_idx]);
                const int32_t iy1 = std::max(ly1, y1_[cand_idx]);
                const int32_t ix2 = std::min(lx2, x2_[cand_idx]);
                const int32_t iy2 = std::min(ly2, y2_[cand_idx]);

                const int32_t iw = ix2 - ix1;
                const int32_t ih = iy2 - iy1;

                if (iw > 0 && ih > 0) {
                    const int32_t inter_area = iw * ih;
                    const int32_t union_area = l_area + area_[cand_idx] - inter_area;

                    if (static_cast<int64_t>(inter_area) * config.iou_den >=
                        static_cast<int64_t>(union_area) * config.iou_num) {
                        suppressed[j] = true;
                    }
                }
            }
        }

        return out_count;
    }

private:
    std::array<int32_t, MaxInput> x1_{};
    std::array<int32_t, MaxInput> y1_{};
    std::array<int32_t, MaxInput> x2_{};
    std::array<int32_t, MaxInput> y2_{};
    std::array<int32_t, MaxInput> area_{};
    std::array<int32_t, MaxInput> score_{};
    std::array<int16_t, MaxInput> class_id_{};
    std::array<uint16_t, MaxInput> indices_{};
    size_t count_{0};
};
