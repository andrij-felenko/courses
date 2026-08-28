#include <stdio.h>
#include <assert.h>
#include <math.h>

void run_c99_comprehensive_tests(void) {
    printf("====================================================\n");
    printf("[C99 UNIT TESTS] Запуск верифікації рушія метрик...\n");
    printf("====================================================\n");
    
    // ТЕСТ 1: Порожній стан (нульові вибірки)
    {
        FastBinaryAccumulator acc;
        fast_binary_init(&acc);
        FastBinaryReport rep = fast_binary_evaluate(&acc);
        assert(rep.total == 0);
        assert(rep.accuracy == 0.0);
        assert(rep.precision == 0.0);
        assert(rep.recall == 0.0);
        assert(rep.mcc == 0.0);
        printf("  ✓ [1/8] Порожній накопичувач: успішно (невизначеності оброблено)\n");
    }
    
    // ТЕСТ 2: Ідеальна класифікація
    {
        FastBinaryAccumulator acc;
        fast_binary_init(&acc);
        uint8_t actual[] = {1, 1, 0, 0, 1, 0};
        uint8_t pred[]   = {1, 1, 0, 0, 1, 0};
        fast_binary_update_batch(&acc, actual, pred, 6);
        FastBinaryReport rep = fast_binary_evaluate(&acc);
        assert(rep.tp == 3 && rep.tn == 3 && rep.fp == 0 && rep.fn == 0);
        assert(fabs(rep.accuracy - 1.0) < 1e-9);
        assert(fabs(rep.f1_score - 1.0) < 1e-9);
        assert(fabs(rep.mcc - 1.0) < 1e-9);
        assert(fabs(rep.cohen_kappa - 1.0) < 1e-9);
        printf("  ✓ [2/8] Ідеальна бінарна модель: успішно (MCC = +1.0)\n");
    }
    
    // ТЕСТ 3: Повна інверсія передбачень
    {
        FastBinaryAccumulator acc;
        fast_binary_init(&acc);
        uint8_t actual[] = {1, 1, 0, 0};
        uint8_t pred[]   = {0, 0, 1, 1};
        fast_binary_update_batch(&acc, actual, pred, 4);
        FastBinaryReport rep = fast_binary_evaluate(&acc);
        assert(rep.accuracy == 0.0);
        assert(rep.tp == 0 && rep.tn == 0);
        assert(fabs(rep.mcc - (-1.0)) < 1e-9);
        printf("  ✓ [3/8] Повна інверсія міток: успішно (MCC = -1.0)\n");
    }
    
    // ТЕСТ 4: Константний нульовий класифікатор (усі 0)
    {
        FastBinaryAccumulator acc;
        fast_binary_init(&acc);
        uint8_t actual[] = {1, 0, 1, 0};
        uint8_t pred[]   = {0, 0, 0, 0};
        fast_binary_update_batch(&acc, actual, pred, 4);
        FastBinaryReport rep = fast_binary_evaluate(&acc);
        assert(rep.accuracy == 0.5);
        assert(rep.precision == 0.0); // Захист від ділення 0/0
        assert(rep.recall == 0.0);
        assert(rep.mcc == 0.0);
        printf("  ✓ [4/8] Константний нульовий прогноз: успішно (ділення на нуль відсутнє)\n");
    }
    
    // ТЕСТ 5: Обчислення ROC-AUC зі зв'язаними оцінками
    {
        MetricSample samples[6] = {
            {0.9, 1},
            {0.8, 1},
            {0.8, 0}, // Зв'язаний ранг зі скором 0.8
            {0.5, 0},
            {0.4, 1},
            {0.1, 0}
        };
        double roc_auc = 0.0, pr_auc = 0.0;
        fast_compute_curves_auc(samples, 6, &roc_auc, &pr_auc);
        assert(roc_auc > 0.5 && roc_auc < 1.0);
        assert(pr_auc > 0.0 && pr_auc < 1.0);
        printf("  ✓ [5/8] Порове сканування ROC/PR із ties: успішно (ROC-AUC = %.4f)\n", roc_auc);
    }
    
    // ТЕСТ 6: Багатокласова матриця 3x3 та MCC Городкіна
    {
        FastMulticlassMatrix cm;
        fast_multiclass_init(&cm, 3);
        uint32_t act[]  = {0, 1, 2, 0, 1, 2, 0, 1, 2};
        uint32_t pred[] = {0, 1, 2, 0, 2, 1, 0, 1, 2};
        fast_multiclass_update(&cm, act, pred, 9);
        FastMulticlassReport rep = fast_multiclass_evaluate(&cm);
        assert(rep.total_samples == 9);
        assert(rep.accuracy > 0.7);
        assert(rep.multiclass_mcc > 0.5);
        printf("  ✓ [6/8] Багатокласова OvR та Gorodkin MCC: успішно (MCC = %.4f)\n", rep.multiclass_mcc);
    }
    
    // ТЕСТ 7: Мультилейбловий накопичувач на бітових масках
    {
        FastMultilabelAccumulator ml_acc;
        fast_multilabel_init(&ml_acc, 4);
        fast_multilabel_update_single(&ml_acc, 0b1011, 0b1011); // Точний збіг
        fast_multilabel_update_single(&ml_acc, 0b1100, 0b1000); // 1 бітова помилка
        assert(ml_acc.total_samples == 2);
        assert(ml_acc.exact_matches == 1);
        printf("  ✓ [7/8] Мультилейблові бітові маски POPCNT: успішно (Exact = 50%%)\n");
    }
    
    // ТЕСТ 8: Калібрувальний накопичувач ECE
    {
        FastCalibrationAccumulator cal;
        fast_calibration_init(&cal);
        fast_calibration_update(&cal, 0.9, 1);
        fast_calibration_update(&cal, 0.9, 1);
        fast_calibration_update(&cal, 0.1, 0);
        fast_calibration_update(&cal, 0.1, 0);
        double ece = fast_calibration_get_ece(&cal);
        double brier = fast_calibration_get_brier(&cal);
        assert(ece < 0.2);
        assert(brier < 0.1);
        printf("  ✓ [8/8] Потоковий ECE та Brier Score: успішно (ECE = %.4f)\n", ece);
    }
    
    printf("====================================================\n");
    printf("[C99 UNIT TESTS] Усі 8 тестів виконано бездоганно!\n");
    printf("====================================================\n\n");
}
