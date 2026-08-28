/* Модульні тести для перевірки коректності математичного ядра */
void run_unit_tests_cpp() {
    std::cout << "[ТЕСТ 1] Ідеальний детектор (Perfect Detection)... ";
    {
        std::vector<GroundTruth> gts = {
            {{10.0f, 10.0f, 50.0f, 50.0f}, 0, 1, 1600.0f, false, false},
            {{100.0f, 100.0f, 200.0f, 200.0f}, 0, 1, 10000.0f, false, false}
        };
        std::vector<Detection> dets = {
            {{10.0f, 10.0f, 50.0f, 50.0f}, 0.99f, 0, 1},
            {{100.0f, 100.0f, 200.0f, 200.0f}, 0.95f, 0, 1}
        };
        auto s = run_full_evaluation_cpp(dets, gts, 1);
        if (std::abs(s.map_coco - 1.0f) < 1e-4f && std::abs(s.map_50 - 1.0f) < 1e-4f) {
            std::cout << std::format("ПРОЙДЕНО (mAP = {:.4f})\n", s.map_coco);
        } else {
            std::cout << std::format("ПОМИЛКА! Отримано mAP = {:.4f}\n", s.map_coco);
        }
    }

    std::cout << "[ТЕСТ 2] Дублювання детекцій (Duplicate Penalty)... ";
    {
        std::vector<GroundTruth> gts = {
            {{50.0f, 50.0f, 100.0f, 100.0f}, 0, 1, 2500.0f, false, false}
        };
        std::vector<Detection> dets = {
            {{50.0f, 50.0f, 100.0f, 100.0f}, 0.90f, 0, 1},
            {{52.0f, 52.0f, 98.0f, 98.0f}, 0.85f, 0, 1}
        };
        auto s = run_full_evaluation_cpp(dets, gts, 1);
        if (std::abs(s.map_50 - 1.0f) < 1e-4f) {
            std::cout << std::format("ПРОЙДЕНО (Дублікат покарано як FP, AP_50 = {:.4f})\n", s.map_50);
        } else {
            std::cout << std::format("ПОМИЛКА! AP_50 = {:.4f}\n", s.map_50);
        }
    }

    std::cout << "[ТЕСТ 3] Масштабна фільтрація (AP_small vs AP_large)... ";
    {
        std::vector<GroundTruth> gts = {
            {{10.0f, 10.0f, 30.0f, 30.0f}, 0, 1, 400.0f, false, false},   /* Small (400 px^2) */
            {{100.0f, 100.0f, 300.0f, 300.0f}, 0, 1, 40000.0f, false, false} /* Large (40000 px^2) */
        };
        std::vector<Detection> dets = {
            {{10.0f, 10.0f, 30.0f, 30.0f}, 0.95f, 0, 1} /* Виявлено лише малий */
        };
        auto s = run_full_evaluation_cpp(dets, gts, 1);
        if (std::abs(s.classes[0].ap_small - 1.0f) < 1e-4f && std::abs(s.classes[0].ap_large - 0.0f) < 1e-4f) {
            std::cout << std::format("ПРОЙДЕНО (AP_small = {:.2f}, AP_large = {:.2f})\n", s.classes[0].ap_small, s.classes[0].ap_large);
        } else {
            std::cout << std::format("ПОМИЛКА! AP_s = {:.2f}, AP_l = {:.2f}\n", s.classes[0].ap_small, s.classes[0].ap_large);
        }
    }
}
