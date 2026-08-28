#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_CLASSES 16

// Структура для бінарної матриці плутанини
typedef struct {
    uint64_t tp;
    uint64_t fp;
    uint64_t fn;
    uint64_t tn;
} BinaryConfusionMatrix;

// Структура повного звіту бінарних метрик
typedef struct {
    double accuracy;
    double balanced_accuracy;
    double precision;
    double recall;
    double specificity;
    double f1_score;
    double f2_score;
    double f05_score;
    double mcc;
    double cohen_kappa;
    double youden_j;
    double markedness;
} BinaryReport;

// Структура для багатокласової матриці KxK
typedef struct {
    uint32_t num_classes;
    uint64_t matrix[MAX_CLASSES][MAX_CLASSES];
    uint64_t total_samples;
} MulticlassConfusionMatrix;

// Структура багатокласового звіту
typedef struct {
    double precision_per_class[MAX_CLASSES];
    double recall_per_class[MAX_CLASSES];
    double f1_per_class[MAX_CLASSES];
    uint64_t support_per_class[MAX_CLASSES];
    
    double accuracy;
    double macro_precision;
    double macro_recall;
    double macro_f1;
    double weighted_f1;
    double micro_f1;
    double multiclass_mcc;
} MulticlassReport;

// Розрахунок F_beta міри із захистом від ділення на нуль
static inline double calc_f_beta(double p, double r, double beta) {
    double b2 = beta * beta;
    double denom = b2 * p + r;
    if (denom <= 1e-15) return 0.0;
    return (1.0 + b2) * (p * r) / denom;
}

BinaryConfusionMatrix compute_binary_matrix(const uint8_t *actual, const uint8_t *pred, size_t n) {
    BinaryConfusionMatrix cm = {0, 0, 0, 0};
    for (size_t i = 0; i < n; ++i) {
        if (actual[i] != 0) {
            if (pred[i] != 0) cm.tp++;
            else              cm.fn++;
        } else {
            if (pred[i] != 0) cm.fp++;
            else              cm.tn++;
        }
    }
    return cm;
}

BinaryReport evaluate_binary(BinaryConfusionMatrix cm) {
    BinaryReport rep;
    memset(&rep, 0, sizeof(rep));
    double tp = (double)cm.tp;
    double fp = (double)cm.fp;
    double fn = (double)cm.fn;
    double tn = (double)cm.tn;
    double total = tp + fp + fn + tn;
    if (total <= 0.0) return rep;

    rep.accuracy = (tp + tn) / total;

    double p_real = tp + fn;
    double n_real = fp + tn;
    rep.recall      = (p_real > 0.0) ? (tp / p_real) : 0.0;
    rep.specificity = (n_real > 0.0) ? (tn / n_real) : 0.0;
    rep.balanced_accuracy = 0.5 * (rep.recall + rep.specificity);
    rep.youden_j = rep.recall + rep.specificity - 1.0;

    double p_pred = tp + fp;
    double n_pred = fn + tn;
    rep.precision  = (p_pred > 0.0) ? (tp / p_pred) : 0.0;
    double npv     = (n_pred > 0.0) ? (tn / n_pred) : 0.0;
    rep.markedness = rep.precision + npv - 1.0;

    rep.f1_score  = calc_f_beta(rep.precision, rep.recall, 1.0);
    rep.f2_score  = calc_f_beta(rep.precision, rep.recall, 2.0);
    rep.f05_score = calc_f_beta(rep.precision, rep.recall, 0.5);

    double num_mcc = (tp * tn) - (fp * fn);
    double den_mcc = sqrt(p_pred * p_real * n_pred * n_real);
    rep.mcc = (den_mcc > 1e-15) ? (num_mcc / den_mcc) : 0.0;

    double p_o = rep.accuracy;
    double p_e = ((p_pred * p_real) + (n_pred * n_real)) / (total * total);
    double den_kappa = 1.0 - p_e;
    rep.cohen_kappa = (fabs(den_kappa) > 1e-15) ? ((p_o - p_e) / den_kappa) : 0.0;

    return rep;
}

MulticlassConfusionMatrix create_multiclass_matrix(uint32_t k) {
    MulticlassConfusionMatrix cm;
    cm.num_classes = (k > MAX_CLASSES) ? MAX_CLASSES : k;
    cm.total_samples = 0;
    memset(cm.matrix, 0, sizeof(cm.matrix));
    return cm;
}

void update_multiclass_matrix(MulticlassConfusionMatrix *cm, const uint32_t *actual, const uint32_t *pred, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        uint32_t a = actual[i];
        uint32_t p = pred[i];
        if (a < cm->num_classes && p < cm->num_classes) {
            cm->matrix[a][p]++;
            cm->total_samples++;
        }
    }
}

MulticlassReport evaluate_multiclass(const MulticlassConfusionMatrix *cm) {
    MulticlassReport rep;
    memset(&rep, 0, sizeof(rep));
    uint32_t K = cm->num_classes;
    if (cm->total_samples == 0 || K == 0) return rep;

    uint64_t total_correct = 0;
    double macro_p_sum = 0.0, macro_r_sum = 0.0, macro_f1_sum = 0.0;
    double weighted_f1_sum = 0.0;

    for (uint32_t k = 0; k < K; ++k) {
        uint64_t tp = cm->matrix[k][k];
        total_correct += tp;

        uint64_t row_sum = 0;
        uint64_t col_sum = 0;
        for (uint32_t i = 0; i < K; ++i) {
            row_sum += cm->matrix[k][i];
            col_sum += cm->matrix[i][k];
        }
        rep.support_per_class[k] = row_sum;

        double prec = (col_sum > 0) ? ((double)tp / (double)col_sum) : 0.0;
        double rec  = (row_sum > 0) ? ((double)tp / (double)row_sum) : 0.0;
        double f1   = (prec + rec > 1e-15) ? (2.0 * prec * rec / (prec + rec)) : 0.0;

        rep.precision_per_class[k] = prec;
        rep.recall_per_class[k]    = rec;
        rep.f1_per_class[k]        = f1;

        macro_p_sum += prec;
        macro_r_sum += rec;
        macro_f1_sum += f1;
        weighted_f1_sum += f1 * (double)row_sum;
    }

    rep.accuracy = (double)total_correct / (double)cm->total_samples;
    rep.macro_precision = macro_p_sum / (double)K;
    rep.macro_recall    = macro_r_sum / (double)K;
    rep.macro_f1        = macro_f1_sum / (double)K;
    rep.weighted_f1     = weighted_f1_sum / (double)cm->total_samples;
    rep.micro_f1        = rep.accuracy;

    // Gorodkin Multiclass MCC
    double num_mcc = 0.0;
    for (uint32_t k = 0; k < K; ++k) {
        for (uint32_t i = 0; i < K; ++i) {
            for (uint32_t j = 0; j < K; ++j) {
                num_mcc += (double)cm->matrix[k][k] * (double)cm->matrix[i][j] -
                           (double)cm->matrix[k][i] * (double)cm->matrix[j][k];
            }
        }
    }

    double d1 = 0.0, d2 = 0.0;
    for (uint32_t k = 0; k < K; ++k) {
        double row_k = 0.0, col_k = 0.0;
        for (uint32_t i = 0; i < K; ++i) {
            row_k += (double)cm->matrix[k][i];
            col_k += (double)cm->matrix[i][k];
        }
        d1 += row_k * ((double)cm->total_samples - row_k);
        d2 += col_k * ((double)cm->total_samples - col_k);
    }

    double den_mcc = sqrt(d1) * sqrt(d2);
    rep.multiclass_mcc = (den_mcc > 1e-15) ? (num_mcc / den_mcc) : 0.0;

    return rep;
}
