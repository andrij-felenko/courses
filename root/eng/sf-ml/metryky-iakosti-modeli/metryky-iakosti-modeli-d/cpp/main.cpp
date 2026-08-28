#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <cstdint>
#include <numeric>
#include <algorithm>

struct BinaryConfusionMatrix {
    uint64_t tp{0};
    uint64_t fp{0};
    uint64_t fn{0};
    uint64_t tn{0};

    [[nodiscard]] constexpr uint64_t total() const noexcept {
        return tp + fp + fn + tn;
    }
};

struct BinaryReport {
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

struct MulticlassReport {
    std::vector<double> precision_per_class;
    std::vector<double> recall_per_class;
    std::vector<double> f1_per_class;
    std::vector<uint64_t> support_per_class;

    double accuracy{0.0};
    double macro_precision{0.0};
    double macro_recall{0.0};
    double macro_f1{0.0};
    double weighted_f1{0.0};
    double micro_f1{0.0};
    double multiclass_mcc{0.0};
};

class MetricsEngine {
public:
    [[nodiscard]] static BinaryConfusionMatrix compute_binary(
        std::span<const uint8_t> actual,
        std::span<const uint8_t> pred) noexcept 
    {
        BinaryConfusionMatrix cm;
        const size_t n = std::min(actual.size(), pred.size());
        for (size_t i = 0; i < n; ++i) {
            const bool yt = (actual[i] != 0);
            const bool yp = (pred[i] != 0);
            if (yt && yp)        ++cm.tp;
            else if (!yt && yp)  ++cm.fp;
            else if (yt && !yp)  ++cm.fn;
            else                 ++cm.tn;
        }
        return cm;
    }

    [[nodiscard]] static BinaryReport evaluate_binary(const BinaryConfusionMatrix& cm) noexcept {
        BinaryReport rep;
        const double tp = static_cast<double>(cm.tp);
        const double fp = static_cast<double>(cm.fp);
        const double fn = static_cast<double>(cm.fn);
        const double tn = static_cast<double>(cm.tn);
        const double total = static_cast<double>(cm.total());
        if (total <= 0.0) return rep;

        rep.accuracy = (tp + tn) / total;

        const double p_real = tp + fn;
        const double n_real = fp + tn;
        rep.recall      = (p_real > 0.0) ? (tp / p_real) : 0.0;
        rep.specificity = (n_real > 0.0) ? (tn / n_real) : 0.0;
        rep.balanced_accuracy = 0.5 * (rep.recall + rep.specificity);
        rep.youden_j = rep.recall + rep.specificity - 1.0;

        const double p_pred = tp + fp;
        const double n_pred = fn + tn;
        rep.precision  = (p_pred > 0.0) ? (tp / p_pred) : 0.0;
        const double npv = (n_pred > 0.0) ? (tn / n_pred) : 0.0;
        rep.markedness = rep.precision + npv - 1.0;

        rep.f1_score  = calc_f_beta(rep.precision, rep.recall, 1.0);
        rep.f2_score  = calc_f_beta(rep.precision, rep.recall, 2.0);
        rep.f05_score = calc_f_beta(rep.precision, rep.recall, 0.5);

        const double num_mcc = (tp * tn) - (fp * fn);
        const double den_mcc = std::sqrt(p_pred * p_real * n_pred * n_real);
        rep.mcc = (den_mcc > 1e-15) ? (num_mcc / den_mcc) : 0.0;

        const double p_o = rep.accuracy;
        const double p_e = ((p_pred * p_real) + (n_pred * n_real)) / (total * total);
        const double den_kappa = 1.0 - p_e;
        rep.cohen_kappa = (std::abs(den_kappa) > 1e-15) ? ((p_o - p_e) / den_kappa) : 0.0;

        return rep;
    }

private:
    [[nodiscard]] static constexpr double calc_f_beta(
        double p, double r, double beta) noexcept 
    {
        const double b2 = beta * beta;
        const double denom = b2 * p + r;
        if (denom <= 1e-15) return 0.0;
        return (1.0 + b2) * (p * r) / denom;
    }
};

class MulticlassMetricsEngine {
public:
    explicit MulticlassMetricsEngine(size_t num_classes)
        : k_(num_classes), matrix_(num_classes * num_classes, 0) {}

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
        if (total_samples_ == 0 || k_ == 0) return rep;

        rep.precision_per_class.resize(k_, 0.0);
        rep.recall_per_class.resize(k_, 0.0);
        rep.f1_per_class.resize(k_, 0.0);
        rep.support_per_class.resize(k_, 0);

        uint64_t total_correct = 0;
        double macro_p_sum = 0.0, macro_r_sum = 0.0, macro_f1_sum = 0.0;
        double weighted_f1_sum = 0.0;

        for (size_t k = 0; k < k_; ++k) {
            const uint64_t tp = matrix_[k * k_ + k];
            total_correct += tp;

            uint64_t row_sum = 0;
            uint64_t col_sum = 0;
            for (size_t i = 0; i < k_; ++i) {
                row_sum += matrix_[k * k_ + i];
                col_sum += matrix_[i * k_ + k];
            }
            rep.support_per_class[k] = row_sum;

            const double prec = (col_sum > 0) ? (static_cast<double>(tp) / col_sum) : 0.0;
            const double rec  = (row_sum > 0) ? (static_cast<double>(tp) / row_sum) : 0.0;
            const double f1   = (prec + rec > 1e-15) ? (2.0 * prec * rec / (prec + rec)) : 0.0;

            rep.precision_per_class[k] = prec;
            rep.recall_per_class[k]    = rec;
            rep.f1_per_class[k]        = f1;

            macro_p_sum += prec;
            macro_r_sum += rec;
            macro_f1_sum += f1;
            weighted_f1_sum += f1 * static_cast<double>(row_sum);
        }

        rep.accuracy = static_cast<double>(total_correct) / static_cast<double>(total_samples_);
        rep.macro_precision = macro_p_sum / static_cast<double>(k_);
        rep.macro_recall    = macro_r_sum / static_cast<double>(k_);
        rep.macro_f1        = macro_f1_sum / static_cast<double>(k_);
        rep.weighted_f1     = weighted_f1_sum / static_cast<double>(total_samples_);
        rep.micro_f1        = rep.accuracy;

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
        const double tot = static_cast<double>(total_samples_);
        for (size_t k = 0; k < k_; ++k) {
            double row_k = 0.0, col_k = 0.0;
            for (size_t i = 0; i < k_; ++i) {
                row_k += static_cast<double>(matrix_[k * k_ + i]);
                col_k += static_cast<double>(matrix_[i * k_ + k]);
            }
            d1 += row_k * (tot - row_k);
            d2 += col_k * (tot - col_k);
        }

        const double den_mcc = std::sqrt(d1) * std::sqrt(d2);
        rep.multiclass_mcc = (den_mcc > 1e-15) ? (num_mcc / den_mcc) : 0.0;

        return rep;
    }

private:
    size_t k_{0};
    uint64_t total_samples_{0};
    std::vector<uint64_t> matrix_;
};
