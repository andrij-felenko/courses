#include <iostream>
#include <cassert>
#include <vector>
#include <cmath>

void run_cpp20_comprehensive_tests() {
    std::cout << "====================================================\n";
    std::cout << "[C++20 UNIT TESTS] Запуск верифікації рушія...\n";
    std::cout << "====================================================\n";

    // ТЕСТ 1: Порожній стан
    {
        metrics::FastBinaryAccumulator acc;
        auto rep = acc.evaluate();
        assert(rep.total == 0);
        assert(rep.accuracy == 0.0);
        assert(rep.mcc == 0.0);
        std::cout << "  ✓ [1/8] C++20 Порожній стан: успішно\n";
    }

    // ТЕСТ 2: Ідеальна класифікація
    {
        metrics::FastBinaryAccumulator acc;
        std::vector<uint8_t> act{1, 1, 0, 0, 1, 0};
        std::vector<uint8_t> pred{1, 1, 0, 0, 1, 0};
        acc.update_batch(act, pred);
        auto rep = acc.evaluate();
        assert(rep.tp == 3 && rep.tn == 3);
        assert(std::abs(rep.mcc - 1.0) < 1e-9);
        std::cout << "  ✓ [2/8] C++20 Ідеальна модель: успішно\n";
    }

    // ТЕСТ 3: Повна інверсія
    {
        metrics::FastBinaryAccumulator acc;
        std::vector<uint8_t> act{1, 1, 0, 0};
        std::vector<uint8_t> pred{0, 0, 1, 1};
        acc.update_batch(act, pred);
        auto rep = acc.evaluate();
        assert(std::abs(rep.mcc - (-1.0)) < 1e-9);
        std::cout << "  ✓ [3/8] C++20 Інверсія міток: успішно\n";
    }

    // ТЕСТ 4: Сканування зв'язаних рангів ROC/PR
    {
        std::vector<metrics::MetricSample> samples{
            {0.9, 1}, {0.8, 1}, {0.8, 0}, {0.5, 0}, {0.4, 1}, {0.1, 0}
        };
        auto curves = metrics::compute_curves(samples);
        assert(curves.roc_auc > 0.5 && curves.roc_auc < 1.0);
        std::cout << "  ✓ [4/8] C++20 ROC/PR злиття: успішно (AUC = " << curves.roc_auc << ")\n";
    }

    // ТЕСТ 5: Багатокласовий рушій
    {
        metrics::FastMulticlassEngine engine(3);
        std::vector<uint32_t> act{0, 1, 2, 0, 1, 2};
        std::vector<uint32_t> pred{0, 1, 2, 0, 2, 1};
        engine.update(act, pred);
        auto rep = engine.evaluate();
        assert(rep.accuracy > 0.6);
        std::cout << "  ✓ [5/8] C++20 Multiclass Engine: успішно\n";
    }

    // ТЕСТ 6: Мультилейбловий бітборд
    {
        metrics::FastMultilabelAccumulator ml(4);
        ml.update_single(0b1100, 0b1100);
        ml.update_single(0b1010, 0b1000);
        assert(ml.subset_accuracy() == 0.5);
        std::cout << "  ✓ [6/8] C++20 Multilabel Bitboard: успішно\n";
    }

    // ТЕСТ 7: Ковзний експоненційний накопичувач (EMA)
    {
        metrics::FastEmaAccumulator ema(0.95);
        for (int i = 0; i < 100; ++i) {
            ema.update(1, 1);
        }
        assert(ema.f1_score() > 0.99);
        std::cout << "  ✓ [7/8] C++20 EMA Stream Accumulator: успішно\n";
    }

    // ТЕСТ 8: Калібрування ECE
    {
        metrics::FastCalibrationAccumulator cal;
        cal.update(0.85, 1);
        cal.update(0.15, 0);
        assert(cal.ece() < 0.2);
        std::cout << "  ✓ [8/8] C++20 Calibration Engine: успішно\n";
    }

    std::cout << "====================================================\n";
    std::cout << "[C++20 UNIT TESTS] Усі 8 тестів виконано успішно!\n";
    std::cout << "====================================================\n\n";
}
