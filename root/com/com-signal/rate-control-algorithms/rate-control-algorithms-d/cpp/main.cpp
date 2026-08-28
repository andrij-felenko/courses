#include <iostream>
#include <cmath>
#include <algorithm>
#include <array>
#include <expected>
#include <string_view>

enum class FrameType {
    I = 0,
    P = 1,
    B = 2
};

struct RateControlConfig {
    double bitrate_kbps;
    double fps;
    double bufsize_kbits;
    double initial_occupancy{0.9};
    int    gop_size{30};
};

class VbvRateController {
public:
    explicit VbvRateController(const RateControlConfig& cfg)
        : cfg_(cfg),
          buffer_fullness_kbits_(cfg.bufsize_kbits * cfg.initial_occupancy) {
        
        const double bits_per_frame = (cfg_.bitrate_kbps * 1000.0) / cfg_.fps;
        constexpr double default_qstep = 4.0; // QP ~ 26

        complexity_x_[static_cast<size_t>(FrameType::I)] = bits_per_frame * 4.0 * default_qstep;
        complexity_x_[static_cast<size_t>(FrameType::P)] = bits_per_frame * 1.0 * default_qstep;
        complexity_x_[static_cast<size_t>(FrameType::B)] = bits_per_frame * 0.4 * default_qstep;

        last_qp_[static_cast<size_t>(FrameType::I)] = 24;
        last_qp_[static_cast<size_t>(FrameType::P)] = 26;
        last_qp_[static_cast<size_t>(FrameType::B)] = 28;
    }

    struct FramePlan {
        int    qp;
        double target_bits;
    };

    [[nodiscard]] FramePlan plan_frame(FrameType type, double satd_factor = 1.0) const {
        const double bits_in_per_frame = (cfg_.bitrate_kbps * 1000.0) / cfg_.fps;
        const double buf_bits = buffer_fullness_kbits_ * 1000.0;
        const double max_buf_bits = cfg_.bufsize_kbits * 1000.0;

        // 1. Базовий розподіл бюджету
        double target_bits = bits_in_per_frame;
        switch (type) {
            case FrameType::I: target_bits *= 3.5; break;
            case FrameType::P: target_bits *= 1.0; break;
            case FrameType::B: target_bits *= 0.4; break;
        }

        if (satd_factor > 0.0) {
            target_bits *= satd_factor;
        }

        // 2. VBV обмеження безпеки (Underflow / Overflow clamping)
        const double min_buf_safety = 0.10 * max_buf_bits;
        const double max_allowed_bits = std::max(bits_in_per_frame * 0.2, 
                                                 buf_bits + bits_in_per_frame - min_buf_safety);
        target_bits = std::min(target_bits, max_allowed_bits);

        const double max_buf_ceiling = 0.95 * max_buf_bits;
        const double min_allowed_bits = buf_bits + bits_in_per_frame - max_buf_ceiling;
        if (min_allowed_bits > 0.0) {
            target_bits = std::max(target_bits, min_allowed_bits);
        }

        // 3. Обчислення QP за моделлю складності
        const auto idx = static_cast<size_t>(type);
        const double qstep = complexity_x_[idx] / target_bits;
        int qp = qstep_to_qp(qstep);

        // Демпфування різких стрибків QP
        const int prev_qp = last_qp_[idx];
        qp = std::clamp(qp, prev_qp - 2, prev_qp + 2);

        return {qp, target_bits};
    }

    void update_frame(FrameType type, int used_qp, double actual_bits) noexcept {
        const double bits_in_per_frame = (cfg_.bitrate_kbps * 1000.0) / cfg_.fps;
        
        // Оновлення буфера VBV
        buffer_fullness_kbits_ += (bits_in_per_frame - actual_bits) / 1000.0;
        buffer_fullness_kbits_ = std::clamp(buffer_fullness_kbits_, 0.0, cfg_.bufsize_kbits);

        // Оновлення моделі складності
        const auto idx = static_cast<size_t>(type);
        const double qstep = qp_to_qstep(used_qp);
        const double inst_x = actual_bits * qstep;
        constexpr double alpha = 0.85;

        complexity_x_[idx] = alpha * complexity_x_[idx] + (1.0 - alpha) * inst_x;
        last_qp_[idx] = used_qp;
        frame_in_gop_ = (frame_in_gop_ + 1) % cfg_.gop_size;
    }

    [[nodiscard]] double buffer_fullness_kbits() const noexcept {
        return buffer_fullness_kbits_;
    }

private:
    static constexpr double qp_to_qstep(int qp) noexcept {
        return 0.625 * std::pow(2.0, static_cast<double>(qp) / 6.0);
    }

    static constexpr int qstep_to_qp(double qstep) noexcept {
        int qp = static_cast<int>(std::round(6.0 * std::log2(qstep / 0.625)));
        return std::clamp(qp, 1, 51);
    }

    RateControlConfig cfg_;
    double buffer_fullness_kbits_;
    std::array<double, 3> complexity_x_{};
    std::array<int, 3> last_qp_{};
    int frame_in_gop_{0};
};
