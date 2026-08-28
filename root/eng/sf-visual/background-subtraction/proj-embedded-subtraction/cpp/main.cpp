#include <cstdint>
#include <vector>
#include <span>
#include <algorithm>
#include <numeric>
#include <memory>

struct Blob {
    uint16_t min_x{0};
    uint16_t min_y{0};
    uint16_t max_x{0};
    uint16_t max_y{0};
    uint32_t area{0};
    uint16_t cx{0};
    uint16_t cy{0};
};

class MotionDetector {
public:
    MotionDetector(uint16_t width, uint16_t height, uint8_t threshold = 20,
                   uint8_t shift_alpha = 4, uint32_t min_area = 50)
        : width_(width), height_(height), threshold_(threshold),
          shift_alpha_(shift_alpha), min_area_(min_area),
          bg_q8_(static_cast<size_t>(width) * height, 0),
          mask_raw_(static_cast<size_t>(width) * height, 0),
          mask_clean_(static_cast<size_t>(width) * height, 0),
          labels_(static_cast<size_t>(width) * height, 0) {}

    std::vector<Blob> process_frame(std::span<const uint8_t> frame) {
        if (!initialized_) {
            initialize_background(frame);
            return {};
        }

        subtract_and_update(frame);
        apply_morphology();
        return extract_blobs();
    }

    void reset() noexcept {
        initialized_ = false;
        std::fill(bg_q8_.begin(), bg_q8_.end(), 0);
    }

private:
    uint16_t width_;
    uint16_t height_;
    uint8_t threshold_;
    uint8_t shift_alpha_;
    uint32_t min_area_;
    bool initialized_{false};

    std::vector<uint16_t> bg_q8_;
    std::vector<uint8_t> mask_raw_;
    std::vector<uint8_t> mask_clean_;
    std::vector<uint16_t> labels_;

    void initialize_background(std::span<const uint8_t> frame) {
        const size_t total = static_cast<size_t>(width_) * height_;
        for (size_t i = 0; i < total; ++i) {
            bg_q8_[i] = static_cast<uint16_t>(frame[i] << 8);
            mask_raw_[i] = 0;
        }
        initialized_ = true;
    }

    void subtract_and_update(std::span<const uint8_t> frame) noexcept {
        const size_t total = static_cast<size_t>(width_) * height_;
        const auto t = threshold_;
        const auto s = shift_alpha_;

        for (size_t i = 0; i < total; ++i) {
            const uint8_t cur = frame[i];
            const uint8_t bg_val = static_cast<uint8_t>(bg_q8_[i] >> 8);

            const int16_t diff = std::abs(static_cast<int16_t>(cur) - static_cast<int16_t>(bg_val));

            if (diff > t) {
                mask_raw_[i] = 255;
            } else {
                mask_raw_[i] = 0;
                const int32_t target = static_cast<int32_t>(cur << 8);
                const int32_t delta = (target - static_cast<int32_t>(bg_q8_[i])) >> s;
                bg_q8_[i] = static_cast<uint16_t>(static_cast<int32_t>(bg_q8_[i]) + delta);
            }
        }
    }

    void apply_morphology() noexcept {
        const size_t w = width_;
        const size_t h = height_;

        // Ерозія з mask_raw_ у mask_clean_
        for (size_t y = 1; y < h - 1; ++y) {
            const size_t row = y * w;
            for (size_t x = 1; x < w - 1; ++x) {
                if (mask_raw_[row + x] &&
                    mask_raw_[row - w + x] && mask_raw_[row + w + x] &&
                    mask_raw_[row + x - 1] && mask_raw_[row + x + 1]) {
                    mask_clean_[row + x] = 255;
                } else {
                    mask_clean_[row + x] = 0;
                }
            }
        }

        // Дилатація з mask_clean_ у mask_raw_
        for (size_t y = 1; y < h - 1; ++y) {
            const size_t row = y * w;
            for (size_t x = 1; x < w - 1; ++x) {
                if (mask_clean_[row + x] ||
                    mask_clean_[row - w + x] || mask_clean_[row + w + x] ||
                    mask_clean_[row + x - 1] || mask_clean_[row + x + 1]) {
                    mask_raw_[row + x] = 255;
                } else {
                    mask_raw_[row + x] = 0;
                }
            }
        }
        std::copy(mask_raw_.begin(), mask_raw_.end(), mask_clean_.begin());
    }

    struct LabelStats {
        uint16_t min_x{0xFFFF};
        uint16_t min_y{0xFFFF};
        uint16_t max_x{0};
        uint16_t max_y{0};
        uint32_t area{0};
        uint32_t sum_x{0};
        uint32_t sum_y{0};
    };

    static uint16_t uf_find(std::vector<uint16_t>& parent, uint16_t i) noexcept {
        while (parent[i] != i) {
            parent[i] = parent[parent[i]];
            i = parent[i];
        }
        return i;
    }

    static void uf_union(std::vector<uint16_t>& parent, uint16_t i, uint16_t j) noexcept {
        const uint16_t root_i = uf_find(parent, i);
        const uint16_t root_j = uf_find(parent, j);
        if (root_i < root_j) parent[root_j] = root_i;
        else if (root_i > root_j) parent[root_i] = root_j;
    }

    std::vector<Blob> extract_blobs() {
        const size_t w = width_;
        const size_t h = height_;
        std::fill(labels_.begin(), labels_.end(), 0);

        constexpr size_t MAX_LABELS = 1024;
        std::vector<uint16_t> parent(MAX_LABELS);
        std::iota(parent.begin(), parent.end(), static_cast<uint16_t>(0));

        uint16_t next_label = 1;

        // Перший прохід CCL
        for (size_t y = 1; y < h; ++y) {
            const size_t row = y * w;
            const size_t prev_row = (y - 1) * w;
            for (size_t x = 1; x < w; ++x) {
                if (!mask_clean_[row + x]) continue;

                const uint16_t left = labels_[row + x - 1];
                const uint16_t up = labels_[prev_row + x];

                if (left == 0 && up == 0) {
                    if (next_label < MAX_LABELS) {
                        labels_[row + x] = next_label++;
                    }
                } else if (left != 0 && up == 0) {
                    labels_[row + x] = left;
                } else if (left == 0 && up != 0) {
                    labels_[row + x] = up;
                } else {
                    labels_[row + x] = left;
                    if (left != up) {
                        uf_union(parent, left, up);
                    }
                }
            }
        }

        std::vector<LabelStats> stats(next_label);

        // Другий прохід CCL
        for (size_t y = 0; y < h; ++y) {
            const size_t row = y * w;
            for (size_t x = 0; x < w; ++x) {
                const uint16_t l = labels_[row + x];
                if (l == 0) continue;

                const uint16_t root = uf_find(parent, l);
                auto& st = stats[root];
                st.area++;
                st.sum_x += static_cast<uint32_t>(x);
                st.sum_y += static_cast<uint32_t>(y);
                st.min_x = std::min(st.min_x, static_cast<uint16_t>(x));
                st.max_x = std::max(st.max_x, static_cast<uint16_t>(x));
                st.min_y = std::min(st.min_y, static_cast<uint16_t>(y));
                st.max_y = std::max(st.max_y, static_cast<uint16_t>(y));
            }
        }

        std::vector<Blob> result;
        for (size_t i = 1; i < next_label; ++i) {
            if (parent[i] == i && stats[i].area >= min_area_) {
                result.push_back(Blob{
                    .min_x = stats[i].min_x,
                    .min_y = stats[i].min_y,
                    .max_x = stats[i].max_x,
                    .max_y = stats[i].max_y,
                    .area = stats[i].area,
                    .cx = static_cast<uint16_t>(stats[i].sum_x / stats[i].area),
                    .cy = static_cast<uint16_t>(stats[i].sum_y / stats[i].area)
                });
            }
        }
        return result;
    }
};
