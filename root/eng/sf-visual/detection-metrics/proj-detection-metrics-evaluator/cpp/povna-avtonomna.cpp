/*
 * ============================================================================
 * Embedded Detector Metrics Evaluator (C++20 Standard)
 * Автономний бортовий оцінювач метрик детекції для вбудованих систем
 * ============================================================================
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <span>
#include <cmath>
#include <format>
#include <string>
#include <array>
#include <optional>

enum class ScaleRange {
    All = 0,
    Small,
    Medium,
    Large
};

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
    float area{0.0f};
    bool is_crowd{false};
    bool matched{false};
};

struct ClassMetrics {
    float ap_50{0.0f};
    float ap_75{0.0f};
    float map_coco{0.0f};
    float ap_small{0.0f};
    float ap_medium{0.0f};
    float ap_large{0.0f};
    float best_f1{0.0f};
    float best_threshold{0.5f};
    int total_gt{0};
    int total_dets{0};
};

struct EvaluationSummary {
    std::vector<ClassMetrics> classes{};
    float map_50{0.0f};
    float map_75{0.0f};
    float map_coco{0.0f};
    float map_small{0.0f};
    float map_medium{0.0f};
    float map_large{0.0f};
    int num_evaluated_classes{0};
};

[[nodiscard]] inline float compute_iou_cpp(const BBox& a, const BBox& b) noexcept {
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

[[nodiscard]] constexpr bool is_gt_in_scale_cpp(float area, ScaleRange scale) noexcept {
    switch (scale) {
        case ScaleRange::Small:  return (area < 1024.0f);
        case ScaleRange::Medium: return (area >= 1024.0f && area < 9216.0f);
        case ScaleRange::Large:  return (area >= 9216.0f);
        case ScaleRange::All:
        default:                 return true;
    }
}

struct SingleApResult {
    float ap{0.0f};
    float best_f1{0.0f};
    float best_threshold{0.5f};
};

[[nodiscard]] SingleApResult evaluate_single_ap_cpp(
    std::span<const Detection> detections,
    std::span<GroundTruth> ground_truths,
    int target_class,
    float iou_threshold,
    ScaleRange scale
) {
    int total_gt = 0;
    for (auto& gt : ground_truths) {
        if (gt.class_id == target_class && is_gt_in_scale_cpp(gt.area, scale)) {
            ++total_gt;
        }
        gt.matched = false;
    }

    if (total_gt == 0) return {0.0f, 0.0f, 0.5f};

    std::vector<Detection> filtered;
    filtered.reserve(detections.size());
    for (const auto& det : detections) {
        if (det.class_id == target_class) {
            filtered.push_back(det);
        }
    }

    if (filtered.empty()) return {0.0f, 0.0f, 0.5f};

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
            if (!is_gt_in_scale_cpp(gt.area, scale)) {
                continue;
            }

            const float iou = compute_iou_cpp(filtered[i].box, gt.box);
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
                fp[i] = true; /* Дублікат цілі */
            }
        } else {
            fp[i] = true;
        }
    }

    std::vector<float> rec(filtered.size());
    std::vector<float> prec(filtered.size());
    int cum_tp = 0, cum_fp = 0;
    float max_f1 = 0.0f;
    float opt_thresh = filtered[0].score;

    for (std::size_t i = 0; i < filtered.size(); ++i) {
        if (tp[i]) ++cum_tp;
        if (fp[i]) ++cum_fp;
        rec[i] = static_cast<float>(cum_tp) / static_cast<float>(total_gt);
        prec[i] = static_cast<float>(cum_tp) / static_cast<float>(cum_tp + cum_fp);

        const float denom = prec[i] + rec[i];
        if (denom > 1e-6f) {
            const float f1 = 2.0f * (prec[i] * rec[i]) / denom;
            if (f1 > max_f1) {
                max_f1 = f1;
                opt_thresh = filtered[i].score;
            }
        }
    }

    /* Монотонна інтерполяція огинаючої справа наліво */
    float max_p = 0.0f;
    for (auto it = prec.rbegin(); it != prec.rend(); ++it) {
        max_p = std::max(max_p, *it);
        *it = max_p;
    }

    /* Чисельна неперервна інтеграція площі під кривою (AUC) */
    float ap = 0.0f;
    float prev_r = 0.0f;
    for (std::size_t i = 0; i < filtered.size(); ++i) {
        if (rec[i] != prev_r) {
            ap += (rec[i] - prev_r) * prec[i];
            prev_r = rec[i];
        }
    }

    return {ap, max_f1, opt_thresh};
}

[[nodiscard]] EvaluationSummary run_full_evaluation_cpp(
    std::span<const Detection> detections,
    std::span<GroundTruth> ground_truths,
    int num_classes
) {
    EvaluationSummary summary;
    summary.classes.resize(num_classes);

    constexpr std::array<float, 10> thresholds = {
        0.50f, 0.55f, 0.60f, 0.65f, 0.70f,
        0.75f, 0.80f, 0.85f, 0.90f, 0.95f
    };

    float sum_map_50 = 0.0f, sum_map_75 = 0.0f, sum_map_coco = 0.0f;
    float sum_map_s = 0.0f, sum_map_m = 0.0f, sum_map_l = 0.0f;
    int valid_classes = 0;

    for (int c = 0; c < num_classes; ++c) {
        auto& cm = summary.classes[c];

        for (const auto& gt : ground_truths) {
            if (gt.class_id == c) ++cm.total_gt;
        }
        for (const auto& det : detections) {
            if (det.class_id == c) ++cm.total_dets;
        }

        if (cm.total_gt == 0) continue;

        auto res50 = evaluate_single_ap_cpp(detections, ground_truths, c, 0.50f, ScaleRange::All);
        cm.ap_50 = res50.ap;
        cm.best_f1 = res50.best_f1;
        cm.best_threshold = res50.best_threshold;

        auto res75 = evaluate_single_ap_cpp(detections, ground_truths, c, 0.75f, ScaleRange::All);
        cm.ap_75 = res75.ap;

        float ap_sum = 0.0f;
        for (float thresh : thresholds) {
            ap_sum += evaluate_single_ap_cpp(detections, ground_truths, c, thresh, ScaleRange::All).ap;
        }
        cm.map_coco = ap_sum / static_cast<float>(thresholds.size());

        cm.ap_small = evaluate_single_ap_cpp(detections, ground_truths, c, 0.50f, ScaleRange::Small).ap;
        cm.ap_medium = evaluate_single_ap_cpp(detections, ground_truths, c, 0.50f, ScaleRange::Medium).ap;
        cm.ap_large = evaluate_single_ap_cpp(detections, ground_truths, c, 0.50f, ScaleRange::Large).ap;

        sum_map_50 += cm.ap_50;
        sum_map_75 += cm.ap_75;
        sum_map_coco += cm.map_coco;
        sum_map_s += cm.ap_small;
        sum_map_m += cm.ap_medium;
        sum_map_l += cm.ap_large;
        ++valid_classes;
    }

    if (valid_classes > 0) {
        summary.num_evaluated_classes = valid_classes;
        summary.map_50 = sum_map_50 / static_cast<float>(valid_classes);
        summary.map_75 = sum_map_75 / static_cast<float>(valid_classes);
        summary.map_coco = sum_map_coco / static_cast<float>(valid_classes);
        summary.map_small = sum_map_s / static_cast<float>(valid_classes);
        summary.map_medium = sum_map_m / static_cast<float>(valid_classes);
        summary.map_large = sum_map_l / static_cast<float>(valid_classes);
    }

    return summary;
}

void print_evaluation_report_cpp(const EvaluationSummary& s) {
    std::cout << "\n========================================================================\n"
              << "         БОРТОВИЙ ЗВIТ ОЦIНКИ МЕТРИК ДЕТЕКТОРА (MS COCO PROTOCOL)       \n"
              << "========================================================================\n"
              << "| Клас |    GT | Dets |  AP@0.50 |  AP@0.75 | mAP@[.5:.95] |  AP_s  |  AP_m  |\n"
              << "|------|-------|------|----------|----------|--------------|--------|--------|\n";

    for (std::size_t c = 0; c < s.classes.size(); ++c) {
        const auto& cm = s.classes[c];
        if (cm.total_gt == 0) continue;
        std::cout << std::format("| {:4d} | {:5d} | {:4d} |  {:7.3f} |  {:7.3f} |      {:7.3f} | {:6.3f} | {:6.3f} |\n",
                                 c, cm.total_gt, cm.total_dets,
                                 cm.ap_50, cm.ap_75, cm.map_coco,
                                 cm.ap_small, cm.ap_medium);
    }

    std::cout << "========================================================================\n"
              << std::format(" ЗВЕДЕНI МЕТРИКИ (Усереднено по {} класах):\n", s.num_evaluated_classes)
              << std::format("   mAP@[0.50:0.95] (Основний бал якості) : {:7.4f} ({:5.1f}%)\n", s.map_coco, s.map_coco * 100.0f)
              << std::format("   mAP@0.50        (VOC поріг 0.50)      : {:7.4f} ({:5.1f}%)\n", s.map_50, s.map_50 * 100.0f)
              << std::format("   mAP@0.75        (Жорсткий поріг 0.75) : {:7.4f} ({:5.1f}%)\n", s.map_75, s.map_75 * 100.0f)
              << std::format("   mAP_small       (Малорозмiрнi цiлi)   : {:7.4f} ({:5.1f}%)\n", s.map_small, s.map_small * 100.0f)
              << std::format("   mAP_medium      (Середнi цiлi)        : {:7.4f} ({:5.1f}%)\n", s.map_medium, s.map_medium * 100.0f)
              << std::format("   mAP_large       (Великi цiлi)         : {:7.4f} ({:5.1f}%)\n", s.map_large, s.map_large * 100.0f)
              << "========================================================================\n\n";
}

[[nodiscard]] std::string serialize_summary_json_cpp(const EvaluationSummary& s) {
    std::string json = std::format(
        "{{\"map\":{:.4f},\"map50\":{:.4f},\"map75\":{:.4f},\"maps\":{:.4f},\"mapm\":{:.4f},\"mapl\":{:.4f},\"classes\":[",
        s.map_coco, s.map_50, s.map_75, s.map_small, s.map_medium, s.map_large);

    bool first = true;
    for (std::size_t c = 0; c < s.classes.size(); ++c) {
        if (s.classes[c].total_gt == 0) continue;
        if (!first) json += ",";
        first = false;
        json += std::format(
            "{{\"id\":{},\"gt\":{},\"dets\":{},\"ap50\":{:.3f},\"map\":{:.3f},\"best_f1\":{:.3f},\"opt_t\":{:.3f}}}",
            c, s.classes[c].total_gt, s.classes[c].total_dets,
            s.classes[c].ap_50, s.classes[c].map_coco,
            s.classes[c].best_f1, s.classes[c].best_threshold);
    }

    json += "]}";
    return json;
}
