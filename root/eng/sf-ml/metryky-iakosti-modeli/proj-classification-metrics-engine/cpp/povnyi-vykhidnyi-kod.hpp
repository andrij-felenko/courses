#ifndef METRICS_ENGINE_HPP
#define METRICS_ENGINE_HPP

#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <cstdint>
#include <numeric>
#include <algorithm>
#include <array>
#include <bit>

namespace metrics {

constexpr double kEpsilon = 1e-15;
constexpr size_t kMaxClasses = 32;
constexpr size_t kNumBins = 10;

struct BinaryReport {
    uint64_t tp{0};
    uint64_t fp{0};
    uint64_t fn{0};
    uint64_t tn{0};
    uint64_t total{0};

    double accuracy{0.0};
    double balanced_accuracy{0.0};
    double precision{0.0};
    double recall{0.0};
    double specificity{0.0};
    double f1_score{0.0};
    double f2_score{0.0};
    double f05_score{0.0};
    double mcc{0.0};
    double cohen_kappa{0.0};
    double youden_j{0.0};
    double markedness{0.0};
};

struct MetricSample {
    double score{0.0};
    uint8_t label{0};

    [[nodiscard]] constexpr bool operator>(const MetricSample& other) const noexcept {
        return score > other.score;
    }
};

struct MulticlassReport {
    uint32_t num_classes{0};
    uint64_t total_samples{0};
    double accuracy{0.0};
    double macro_precision{0.0};
    double macro_recall{0.0};
    double macro_f1{0.0};
    double weighted_f1{0.0};
    double micro_f1{0.0};
    double multiclass_mcc{0.0};

    std::vector<double> class_precision;
    std::vector<double> class_recall;
    std::vector<double> class_f1;
    std::vector<uint64_t> class_support;
};

struct CurvesResult {
    double roc_auc{0.0};
    double pr_auc{0.0};
};

// ----------------------------------------------------------------------------
// Безрозгалужений бінарний накопичувач C++20
// ----------------------------------------------------------------------------

class alignas(64) FastBinaryAccumulator {
public:
    constexpr FastBinaryAccumulator() noexcept = default;

    void reset() noexcept {
        counters_.fill(0);
    }

    void update_single(uint8_t actual, uint8_t pred) noexcept {
        const uint32_t idx = (static_cast<uint32_t>(actual != 0) << 1) |
                             static_cast<uint32_t>(pred != 0);
        ++counters_[idx];
    }

    void update_batch(std::span<const uint8_t> actual, std::span<const uint8_t> pred) noexcept {
        const size_t n = std::min(actual.size(), pred.size());
        for (size_t i = 0; i < n; ++i) {
            const uint32_t idx = (static_cast<uint32_t>(actual[i] != 0) << 1) |
                                 static_cast<uint32_t>(pred[i] != 0);
            ++counters_[idx];
        }
    }

    [[nodiscard]] BinaryReport evaluate() const noexcept {
        BinaryReport rep;
        rep.tn = counters_[0];
        rep.fp = counters_[1];
        rep.fn = counters_[2];
        rep.tp = counters_[3];
        rep.total = rep.tn + rep.fp + rep.fn + rep.tp;

        if (rep.total == 0) return rep;

        const double tp = static_cast<double>(rep.tp);
        const double fp = static_cast<double>(rep.fp);
        const double fn = static_cast<double>(rep.fn);
        const double tn = static_cast<double>(rep.tn);
        const double total = static_cast<double>(rep.total);

        rep.accuracy = (tp + tn) / total;

        const double p_real = tp + fn;
        const double n_real = fp + tn;
        rep.recall      = (p_real > kEpsilon) ? (tp / p_real) : 0.0;
        rep.specificity = (n_real > kEpsilon) ? (tn / n_real) : 0.0;
        rep.balanced_accuracy = 0.5 * (rep.recall + rep.specificity);
        rep.youden_j = rep.recall + rep.specificity - 1.0;

        const double p_pred = tp + fp;
        const double n_pred = fn + tn;
        rep.precision  = (p_pred > kEpsilon) ? (tp / p_pred) : 0.0;
        const double npv = (n_pred > kEpsilon) ? (tn / n_pred) : 0.0;
        rep.markedness = rep.precision + npv - 1.0;

        rep.f1_score  = calc_f_beta(rep.precision, rep.recall, 1.0);
        rep.f2_score  = calc_f_beta(rep.precision, rep.recall, 2.0);
        rep.f05_score = calc_f_beta(rep.precision, rep.recall, 0.5);

        const double num_mcc = (tp * tn) - (fp * fn);
        const double den_mcc = std::sqrt(p_pred * p_real * n_pred * n_real);
        rep.mcc = (den_mcc > kEpsilon) ? (num_mcc / den_mcc) : 0.0;

        const double p_o = rep.accuracy;
        const double p_e = ((p_pred * p_real) + (n_pred * n_real)) / (total * total);
        const double den_kappa = 1.0 - p_e;
        rep.cohen_kappa = (std::abs(den_kappa) > kEpsilon) ? ((p_o - p_e) / den_kappa) : 0.0;

        return rep;
    }

private:
    [[nodiscard]] static constexpr double calc_f_beta(double p, double r, double beta) noexcept {
        const double b2 = beta * beta;
        const double denom = b2 * p + r;
        if (denom <= kEpsilon) return 0.0;
        return (1.0 + b2) * (p * r) / denom;
    }

    std::array<uint64_t, 4> counters_{0, 0, 0, 0};
};

// ----------------------------------------------------------------------------
// Сканування кривих ROC-AUC та PR-AUC
// ----------------------------------------------------------------------------

[[nodiscard]] inline CurvesResult compute_curves(std::span<MetricSample> samples) {
    if (samples.empty()) return {0.0, 0.0};

    uint64_t total_p = 0;
    uint64_t total_n = 0;
    for (const auto& s : samples) {
        if (s.label != 0) ++total_p;
        else              ++total_n;
    }

    if (total_p == 0 || total_n == 0) {
        return {0.5, (total_p > 0 ? 1.0 : 0.0)};
    }

    std::sort(samples.begin(), samples.end(), std::greater<MetricSample>());

    double roc_auc_sum = 0.0;
    double pr_auc_sum  = 0.0;
    double prev_fpr    = 0.0;
    double prev_tpr    = 0.0;
    double prev_recall = 0.0;

    uint64_t cum_tp = 0;
    uint64_t cum_fp = 0;

    const double p_double = static_cast<double>(total_p);
    const double n_double = static_cast<double>(total_n);

    size_t i = 0;
    const size_t n = samples.size();
    while (i < n) {
        size_t j = i;
        uint64_t block_tp = 0;
        uint64_t block_fp = 0;

        while (j < n && std::abs(samples[j].score - samples[i].score) < 1e-12) {
            if (samples[j].label != 0) ++block_tp;
            else                      ++block_fp;
            ++j;
        }

        cum_tp += block_tp;
        cum_fp += block_fp;

        const double curr_tpr = static_cast<double>(cum_tp) / p_double;
        const double curr_fpr = static_cast<double>(cum_fp) / n_double;
        const double curr_recall = curr_tpr;
        const double curr_precision = static_cast<double>(cum_tp) / static_cast<double>(cum_tp + cum_fp);

        roc_auc_sum += (curr_fpr - prev_fpr) * (prev_tpr + curr_tpr) * 0.5;
        pr_auc_sum  += (curr_recall - prev_recall) * curr_precision;

        prev_fpr = curr_fpr;
        prev_tpr = curr_tpr;
        prev_recall = curr_recall;
        i = j;
    }

    return {roc_auc_sum, pr_auc_sum};
}

// ----------------------------------------------------------------------------
// Багатокласовий рушій
// ----------------------------------------------------------------------------

class FastMulticlassEngine {
public:
    explicit FastMulticlassEngine(size_t num_classes)
        : k_(std::min(num_classes, kMaxClasses)), matrix_(k_ * k_, 0) {}

    void update(std::span<const uint32_t> actual, std::span<const uint32_t> pred) noexcept {
        const size_t n = std::min(actual.size(), pred.size());
        for (size_t i = 0; i < n; ++i) {
            const size_t a = actual[i];
            const size_t p = pred[i];
            if (a < k_ && p < k_) {
                ++matrix_[a * k_ + p];
                ++total_samples_;
            }
        }
    }

    [[nodiscard]] MulticlassReport evaluate() const {
        MulticlassReport rep;
        rep.num_classes = static_cast<uint32_t>(k_);
        rep.total_samples = total_samples_;

        if (total_samples_ == 0 || k_ == 0) return rep;

        rep.class_precision.resize(k_, 0.0);
        rep.class_recall.resize(k_, 0.0);
        rep.class_f1.resize(k_, 0.0);
        rep.class_support.resize(k_, 0);

        uint64_t total_correct = 0;
        double macro_p_acc = 0.0;
        double macro_r_acc = 0.0;
        double macro_f1_acc = 0.0;
        double weighted_f1_acc = 0.0;

        for (size_t k = 0; k < k_; ++k) {
            const uint64_t tp = matrix_[k * k_ + k];
            total_correct += tp;

            uint64_t row_sum = 0;
            uint64_t col_sum = 0;
            for (size_t i = 0; i < k_; ++i) {
                row_sum += matrix_[k * k_ + i];
                col_sum += matrix_[i * k_ + k];
            }
            rep.class_support[k] = row_sum;

            const double prec = (col_sum > 0) ? (static_cast<double>(tp) / col_sum) : 0.0;
            const double rec  = (row_sum > 0) ? (static_cast<double>(tp) / row_sum) : 0.0;
            const double f1   = (prec + rec > kEpsilon) ? (2.0 * prec * rec / (prec + rec)) : 0.0;

            rep.class_precision[k] = prec;
            rep.class_recall[k]    = rec;
            rep.class_f1[k]        = f1;

            macro_p_acc += prec;
            macro_r_acc += rec;
            macro_f1_acc += f1;
            weighted_f1_acc += f1 * static_cast<double>(row_sum);
        }

        const double total_d = static_cast<double>(total_samples_);
        rep.accuracy = static_cast<double>(total_correct) / total_d;
        rep.micro_f1 = rep.accuracy;
        rep.macro_precision = macro_p_acc / static_cast<double>(k_);
        rep.macro_recall    = macro_r_acc / static_cast<double>(k_);
        rep.macro_f1        = macro_f1_acc / static_cast<double>(k_);
        rep.weighted_f1     = weighted_f1_acc / total_d;

        // Gorodkin Multiclass MCC
        double num_mcc = 0.0;
        for (size_t k = 0; k < k_; ++k) {
            for (size_t i = 0; i < k_; ++i) {
                for (size_t j = 0; j < k_; ++j) {
                    num_mcc += static_cast<double>(matrix_[k * k_ + k]) * static_cast<double>(matrix_[i * k_ + j]) -
                               static_cast<double>(matrix_[k * k_ + i]) * static_cast<double>(matrix_[j * k_ + k]);
                }
            }
        }

        double d1 = 0.0, d2 = 0.0;
        for (size_t k = 0; k < k_; ++k) {
            double row_k = 0.0, col_k = 0.0;
            for (size_t i = 0; i < k_; ++i) {
                row_k += static_cast<double>(matrix_[k * k_ + i]);
                col_k += static_cast<double>(matrix_[i * k_ + k]);
            }
            d1 += row_k * (total_d - row_k);
            d2 += col_k * (total_d - col_k);
        }

        const double den_mcc = std::sqrt(d1) * std::sqrt(d2);
        rep.multiclass_mcc = (den_mcc > kEpsilon) ? (num_mcc / den_mcc) : 0.0;

        return rep;
    }

private:
    size_t k_{0};
    uint64_t total_samples_{0};
    std::vector<uint64_t> matrix_;
};

// ----------------------------------------------------------------------------
// Мультилейбловий накопичувач на бітових масках
// ----------------------------------------------------------------------------

class FastMultilabelAccumulator {
public:
    explicit FastMultilabelAccumulator(uint32_t num_labels = 64) noexcept
        : num_labels_(std::min(num_labels, 64u)) {}

    void update_single(uint64_t actual_mask, uint64_t pred_mask) noexcept {
        ++total_samples_;
        if (actual_mask == pred_mask) {
            ++exact_matches_;
        }

        const uint64_t diff = actual_mask ^ pred_mask;
        total_bit_errors_ += std::popcount(diff);

        const uint64_t inter = actual_mask & pred_mask;
        const uint64_t uni   = actual_mask | pred_mask;
        if (uni == 0) {
            jaccard_sum_ += 1.0;
        } else {
            jaccard_sum_ += static_cast<double>(std::popcount(inter)) / static_cast<double>(std::popcount(uni));
        }
    }

    [[nodiscard]] double hamming_loss() const noexcept {
        if (total_samples_ == 0 || num_labels_ == 0) return 0.0;
        return static_cast<double>(total_bit_errors_) / 
               (static_cast<double>(total_samples_) * static_cast<double>(num_labels_));
    }

    [[nodiscard]] double subset_accuracy() const noexcept {
        if (total_samples_ == 0) return 0.0;
        return static_cast<double>(exact_matches_) / static_cast<double>(total_samples_);
    }

    [[nodiscard]] double mean_jaccard() const noexcept {
        if (total_samples_ == 0) return 0.0;
        return jaccard_sum_ / static_cast<double>(total_samples_);
    }

private:
    uint64_t total_samples_{0};
    uint32_t num_labels_{64};
    uint64_t exact_matches_{0};
    uint64_t total_bit_errors_{0};
    double   jaccard_sum_{0.0};
};

// ----------------------------------------------------------------------------
// Ковзний експоненційний накопичувач (EMA)
// ----------------------------------------------------------------------------

class FastEmaAccumulator {
public:
    explicit FastEmaAccumulator(double gamma = 0.999) noexcept : gamma_(gamma) {}

    void update(uint8_t actual, uint8_t pred) noexcept {
        const double s_tp = (actual != 0 && pred != 0) ? 1.0 : 0.0;
        const double s_fp = (actual == 0 && pred != 0) ? 1.0 : 0.0;
        const double s_fn = (actual != 0 && pred == 0) ? 1.0 : 0.0;
        const double s_tn = (actual == 0 && pred == 0) ? 1.0 : 0.0;

        if (!initialized_) {
            tp_ema_ = s_tp;
            fp_ema_ = s_fp;
            fn_ema_ = s_fn;
            tn_ema_ = s_tn;
            initialized_ = true;
        } else {
            tp_ema_ = gamma_ * tp_ema_ + (1.0 - gamma_) * s_tp;
            fp_ema_ = gamma_ * fp_ema_ + (1.0 - gamma_) * s_fp;
            fn_ema_ = gamma_ * fn_ema_ + (1.0 - gamma_) * s_fn;
            tn_ema_ = gamma_ * tn_ema_ + (1.0 - gamma_) * s_tn;
        }
    }

    [[nodiscard]] double precision() const noexcept {
        const double denom = tp_ema_ + fp_ema_;
        return (denom > kEpsilon) ? (tp_ema_ / denom) : 0.0;
    }

    [[nodiscard]] double recall() const noexcept {
        const double denom = tp_ema_ + fn_ema_;
        return (denom > kEpsilon) ? (tp_ema_ / denom) : 0.0;
    }

    [[nodiscard]] double f1_score() const noexcept {
        const double p = precision();
        const double r = recall();
        const double denom = p + r;
        return (denom > kEpsilon) ? (2.0 * p * r / denom) : 0.0;
    }

private:
    double gamma_{0.999};
    double tp_ema_{0.0};
    double fp_ema_{0.0};
    double fn_ema_{0.0};
    double tn_ema_{0.0};
    bool   initialized_{false};
};

// ----------------------------------------------------------------------------
// Потоковий калібрувальний накопичувач (ECE & Brier Score)
// ----------------------------------------------------------------------------

class FastCalibrationAccumulator {
public:
    FastCalibrationAccumulator() noexcept = default;

    void update(double prob, uint8_t actual) noexcept {
        ++total_samples_;
        const double y = (actual != 0) ? 1.0 : 0.0;
        const double err = prob - y;
        brier_sum_ += err * err;

        size_t bin_idx = static_cast<size_t>(prob * static_cast<double>(kNumBins));
        if (bin_idx >= kNumBins) bin_idx = kNumBins - 1;

        ++bins_[bin_idx].count;
        bins_[bin_idx].sum_conf += prob;
        bins_[bin_idx].sum_actual += y;
    }

    [[nodiscard]] double ece() const noexcept {
        if (total_samples_ == 0) return 0.0;
        double ece_sum = 0.0;
        const double total_d = static_cast<double>(total_samples_);

        for (const auto& b : bins_) {
            if (b.count > 0) {
                const double bin_size = static_cast<double>(b.count);
                const double avg_conf = b.sum_conf / bin_size;
                const double avg_acc  = b.sum_actual / bin_size;
                ece_sum += (bin_size / total_d) * std::abs(avg_acc - avg_conf);
            }
        }
        return ece_sum;
    }

    [[nodiscard]] double brier_score() const noexcept {
        if (total_samples_ == 0) return 0.0;
        return brier_sum_ / static_cast<double>(total_samples_);
    }

private:
    struct Bin {
        uint64_t count{0};
        double   sum_conf{0.0};
        double   sum_actual{0.0};
    };

    uint64_t total_samples_{0};
    double   brier_sum_{0.0};
    std::array<Bin, kNumBins> bins_{};
};

} // namespace metrics

#endif // METRICS_ENGINE_HPP
