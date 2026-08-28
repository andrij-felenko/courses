/* Модульні тести для перевірки коректності математичного ядра */
void run_unit_tests_c(void) {
    printf("[ТЕСТ 1] Ідеальний детектор (Perfect Detection)... ");
    {
        GroundTruth gts[2] = {
            {{10.0f, 10.0f, 50.0f, 50.0f}, 0, 1, 1600.0f, false, false},
            {{100.0f, 100.0f, 200.0f, 200.0f}, 0, 1, 10000.0f, false, false}
        };
        Detection dets[2] = {
            {{10.0f, 10.0f, 50.0f, 50.0f}, 0.99f, 0, 1},
            {{100.0f, 100.0f, 200.0f, 200.0f}, 0.95f, 0, 1}
        };
        EvaluationSummary s = run_full_evaluation_c(dets, 2, gts, 2, 1);
        if (fabsf(s.map_coco - 1.0f) < 1e-4f && fabsf(s.map_50 - 1.0f) < 1e-4f) {
            printf("ПРОЙДЕНО (mAP = %.4f)\n", s.map_coco);
        } else {
            printf("ПОМИЛКА! Отримано mAP = %.4f\n", s.map_coco);
        }
    }

    printf("[ТЕСТ 2] Дублювання детекцій (Duplicate Penalty)... ");
    {
        GroundTruth gts[1] = {
            {{50.0f, 50.0f, 100.0f, 100.0f}, 0, 1, 2500.0f, false, false}
        };
        Detection dets[2] = {
            {{50.0f, 50.0f, 100.0f, 100.0f}, 0.90f, 0, 1},
            {{52.0f, 52.0f, 98.0f, 98.0f}, 0.85f, 0, 1}
        };
        /* 1 TP і 1 FP -> Precision = 0.5 при Recall = 1.0 */
        EvaluationSummary s = run_full_evaluation_c(dets, 2, gts, 1, 1);
        if (fabsf(s.map_50 - 1.0f) < 1e-4f) {
            printf("ПРОЙДЕНО (Дублікат покарано як FP, AP_50 = %.4f)\n", s.map_50);
        } else {
            printf("ПОМИЛКА! AP_50 = %.4f\n", s.map_50);
        }
    }

    printf("[ТЕСТ 3] Масштабна фільтрація (AP_small vs AP_large)... ");
    {
        GroundTruth gts[2] = {
            {{10.0f, 10.0f, 30.0f, 30.0f}, 0, 1, 400.0f, false, false},   /* Small (400 px^2) */
            {{100.0f, 100.0f, 300.0f, 300.0f}, 0, 1, 40000.0f, false, false} /* Large (40000 px^2) */
        };
        Detection dets[1] = {
            {{10.0f, 10.0f, 30.0f, 30.0f}, 0.95f, 0, 1} /* Виявлено лише малий */
        };
        EvaluationSummary s = run_full_evaluation_c(dets, 1, gts, 2, 1);
        if (fabsf(s.classes[0].ap_small - 1.0f) < 1e-4f && fabsf(s.classes[0].ap_large - 0.0f) < 1e-4f) {
            printf("ПРОЙДЕНО (AP_small = %.2f, AP_large = %.2f)\n", s.classes[0].ap_small, s.classes[0].ap_large);
        } else {
            printf("ПОМИЛКА! AP_s = %.2f, AP_l = %.2f\n", s.classes[0].ap_small, s.classes[0].ap_large);
        }
    }
}
