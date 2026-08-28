#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <optional>
#include <span>

struct BoundingBox {
    float x1{0.0f};
    float y1{0.0f};
    float x2{0.0f};
    float y2{0.0f};
    float score{0.0f};

    [[nodiscard]] constexpr float area() const noexcept {
        return std::max(0.0f, x2 - x1) * std::max(0.0f, y2 - y1);
    }
};

struct TrackedObject {
    BoundingBox box;
    int track_id{-1};
};

[[nodiscard]] inline float compute_iou(const BoundingBox& a, const BoundingBox& b) noexcept {
    const float xx1 = std::max(a.x1, b.x1);
    const float yy1 = std::max(a.y1, b.y1);
    const float xx2 = std::min(a.x2, b.x2);
    const float yy2 = std::min(a.y2, b.y2);
    const float w = std::max(0.0f, xx2 - xx1);
    const float h = std::max(0.0f, yy2 - yy1);
    const float inter = w * h;
    const float un = a.area() + b.area() - inter;
    return (un > 0.0f) ? (inter / un) : 0.0f;
}

class KalmanBoxTrackerCpp {
public:
    explicit KalmanBoxTrackerCpp(const BoundingBox& bbox, int id) noexcept
        : id_(id) {
        const float w = bbox.x2 - bbox.x1;
        const float h = bbox.y2 - bbox.y1;
        x_[0] = bbox.x1 + w * 0.5f;
        x_[1] = bbox.y1 + h * 0.5f;
        x_[2] = w * h;
        x_[3] = (h > 0.0f) ? (w / h) : 1.0f;
        x_[4] = x_[5] = x_[6] = 0.0f;

        for (size_t i = 0; i < 7; ++i) {
            P_[i] = (i < 4) ? 10.0f : 1000.0f;
        }
    }

    [[nodiscard]] BoundingBox predict() noexcept {
        // x = F * x
        x_[0] += x_[4];
        x_[1] += x_[5];
        x_[2] += x_[6];

        for (size_t i = 0; i < 7; ++i) {
            P_[i] += (i < 4) ? 0.01f : 0.1f;
        }
        ++age_;
        if (time_since_update_ > 0) {
            hit_streak_ = 0;
        }
        ++time_since_update_;
        return get_bbox();
    }

    void update(const BoundingBox& bbox) noexcept {
        const float w = bbox.x2 - bbox.x1;
        const float h = bbox.y2 - bbox.y1;
        const std::array<float, 4> z = {
            bbox.x1 + w * 0.5f,
            bbox.y1 + h * 0.5f,
            w * h,
            (h > 0.0f) ? (w / h) : 1.0f
        };

        for (size_t i = 0; i < 4; ++i) {
            const float r_noise = (i < 2) ? 1.0f : 10.0f;
            const float s = P_[i] + r_noise;
            const float k = P_[i] / s;
            const float innov = z[i] - x_[i];
            x_[i] += k * innov;
            P_[i] *= (1.0f - k);
            if (i < 3) {
                x_[i + 4] += (k * 0.5f) * innov;
            }
        }
        time_since_update_ = 0;
        ++hits_;
        ++hit_streak_;
    }

    [[nodiscard]] BoundingBox get_bbox() const noexcept {
        const float u = x_[0], v = x_[1], s = x_[2], r = x_[3];
        if (s <= 0.0f || r <= 0.0f) return {};
        const float w = std::sqrt(s * r);
        const float h = std::sqrt(s / r);
        return { u - w * 0.5f, v - h * 0.5f, u + w * 0.5f, v + h * 0.5f, 1.0f };
    }

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] int time_since_update() const noexcept { return time_since_update_; }
    [[nodiscard]] int hit_streak() const noexcept { return hit_streak_; }

private:
    std::array<float, 7> x_{};
    std::array<float, 7> P_{};
    int id_{0};
    int hits_{1};
    int hit_streak_{1};
    int age_{0};
    int time_since_update_{0};
};

class SortTracker {
public:
    explicit SortTracker(int max_age = 1, int min_hits = 3, float iou_thresh = 0.3f) noexcept
        : max_age_(max_age), min_hits_(min_hits), iou_threshold_(iou_thresh) {}

    [[nodiscard]] std::vector<TrackedObject> update(std::span<const BoundingBox> detections) {
        ++frame_count_;

        // 1. Прогноз для всіх наявних треків
        std::vector<BoundingBox> predicted_boxes;
        predicted_boxes.reserve(trackers_.size());
        for (auto& trk : trackers_) {
            predicted_boxes.push_back(trk.predict());
        }

        // 2. Жадібна асоціація
        std::vector<bool> det_matched(detections.size(), false);
        for (size_t i = 0; i < trackers_.size(); ++i) {
            float best_iou = iou_threshold_;
            int best_det = -1;
            for (size_t j = 0; j < detections.size(); ++j) {
                if (det_matched[j]) continue;
                const float iou = compute_iou(predicted_boxes[i], detections[j]);
                if (iou > best_iou) {
                    best_iou = iou;
                    best_det = static_cast<int>(j);
                }
            }
            if (best_det >= 0) {
                det_matched[best_det] = true;
                trackers_[i].update(detections[best_det]);
            }
        }

        // 3. Ініціалізація нових треків
        for (size_t j = 0; j < detections.size(); ++j) {
            if (!det_matched[j]) {
                trackers_.emplace_back(detections[j], next_id_++);
            }
        }

        // 4. Збір результатів та видалення застарілих треків
        std::vector<TrackedObject> results;
        auto it = trackers_.begin();
        while (it != trackers_.end()) {
            if (it->time_since_update() > max_age_) {
                it = trackers_.erase(it);
            } else {
                if (it->time_since_update() < 1 &&
                    (it->hit_streak() >= min_hits_ || frame_count_ <= min_hits_)) {
                    results.push_back(TrackedObject{ it->get_bbox(), it->id() });
                }
                ++it;
            }
        }
        return results;
    }

private:
    int max_age_{1};
    int min_hits_{3};
    float iou_threshold_{0.3f};
    int next_id_{1};
    int frame_count_{0};
    std::vector<KalmanBoxTrackerCpp> trackers_;
};
