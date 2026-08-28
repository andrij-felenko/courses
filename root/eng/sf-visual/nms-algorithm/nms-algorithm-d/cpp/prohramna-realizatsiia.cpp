#include <algorithm>
#include <concepts>
#include <cstdint>
#include <numeric>
#include <span>
#include <vector>

struct BoundingBox {
    float x1{0.0f};
    float y1{0.0f};
    float x2{0.0f};
    float y2{0.0f};
    float score{0.0f};
    int32_t class_id{0};

    [[nodiscard]] constexpr float area() const noexcept {
        const float w = x2 - x1;
        const float h = y2 - y1;
        return (w > 0.0f && h > 0.0f) ? (w * h) : 0.0f;
    }
};

[[nodiscard]] inline float calculate_iou(const BoundingBox& a, const BoundingBox& b) noexcept {
    const float inter_x1 = std::max(a.x1, b.x1);
    const float inter_y1 = std::max(a.y1, b.y1);
    const float inter_x2 = std::min(a.x2, b.x2);
    const float inter_y2 = std::min(a.y2, b.y2);

    const float inter_w = std::max(0.0f, inter_x2 - inter_x1);
    const float inter_h = std::max(0.0f, inter_y2 - inter_y1);
    const float inter_area = inter_w * inter_h;

    if (inter_area <= 0.0f) {
        return 0.0f;
    }

    const float union_area = a.area() + b.area() - inter_area;
    return (union_area > 0.0f) ? (inter_area / union_area) : 0.0f;
}

/* Ідіоматичний NMS на C++20 з використанням std::span та std::vector */
[[nodiscard]] std::vector<BoundingBox> nms_greedy_cpp(
    std::span<const BoundingBox> input_boxes,
    float score_threshold,
    float nms_threshold,
    size_t max_output = 100) {

    if (input_boxes.empty() || max_output == 0) {
        return {};
    }

    std::vector<size_t> indices;
    indices.reserve(input_boxes.size());

    // 1. Попередня фільтрація за порогом упевненості
    for (size_t i = 0; i < input_boxes.size(); ++i) {
        if (input_boxes[i].score >= score_threshold) {
            indices.push_back(i);
        }
    }

    if (indices.empty()) {
        return {};
    }

    // 2. Сортування за спаданням скору
    std::sort(indices.begin(), indices.end(),
              [&input_boxes](size_t a, size_t b) noexcept {
                  return input_boxes[a].score > input_boxes[b].score;
              });

    // 3. Ітеративне придушення
    std::vector<bool> suppressed(indices.size(), false);
    std::vector<BoundingBox> results;
    results.reserve(std::min(max_output, indices.size()));

    for (size_t i = 0; i < indices.size(); ++i) {
        if (suppressed[i]) {
            continue;
        }

        const size_t lead_idx = indices[i];
        results.push_back(input_boxes[lead_idx]);
        if (results.size() >= max_output) {
            break;
        }

        for (size_t j = i + 1; j < indices.size(); ++j) {
            if (suppressed[j]) {
                continue;
            }

            const size_t cand_idx = indices[j];
            if (input_boxes[lead_idx].class_id == input_boxes[cand_idx].class_id) {
                if (calculate_iou(input_boxes[lead_idx], input_boxes[cand_idx]) >= nms_threshold) {
                    suppressed[j] = true;
                }
            }
        }
    }

    return results;
}
