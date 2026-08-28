#include <iostream>
#include <vector>
#include <algorithm>
#include <span>
#include <cmath>
#include <optional>

struct BBox {
    float x1{0.0f}, y1{0.0f}, x2{0.0f}, y2{0.0f};

    [[nodiscard]] constexpr float area() const noexcept {
        const float w = std::max(0.0f, x2 - x1);
        const float h = std::max(0.0f, y2 - y1);
        return w * h;
    }
};

struct Detection {
    BBox box{};
    float score{0.0f};
    int class_id{0};
    int image_id{0};
};

struct GroundTruth {
    BBox box{};
    int class_id{0};
    int image_id{0};
    bool matched{false};
};

[[nodiscard]] inline float compute_iou(const BBox& a, const BBox& b) noexcept {
    const float ix1 = std::max(a.x1, b.x1);
    const float iy1 = std::max(a.y1, b.y1);
    const float ix2 = std::min(a.x2, b.x2);
    const float iy2 = std::min(a.y2, b.y2);

    const float iw = std::max(0.0f, ix2 - ix1);
    const float ih = std::max(0.0f, iy2 - iy1);
    const float inter = iw * ih;

    if (inter <= 0.0f) return 0.0f;

    const float uni = a.area() + b.area() - inter;
    return (uni > 0.0f) ? (inter / uni) : 0.0f;
}

[[nodiscard]] float evaluate_class_ap(
    std::span<const Detection> detections,
    std::span<GroundTruth> ground_truths,
    int target_class,
    float iou_threshold
) {
    int total_gt = 0;
    for (auto& gt : ground_truths) {
        if (gt.class_id == target_class) {
            ++total_gt;
            gt.matched = false;
        }
    }
    if (total_gt == 0) {
        return detections.empty() ? 1.0f : 0.0f;
    }

    std::vector<Detection> filtered;
    filtered.reserve(detections.size());
    for (const auto& det : detections) {
        if (det.class_id == target_class) {
            filtered.push_back(det);
        }
    }

    if (filtered.empty()) {
        return 0.0f;
    }

    std::ranges::sort(filtered, [](const Detection& a, const Detection& b) noexcept {
        return a.score > b.score;
    });

    std::vector<bool> tp(filtered.size(), false);
    std::vector<bool> fp(filtered.size(), false);

    for (std::size_t i = 0; i < filtered.size(); ++i) {
        float best_iou = 0.0f;
        std::optional<std::size_t> best_gt_idx;

        for (std::size_t j = 0; j < ground_truths.size(); ++j) {
            auto& gt = ground_truths[j];
            if (gt.class_id != target_class || gt.image_id != filtered[i].image_id) {
                continue;
            }
            const float iou = compute_iou(filtered[i].box, gt.box);
            if (iou > best_iou) {
                best_iou = iou;
                best_gt_idx = j;
            }
        }

        if (best_iou >= iou_threshold && best_gt_idx.has_value()) {
            auto& gt = ground_truths[*best_gt_idx];
            if (!gt.matched) {
                tp[i] = true;
                gt.matched = true;
            } else {
                fp[i] = true; /* Дублікат */
            }
        } else {
            fp[i] = true;
        }
    }

    std::vector<float> rec(filtered.size());
    std::vector<float> prec(filtered.size());
    int cum_tp = 0, cum_fp = 0;

    for (std::size_t i = 0; i < filtered.size(); ++i) {
        if (tp[i]) ++cum_tp;
        if (fp[i]) ++cum_fp;
        rec[i] = static_cast<float>(cum_tp) / static_cast<float>(total_gt);
        prec[i] = static_cast<float>(cum_tp) / static_cast<float>(cum_tp + cum_fp);
    }

    /* Монотонна інтерполяція огинаючої */
    float max_p = 0.0f;
    for (auto it = prec.rbegin(); it != prec.rend(); ++it) {
        max_p = std::max(max_p, *it);
        *it = max_p;
    }

    /* Обчислення площі під кривою (AUC) */
    float ap = 0.0f;
    float prev_r = 0.0f;
    for (std::size_t i = 0; i < filtered.size(); ++i) {
        if (rec[i] != prev_r) {
            ap += (rec[i] - prev_r) * prec[i];
            prev_r = rec[i];
        }
    }

    return ap;
}

[[nodiscard]] float evaluate_coco_map(
    std::span<const Detection> detections,
    std::span<GroundTruth> ground_truths,
    int num_classes
) {
    float total_map = 0.0f;
    int evaluated_classes = 0;

    for (int c = 0; c < num_classes; ++c) {
        float class_ap_sum = 0.0f;
        for (int step = 0; step < 10; ++step) {
            const float thresh = 0.50f + static_cast<float>(step) * 0.05f;
            class_ap_sum += evaluate_class_ap(detections, ground_truths, c, thresh);
        }
        total_map += (class_ap_sum / 10.0f);
        ++evaluated_classes;
    }

    return (evaluated_classes > 0) ? (total_map / static_cast<float>(evaluated_classes)) : 0.0f;
}
