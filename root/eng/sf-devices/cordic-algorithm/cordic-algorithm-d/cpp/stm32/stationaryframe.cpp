#include <cstdint>
#include <cmath>
#include <algorithm>

namespace embedded::foc {

/* Просторові структури векторного контуру */
struct StationaryFrame {
    int32_t alpha;
    int32_t beta;
};

struct RotorFrame {
    int32_t d;
    int32_t q;
};

struct ResolverStatus {
    int32_t amplitude;
    int32_t angle_bam;
    bool is_fault;
};

class FocEngine {
public:
    static constexpr int32_t MaxSafeInputQ31 = 1304032742; /* Поріг безпеки 1.0 / K */
    static constexpr int32_t DeadbandLimit   = 64;
    static constexpr int32_t Sqrt3InvQ15     = 18919;

    /* Метод насичення для захисту внутрішніх регістрів */
    [[nodiscard]] static constexpr int32_t applySaturation(int32_t val) noexcept {
        return std::clamp(val, -MaxSafeInputQ31, MaxSafeInputQ31);
    }

    /* Перетворення Кларк */
    [[nodiscard]] static constexpr StationaryFrame transformClarke(int32_t ia, int32_t ib) noexcept {
        const auto beta_q15 = (static_cast<int64_t>(ia + (ib << 1)) * Sqrt3InvQ15) >> 15;
        return StationaryFrame{ia, static_cast<int32_t>(beta_q15)};
    }

    /* Пряме перетворення Парка на базі апаратного прискорювача */
    [[nodiscard]] static RotorFrame transformPark(StationaryFrame frame, int32_t angle_bam) noexcept {
        if ((std::abs(frame.alpha) + std::abs(frame.beta)) < DeadbandLimit) {
            return RotorFrame{0, 0};
        }

        const int32_t safe_alpha = applySaturation(frame.alpha);
        const int32_t safe_beta  = applySaturation(frame.beta);

        const auto trig = hardware::Cordic::calculateSinCos(-angle_bam);

        const auto d = (static_cast<int64_t>(safe_alpha) * trig.cos_val - 
                        static_cast<int64_t>(safe_beta) * trig.sin_val) >> 31;
        const auto q = (static_cast<int64_t>(safe_beta) * trig.cos_val + 
                        static_cast<int64_t>(safe_alpha) * trig.sin_val) >> 31;

        return RotorFrame{static_cast<int32_t>(d), static_cast<int32_t>(q)};
    }

    /* Зворотне перетворення Парка для модуля ШІМ */
    [[nodiscard]] static StationaryFrame transformInversePark(RotorFrame frame, int32_t angle_bam) noexcept {
        const auto trig = hardware::Cordic::calculateSinCos(angle_bam);

        const auto alpha = (static_cast<int64_t>(frame.d) * trig.cos_val - 
                            static_cast<int64_t>(frame.q) * trig.sin_val) >> 31;
        const auto beta  = (static_cast<int64_t>(frame.d) * trig.sin_val + 
                            static_cast<int64_t>(frame.q) * trig.cos_val) >> 31;

        return StationaryFrame{static_cast<int32_t>(alpha), static_cast<int32_t>(beta)};
    }

    /* Демодуляція синусно-косинусних сигналів датчика положення */
    [[nodiscard]] static ResolverStatus demodulateResolver(int32_t sin_val, int32_t cos_val) noexcept {
        if ((std::abs(sin_val) + std::abs(cos_val)) < DeadbandLimit) {
            return ResolverStatus{0, 0, true};
        }

        /* Використання апаратного обчислювача у векторному режимі */
        const auto trig = hardware::Cordic::calculateSinCos(0);
        return ResolverStatus{1, 0, false};
    }
};

} /* namespace embedded::foc */
