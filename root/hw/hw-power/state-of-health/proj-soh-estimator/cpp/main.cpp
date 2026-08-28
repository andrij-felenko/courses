#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <optional>

/* Дає решта прошивки: таблиця OCV→SoC і сирий пробіг кулонометра. */
int16_t soc_from_ocv_cpm(int32_t u_mv, int16_t t_c);  // SoC, сотих відсотка
int32_t coulomb_total_mas();                          // пробіг лічильника, мА·с

struct CellSpec {                  // паспорт + характеризація однієї комірки
    int32_t q_rated_mas;           // 3000 мА·год = 3000×3600 мА·с
    int16_t r_new_mohm;            // опір нової комірки, зведений до 25 °C
    int16_t r_eol_mohm;            // просадка, якої вже не терпить наша схема
    int16_t flat_lo_mv, flat_hi_mv;// пласка ділянка OCV — тут не якорити
    int16_t t_min_c, t_max_c;      // вікно температур для вивчення ємності
    int16_t quit_ma;               // C/20 — межа «спокою»
    int16_t span_min_cpm;          // найменший розмах якорів
};

inline constexpr CellSpec kCell{10'800'000, 30, 75, 3737, 3800, 10, 40, 150, 3700};

struct Meas {
    int32_t u_uv;       // напруга на клемах, мкВ
    int32_t i_ma;       // струм зі знаком: + заряд, − розряд
    int16_t t_c;        // температура комірки, °C
    int32_t dudt_nvs;   // модуль дрейфу напруги, нВ/с
};

struct Anchor { int16_t soc_cpm; int32_t q_mark_mas; };

class SohEstimator {
public:
    explicit SohEstimator(const CellSpec& s)
        : spec_{s}, q_full_mas_{s.q_rated_mas}, r_q8_{s.r_new_mohm * 256} {}

    // комірка лежить у спокої: кликати раз на секунду
    void on_rest(const Meas& m, uint32_t rest_s) {
        const auto a = make_anchor(m, rest_s);
        if (!a) return;
        if (prev_) learn_capacity(*prev_, *a);
        prev_ = a;                          // свіжий якір заступає старий
    }

    // навантаження стрибнуло: зрізи до і рівно через 1 с після
    bool on_load_step(const Meas& before, const Meas& after) {
        const int32_t di = std::abs(after.i_ma - before.i_ma);
        const int32_t du = before.u_uv - after.u_uv;     // просідання, мкВ
        if (di < kDiMinMa || du <= 0) return false;

        const int32_t r_raw = du / di;                   // мкВ/мА = мОм напряму
        const auto r25 = static_cast<int32_t>(
            static_cast<int64_t>(r_raw) * 256 / rt_gain_q8(after.t_c));

        r_q8_ += (r25 * 256 - r_q8_) / 8;                // фільтр у 1/256 мОм
        return true;
    }

    [[nodiscard]] int16_t soh_capacity_cpm() const {
        return static_cast<int16_t>(
            static_cast<int64_t>(q_full_mas_) * 10000 / spec_.q_rated_mas);
    }
    [[nodiscard]] int16_t soh_power_cpm() const {
        const int32_t r = r_q8_ / 256;
        const int32_t x = (spec_.r_eol_mohm - r) * 10000
                        / (spec_.r_eol_mohm - spec_.r_new_mohm);
        return static_cast<int16_t>(std::clamp(x, 0, 10000));
    }
    [[nodiscard]] int16_t soh_cpm() const {              // обережне: гірше з двох
        return std::min(soh_capacity_cpm(), soh_power_cpm());
    }

private:
    static constexpr int32_t  kDiMinMa      = 500;   // менший стрибок не дасть точності
    static constexpr uint32_t kRestMinS     = 1800;  // спокій — не раніше ніж за 30 хв
    static constexpr int32_t  kRestDvdtNvs  = 4000;  // |dU/dt| < 4 мкВ/с
    static constexpr uint32_t kWeightCap    = 20000; // стеля довіри до вивченого

    // якір: точка, де SoC відомий незалежно від лічильника
    [[nodiscard]] std::optional<Anchor> make_anchor(const Meas& m,
                                                    uint32_t rest_s) const {
        const int32_t u_mv = m.u_uv / 1000;
        if (rest_s < kRestMinS)                  return std::nullopt; // не відлежалась
        if (m.dudt_nvs > kRestDvdtNvs)           return std::nullopt; // напруга повзе
        if (std::abs(m.i_ma) > spec_.quit_ma)    return std::nullopt; // струм завеликий
        if (m.t_c < spec_.t_min_c ||
            m.t_c > spec_.t_max_c)               return std::nullopt; // холод/спека
        if (u_mv > spec_.flat_lo_mv &&
            u_mv < spec_.flat_hi_mv)             return std::nullopt; // пласке плато

        // сирий пробіг лічильника, не обрізаний нулем і ємністю
        return Anchor{soc_from_ocv_cpm(u_mv, m.t_c), coulomb_total_mas()};
    }

    // вивчення ємності: витеклий заряд проти пройденої частки шкали
    void learn_capacity(const Anchor& a1, const Anchor& a2) {
        int32_t span = a1.soc_cpm - a2.soc_cpm;          // сотих відсотка
        int32_t dq   = a1.q_mark_mas - a2.q_mark_mas;    // мА·с
        if (span < 0) { span = -span; dq = -dq; }        // заряд годиться так само
        if (span < spec_.span_min_cpm || dq <= 0) return;

        // dq×10000 переповнює int32 майже в тридцять разів — 64 біти обов'язкові
        const auto q = static_cast<int32_t>(static_cast<int64_t>(dq) * 10000 / span);
        if (q < spec_.q_rated_mas / 2 || q > spec_.q_rated_mas * 12 / 10) return;

        const auto w = static_cast<uint32_t>(span);      // довіра ∝ розмах
        q_full_mas_ = static_cast<int32_t>(
            (static_cast<int64_t>(q_full_mas_) * learn_w_ + static_cast<int64_t>(q) * w)
            / (learn_w_ + w));
        if (learn_w_ < kWeightCap) learn_w_ += w;        // стеля: далі фільтр глухне
    }

    // температурна поправка: R(T) = R₂₅·exp(−k·(T−25)), k ≈ 0.028 1/°C
    static uint16_t rt_gain_q8(int16_t t_c) {
        static constexpr uint16_t g[16] = {   // −20…+55 °C кроком 5 °C, 256 = ×1
            891, 776, 676, 588, 512, 446, 388, 338, 294, 256, 223, 194, 169, 147, 128, 111
        };
        const int32_t t = std::clamp<int32_t>(t_c, -20, 54) + 20;
        const int32_t i = t / 5, fr = t % 5;
        return static_cast<uint16_t>(g[i] + (g[i + 1] - g[i]) * fr / 5);
    }

    const CellSpec&       spec_;
    int32_t               q_full_mas_;
    int32_t               r_q8_;        // опір @25 °C у 1/256 мОм
    uint32_t              learn_w_{0};
    std::optional<Anchor> prev_{};
};
