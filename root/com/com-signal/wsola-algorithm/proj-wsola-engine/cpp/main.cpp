#include <vector>
#include <cmath>
#include <algorithm>
#include <numbers>
#include <span.h>

class WsolaEngine {
public:
    WsolaEngine(int frame_size, int seek_range, float tempo)
        : frame_size_(frame_size),
          synth_hop_(frame_size / 2),
          seek_range_(seek_range),
          template_size_(frame_size / 2),
          tempo_(tempo),
          window_(frame_size, 0.0f),
          in_buf_((frame_size + seek_range) * 4, 0.0f),
          out_buf_(frame_size * 4, 0.0f) {
        
        // Генерація вікна Ганна із задоволенням умови COLA
        for (int i = 0; i < frame_size_; ++i) {
            window_[i] = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * i / frame_size_));
        }
    }

    void set_tempo(float tempo) noexcept {
        tempo_ = tempo;
    }

    void push_input(std::span<const float> samples) {
        in_buf_.insert(in_buf_.end() - in_buf_free_count(), samples.begin(), samples.end());
        in_valid_count_ += static_cast<int>(samples.size());
    }

    bool process_frame() {
        const int nom_pos = static_cast<int>(ana_pos_);
        const int req_lookahead = nom_pos + seek_range_ + frame_size_;

        if (in_valid_count_ < req_lookahead) {
            return false; // Очікування додаткових відліків
        }

        int ref_pos = last_tau_ + synth_hop_;
        if (ref_pos + template_size_ > in_valid_count_) {
            ref_pos = nom_pos;
        }

        const int delta = find_best_shift(nom_pos, ref_pos);
        const int tau_k = nom_pos + delta;

        // Внесок у буфер акумуляції overlap-add
        for (int n = 0; n < frame_size_; ++n) {
            out_buf_[n] += in_buf_[tau_k + n] * window_[n];
        }

        out_valid_count_ += synth_hop_;
        last_tau_ = tau_k;
        ana_pos_ += static_cast<float>(synth_hop_) * tempo_;

        // Просування часової шкали
        const int consume = synth_hop_;
        std::copy(in_buf_.begin() + consume, in_buf_.begin() + in_valid_count_, in_buf_.begin());
        in_valid_count_ -= consume;
        last_tau_ -= consume;
        ana_pos_ -= static_cast<float>(consume);

        return true;
    }

    int pull_output(std::span<float> dst) {
        const int count = std::min(static_cast<int>(dst.size()), out_valid_count_);
        if (count <= 0) return 0;

        std::copy_n(out_buf_.begin(), count, dst.begin());

        // Зсув буфера синтезу та очищення вивільненої зони
        std::copy(out_buf_.begin() + count, out_buf_.end(), out_buf_.begin());
        std::fill(out_buf_.end() - count, out_buf_.end(), 0.0f);
        out_valid_count_ -= count;

        return count;
    }

private:
    int find_best_shift(int base_pos, int ref_pos) const noexcept {
        float best_corr = -1e30f;
        int best_delta = 0;

        for (int d = -seek_range_; d <= seek_range_; ++d) {
            const int cand_pos = base_pos + d;
            if (cand_pos < 0 || cand_pos + template_size_ > in_valid_count_) {
                continue;
            }

            float corr = 0.0f;
            for (int m = 0; m < template_size_; ++m) {
                corr += in_buf_[ref_pos + m] * in_buf_[cand_pos + m];
            }

            if (corr > best_corr) {
                best_corr = corr;
                best_delta = d;
            }
        }
        return best_delta;
    }

    [[nodiscard]] int in_buf_free_count() const noexcept {
        return static_cast<int>(in_buf_.size()) - in_valid_count_;
    }

    int frame_size_{512};
    int synth_hop_{256};
    int seek_range_{128};
    int template_size_{256};
    float tempo_{1.0f};

    std::vector<float> window_;
    std::vector<float> in_buf_;
    int in_valid_count_{0};

    std::vector<float> out_buf_;
    int out_valid_count_{0};

    int last_tau_{0};
    float ana_pos_{0.0f};
};
