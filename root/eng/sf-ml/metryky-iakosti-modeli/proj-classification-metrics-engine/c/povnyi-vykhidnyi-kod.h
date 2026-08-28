#ifndef METRICS_ENGINE_H
#define METRICS_ENGINE_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

#define METRICS_MAX_CLASSES 32
#define METRICS_NUM_BINS    10
#define METRICS_EPSILON     1e-15

// Вирівняний накопичувач бінарної матриці плутанини
typedef struct {
    uint64_t counters[4]; // [0]=TN, [1]=FP, [2]=FN, [3]=TP
} FastBinaryAccumulator;

// Структура повного звіту бінарних метрик
typedef struct {
    uint64_t tp;
    uint64_t fp;
    uint64_t fn;
    uint64_t tn;
    uint64_t total;
    
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
} FastBinaryReport;

// Елемент для порового сканування ROC/PR кривих
typedef struct {
    double score;
    uint8_t label;
} MetricSample;

// Багатокласова матриця плутанини K x K
typedef struct {
    uint32_t num_classes;
    uint64_t total_samples;
    uint64_t matrix[METRICS_MAX_CLASSES][METRICS_MAX_CLASSES];
} FastMulticlassMatrix;

// Багатокласовий звіт якості
typedef struct {
    uint32_t num_classes;
    uint64_t total_samples;
    double accuracy;
    double macro_precision;
    double macro_recall;
    double macro_f1;
    double weighted_f1;
    double micro_f1;
    double multiclass_mcc;
    
    double class_precision[METRICS_MAX_CLASSES];
    double class_recall[METRICS_MAX_CLASSES];
    double class_f1[METRICS_MAX_CLASSES];
    uint64_t class_support[METRICS_MAX_CLASSES];
} FastMulticlassReport;

// Накопичувач мультилейблових метрик на бітових масках
typedef struct {
    uint64_t total_samples;
    uint32_t num_labels;
    uint64_t exact_matches;
    uint64_t total_bit_errors;
    double   jaccard_sum;
} FastMultilabelAccumulator;

// Ковзний експоненційний накопичувач метрик (EMA)
typedef struct {
    double gamma;
    double tp_ema;
    double fp_ema;
    double fn_ema;
    double tn_ema;
    bool   initialized;
} FastEmaAccumulator;

// Потоковий накопичувач калібрування ECE та Brier Score
typedef struct {
    uint64_t total_samples;
    double   brier_sum;
    struct {
        uint64_t count;
        double   sum_conf;
        double   sum_actual;
    } bins[METRICS_NUM_BINS];
} FastCalibrationAccumulator;

// ----------------------------------------------------------------------------
// Реалізація функцій бінарного накопичувача
// ----------------------------------------------------------------------------

static inline void fast_binary_init(FastBinaryAccumulator *acc) {
    acc->counters[0] = 0;
    acc->counters[1] = 0;
    acc->counters[2] = 0;
    acc->counters[3] = 0;
}

static inline void fast_binary_update_single(FastBinaryAccumulator *acc, uint8_t actual, uint8_t pred) {
    uint32_t idx = ((uint32_t)(actual != 0) << 1) | (uint32_t)(pred != 0);
    acc->counters[idx]++;
}

static inline void fast_binary_update_batch(FastBinaryAccumulator *acc, 
                                            const uint8_t *actual, 
                                            const uint8_t *pred, 
                                            size_t n) 
{
    for (size_t i = 0; i < n; ++i) {
        uint32_t idx = ((uint32_t)(actual[i] != 0) << 1) | (uint32_t)(pred[i] != 0);
        acc->counters[idx]++;
    }
}

static inline double safe_calc_fbeta(double p, double r, double beta) {
    double b2 = beta * beta;
    double denom = b2 * p + r;
    if (denom <= METRICS_EPSILON) return 0.0;
    return (1.0 + b2) * (p * r) / denom;
}

static inline FastBinaryReport fast_binary_evaluate(const FastBinaryAccumulator *acc) {
    FastBinaryReport rep;
    memset(&rep, 0, sizeof(rep));
    
    rep.tn = acc->counters[0];
    rep.fp = acc->counters[1];
    rep.fn = acc->counters[2];
    rep.tp = acc->counters[3];
    rep.total = rep.tn + rep.fp + rep.fn + rep.tp;
    
    if (rep.total == 0) return rep;
    
    double tp = (double)rep.tp;
    double fp = (double)rep.fp;
    double fn = (double)rep.fn;
    double tn = (double)rep.tn;
    double total = (double)rep.total;
    
    rep.accuracy = (tp + tn) / total;
    
    double p_real = tp + fn;
    double n_real = fp + tn;
    rep.recall      = (p_real > METRICS_EPSILON) ? (tp / p_real) : 0.0;
    rep.specificity = (n_real > METRICS_EPSILON) ? (tn / n_real) : 0.0;
    rep.balanced_accuracy = 0.5 * (rep.recall + rep.specificity);
    rep.youden_j = rep.recall + rep.specificity - 1.0;
    
    double p_pred = tp + fp;
    double n_pred = fn + tn;
    rep.precision  = (p_pred > METRICS_EPSILON) ? (tp / p_pred) : 0.0;
    double npv     = (n_pred > METRICS_EPSILON) ? (tn / n_pred) : 0.0;
    rep.markedness = rep.precision + npv - 1.0;
    
    rep.f1_score  = safe_calc_fbeta(rep.precision, rep.recall, 1.0);
    rep.f2_score  = safe_calc_fbeta(rep.precision, rep.recall, 2.0);
    rep.f05_score = safe_calc_fbeta(rep.precision, rep.recall, 0.5);
    
    double num_mcc = (tp * tn) - (fp * fn);
    double den_mcc = sqrt(p_pred * p_real * n_pred * n_real);
    rep.mcc = (den_mcc > METRICS_EPSILON) ? (num_mcc / den_mcc) : 0.0;
    
    double p_o = rep.accuracy;
    double p_e = ((p_pred * p_real) + (n_pred * n_real)) / (total * total);
    double den_kappa = 1.0 - p_e;
    rep.cohen_kappa = (fabs(den_kappa) > METRICS_EPSILON) ? ((p_o - p_e) / den_kappa) : 0.0;
    
    return rep;
}

// ----------------------------------------------------------------------------
// Інтегрування ROC-AUC та Average Precision
// ----------------------------------------------------------------------------

static int compare_metric_samples_desc(const void *a, const void *b) {
    const MetricSample *sa = (const MetricSample *)a;
    const MetricSample *sb = (const MetricSample *)b;
    if (sa->score < sb->score) return 1;
    if (sa->score > sb->score) return -1;
    return 0;
}

static inline void fast_compute_curves_auc(MetricSample *samples, 
                                           size_t n, 
                                           double *out_roc_auc, 
                                           double *out_pr_auc) 
{
    if (n == 0) {
        *out_roc_auc = 0.0;
        *out_pr_auc = 0.0;
        return;
    }
    
    uint64_t total_p = 0;
    uint64_t total_n = 0;
    for (size_t i = 0; i < n; ++i) {
        if (samples[i].label != 0) total_p++;
        else                      total_n++;
    }
    
    if (total_p == 0 || total_n == 0) {
        *out_roc_auc = 0.5;
        *out_pr_auc = (total_p > 0) ? 1.0 : 0.0;
        return;
    }
    
    qsort(samples, n, sizeof(MetricSample), compare_metric_samples_desc);
    
    double roc_auc_sum = 0.0;
    double pr_auc_sum  = 0.0;
    double prev_fpr    = 0.0;
    double prev_tpr    = 0.0;
    double prev_recall = 0.0;
    
    uint64_t cum_tp = 0;
    uint64_t cum_fp = 0;
    
    double p_double = (double)total_p;
    double n_double = (double)total_n;
    
    size_t i = 0;
    while (i < n) {
        size_t j = i;
        uint64_t block_tp = 0;
        uint64_t block_fp = 0;
        
        while (j < n && fabs(samples[j].score - samples[i].score) < 1e-12) {
            if (samples[j].label != 0) block_tp++;
            else                      block_fp++;
            j++;
        }
        
        cum_tp += block_tp;
        cum_fp += block_fp;
        
        double curr_tpr = (double)cum_tp / p_double;
        double curr_fpr = (double)cum_fp / n_double;
        double curr_recall = curr_tpr;
        double curr_precision = (double)cum_tp / (double)(cum_tp + cum_fp);
        
        roc_auc_sum += (curr_fpr - prev_fpr) * (prev_tpr + curr_tpr) * 0.5;
        pr_auc_sum  += (curr_recall - prev_recall) * curr_precision;
        
        prev_fpr = curr_fpr;
        prev_tpr = curr_tpr;
        prev_recall = curr_recall;
        i = j;
    }
    
    *out_roc_auc = roc_auc_sum;
    *out_pr_auc  = pr_auc_sum;
}

// ----------------------------------------------------------------------------
// Багатокласовий модуль
// ----------------------------------------------------------------------------

static inline void fast_multiclass_init(FastMulticlassMatrix *cm, uint32_t num_classes) {
    cm->num_classes = (num_classes > METRICS_MAX_CLASSES) ? METRICS_MAX_CLASSES : num_classes;
    cm->total_samples = 0;
    memset(cm->matrix, 0, sizeof(cm->matrix));
}

static inline void fast_multiclass_update(FastMulticlassMatrix *cm, 
                                          const uint32_t *actual, 
                                          const uint32_t *pred, 
                                          size_t n) 
{
    uint32_t K = cm->num_classes;
    for (size_t i = 0; i < n; ++i) {
        uint32_t a = actual[i];
        uint32_t p = pred[i];
        if (a < K && p < K) {
            cm->matrix[a][p]++;
            cm->total_samples++;
        }
    }
}

static inline FastMulticlassReport fast_multiclass_evaluate(const FastMulticlassMatrix *cm) {
    FastMulticlassReport rep;
    memset(&rep, 0, sizeof(rep));
    uint32_t K = cm->num_classes;
    rep.num_classes = K;
    rep.total_samples = cm->total_samples;
    
    if (cm->total_samples == 0 || K == 0) return rep;
    
    uint64_t total_correct = 0;
    double macro_p_acc = 0.0;
    double macro_r_acc = 0.0;
    double macro_f1_acc = 0.0;
    double weighted_f1_acc = 0.0;
    
    for (uint32_t k = 0; k < K; ++k) {
        uint64_t tp = cm->matrix[k][k];
        total_correct += tp;
        
        uint64_t row_sum = 0;
        uint64_t col_sum = 0;
        for (uint32_t i = 0; i < K; ++i) {
            row_sum += cm->matrix[k][i];
            col_sum += cm->matrix[i][k];
        }
        rep.class_support[k] = row_sum;
        
        double prec = (col_sum > 0) ? ((double)tp / (double)col_sum) : 0.0;
        double rec  = (row_sum > 0) ? ((double)tp / (double)row_sum) : 0.0;
        double f1   = (prec + rec > METRICS_EPSILON) ? (2.0 * prec * rec / (prec + rec)) : 0.0;
        
        rep.class_precision[k] = prec;
        rep.class_recall[k]    = rec;
        rep.class_f1[k]        = f1;
        
        macro_p_acc += prec;
        macro_r_acc += rec;
        macro_f1_acc += f1;
        weighted_f1_acc += f1 * (double)row_sum;
    }
    
    double total_d = (double)cm->total_samples;
    rep.accuracy = (double)total_correct / total_d;
    rep.micro_f1 = rep.accuracy;
    rep.macro_precision = macro_p_acc / (double)K;
    rep.macro_recall    = macro_r_acc / (double)K;
    rep.macro_f1        = macro_f1_acc / (double)K;
    rep.weighted_f1     = weighted_f1_acc / total_d;
    
    // Розрахунок Gorodkin's MCC
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
        d1 += row_k * (total_d - row_k);
        d2 += col_k * (total_d - col_k);
    }
    
    double den_mcc = sqrt(d1) * sqrt(d2);
    rep.multiclass_mcc = (den_mcc > METRICS_EPSILON) ? (num_mcc / den_mcc) : 0.0;
    
    return rep;
}

// ----------------------------------------------------------------------------
// Мультилейбловий модуль на бітових масках
// ----------------------------------------------------------------------------

static inline void fast_multilabel_init(FastMultilabelAccumulator *acc, uint32_t num_labels) {
    acc->total_samples = 0;
    acc->num_labels = (num_labels > 64) ? 64 : num_labels;
    acc->exact_matches = 0;
    acc->total_bit_errors = 0;
    acc->jaccard_sum = 0.0;
}

static inline void fast_multilabel_update_single(FastMultilabelAccumulator *acc, 
                                                 uint64_t actual_mask, 
                                                 uint64_t pred_mask) 
{
    acc->total_samples++;
    if (actual_mask == pred_mask) {
        acc->exact_matches++;
    }
    
    uint64_t diff = actual_mask ^ pred_mask;
    acc->total_bit_errors += (uint64_t)__builtin_popcountll(diff);
    
    uint64_t inter = actual_mask & pred_mask;
    uint64_t uni   = actual_mask | pred_mask;
    if (uni == 0) {
        acc->jaccard_sum += 1.0;
    } else {
        acc->jaccard_sum += (double)__builtin_popcountll(inter) / (double)__builtin_popcountll(uni);
    }
}

// ----------------------------------------------------------------------------
// Ковзний експоненційний модуль (EMA)
// ----------------------------------------------------------------------------

static inline void fast_ema_init(FastEmaAccumulator *acc, double gamma) {
    acc->gamma = gamma;
    acc->tp_ema = 0.0;
    acc->fp_ema = 0.0;
    acc->fn_ema = 0.0;
    acc->tn_ema = 0.0;
    acc->initialized = false;
}

static inline void fast_ema_update(FastEmaAccumulator *acc, uint8_t actual, uint8_t pred) {
    double s_tp = (actual != 0 && pred != 0) ? 1.0 : 0.0;
    double s_fp = (actual == 0 && pred != 0) ? 1.0 : 0.0;
    double s_fn = (actual != 0 && pred == 0) ? 1.0 : 0.0;
    double s_tn = (actual == 0 && pred == 0) ? 1.0 : 0.0;
    
    if (!acc->initialized) {
        acc->tp_ema = s_tp;
        acc->fp_ema = s_fp;
        acc->fn_ema = s_fn;
        acc->tn_ema = s_tn;
        acc->initialized = true;
    } else {
        double g = acc->gamma;
        acc->tp_ema = g * acc->tp_ema + (1.0 - g) * s_tp;
        acc->fp_ema = g * acc->fp_ema + (1.0 - g) * s_fp;
        acc->fn_ema = g * acc->fn_ema + (1.0 - g) * s_fn;
        acc->tn_ema = g * acc->tn_ema + (1.0 - g) * s_tn;
    }
}

// ----------------------------------------------------------------------------
// Потоковий калібрувальний модуль ECE & Brier Score
// ----------------------------------------------------------------------------

static inline void fast_calibration_init(FastCalibrationAccumulator *acc) {
    acc->total_samples = 0;
    acc->brier_sum = 0.0;
    for (size_t b = 0; b < METRICS_NUM_BINS; ++b) {
        acc->bins[b].count = 0;
        acc->bins[b].sum_conf = 0.0;
        acc->bins[b].sum_actual = 0.0;
    }
}

static inline void fast_calibration_update(FastCalibrationAccumulator *acc, double prob, uint8_t actual) {
    acc->total_samples++;
    double y = (actual != 0) ? 1.0 : 0.0;
    double err = prob - y;
    acc->brier_sum += err * err;
    
    size_t bin_idx = (size_t)(prob * (double)METRICS_NUM_BINS);
    if (bin_idx >= METRICS_NUM_BINS) bin_idx = METRICS_NUM_BINS - 1;
    
    acc->bins[bin_idx].count++;
    acc->bins[bin_idx].sum_conf += prob;
    acc->bins[bin_idx].sum_actual += y;
}

static inline double fast_calibration_get_ece(const FastCalibrationAccumulator *acc) {
    if (acc->total_samples == 0) return 0.0;
    double ece_sum = 0.0;
    double total_d = (double)acc->total_samples;
    
    for (size_t b = 0; b < METRICS_NUM_BINS; ++b) {
        if (acc->bins[b].count > 0) {
            double bin_size = (double)acc->bins[b].count;
            double avg_conf = acc->bins[b].sum_conf / bin_size;
            double avg_acc  = acc->bins[b].sum_actual / bin_size;
            ece_sum += (bin_size / total_d) * fabs(avg_acc - avg_conf);
        }
    }
    return ece_sum;
}

static inline double fast_calibration_get_brier(const FastCalibrationAccumulator *acc) {
    if (acc->total_samples == 0) return 0.0;
    return acc->brier_sum / (double)acc->total_samples;
}

#ifdef __cplusplus
}
#endif

#endif // METRICS_ENGINE_H
