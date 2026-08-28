/* ============================================================================
 * Файл: test_temp_scaler.c
 * Опис: Набір верифікаційних юніт-тестів для перевірки калібратора (C99)
 * ============================================================================ */
#include "temp_scaler.h"
#include <stdio.h>
#include <assert.h>
#include <math.h>

static void test_invariant_t1(void) {
    const float logits[] = {2.0f, 1.0f, 0.1f};
    float probs[3];
    ts_status_t status = ts_calibrate_logits(logits, 3, 1.0f, probs);
    assert(status == TS_SUCCESS);

    float sum = probs[0] + probs[1] + probs[2];
    assert(fabsf(sum - 1.0f) < 1e-5f);
    assert(probs[0] > probs[1] && probs[1] > probs[2]);
    printf("[PASS] Test 1: Invariant T=1.0\n");
}

static void test_numerical_stability(void) {
    /* Екстремальні логіти, які зазвичай переповнюють expf */
    const float extreme_logits[] = {1000.0f, 950.0f, -500.0f};
    float probs[3];
    ts_status_t status = ts_calibrate_logits(extreme_logits, 3, 1.5f, probs);
    assert(status == TS_SUCCESS);
    assert(!isnan(probs[0]) && !isinf(probs[0]));
    assert(!isnan(probs[1]) && !isinf(probs[1]));
    assert(!isnan(probs[2]) && !isinf(probs[2]));
    assert(probs[0] > 0.99f);
    printf("[PASS] Test 2: Extreme logits numerical stability (Log-Sum-Exp)\n");
}

static void test_safety_threshold(void) {
    const float logits[] = {2.5f, 2.0f, 0.5f};
    ts_decision_t decision;

    /* При T=1.0 впевненість висока */
    ts_evaluate_safety(logits, 3, 1.0f, 0.60f, &decision);
    assert(decision.predicted_class == 0);
    assert(decision.is_safe_to_execute == false); // max prob ~0.57 < 0.60

    /* При T=2.5 розподіл стає ще м'якшим */
    ts_evaluate_safety(logits, 3, 2.5f, 0.50f, &decision);
    assert(decision.predicted_class == 0);
    assert(decision.is_safe_to_execute == false);
    printf("[PASS] Test 3: Safety decision threshold\n");
}

static void test_temperature_optimization(void) {
    /* Синтетичний набір надвпевнених зразків */
    const float flat_logits[] = {
        10.0f, 2.0f, 1.0f,  /* зразок 0, мітка 0 (правильно) */
        8.0f,  3.0f, 1.0f,  /* зразок 1, мітка 0 (правильно) */
        1.0f,  9.0f, 2.0f,  /* зразок 2, мітка 0 (помилка моделі!) */
        2.0f,  8.0f, 1.0f   /* зразок 3, мітка 1 (правильно) */
    };
    const size_t labels[] = {0, 0, 0, 1};

    ts_dataset_t dataset = {
        .logits_flat = flat_logits,
        .labels = labels,
        .num_samples = 4,
        .num_classes = 3
    };

    float opt_temp = 0.0f;
    ts_status_t status = ts_optimize_temperature(&dataset, 0.1f, 10.0f, 35, 1e-4f, &opt_temp);
    assert(status == TS_SUCCESS);
    assert(opt_temp > 1.0f); // Оптимізатор повинен охолодити модель (T > 1)

    ts_metrics_t metrics_before, metrics_after;
    ts_compute_metrics(&dataset, 1.0f, 5, &metrics_before);
    ts_compute_metrics(&dataset, opt_temp, 5, &metrics_after);

    assert(metrics_after.nll < metrics_before.nll);
    printf("[PASS] Test 4: Temperature Optimization (T* = %.4f, NLL before: %.4f, NLL after: %.4f)\n", 
           opt_temp, metrics_before.nll, metrics_after.nll);
}

int main(void) {
    printf("=== Запуск тестів калібратора логітів ===\n");
    test_invariant_t1();
    test_numerical_stability();
    test_safety_threshold();
    test_temperature_optimization();
    printf("=== Усі тести пройдено успішно! ===\n");
    return 0;
}
