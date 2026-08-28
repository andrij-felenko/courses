// ============================================================================
// Файл: test_temp_scaler.cpp
// Опис: Набір юніт-тестів для C++20 реалізації калібратора
// ============================================================================
#include "temp_scaler.hpp"
#include <iostream>
#include <cassert>

using namespace ml_safety;

void test_cpp_basic() {
    const std::vector<float> logits = {3.0f, 1.0f, 0.2f};
    auto probs = TemperatureScaler::calibrate(logits, 1.0f);
    assert(probs.has_value());
    assert(probs->size() == 3);

    float sum = (*probs)[0] + (*probs)[1] + (*probs)[2];
    assert(std::abs(sum - 1.0f) < 1e-5f);
    std::cout << "[PASS] C++ Test 1: Basic calibrate\n";
}

void test_cpp_safety() {
    const std::vector<float> logits = {4.0f, 1.0f, 0.0f};
    auto dec = TemperatureScaler::evaluate_decision(logits, 2.0f, 0.85f);
    assert(dec.has_value());
    assert(dec->predicted_class == 0);
    std::cout << "[PASS] C++ Test 2: Decision evaluation\n";
}

void test_cpp_optimizer() {
    std::vector<float> l1 = {12.0f, 2.0f};
    std::vector<float> l2 = {1.0f, 11.0f};
    std::vector<float> l3 = {8.0f, 9.0f}; // Помилка з високою впевненістю

    std::vector<DatasetSample> dataset = {
        { .logits = l1, .true_label = 0 },
        { .logits = l2, .true_label = 1 },
        { .logits = l3, .true_label = 0 }
    };

    auto opt_res = TemperatureScaler::optimize_temperature(dataset);
    assert(opt_res.has_value());
    assert(*opt_res > 1.0f);

    auto m_before = TemperatureScaler::compute_metrics(dataset, 1.0f);
    auto m_after = TemperatureScaler::compute_metrics(dataset, *opt_res);
    assert(m_after->nll < m_before->nll);

    std::cout << "[PASS] C++ Test 3: Optimizer (T* = " << *opt_res 
              << ", NLL: " << m_before->nll << " -> " << m_after->nll << ")\n";
}

int main() {
    std::cout << "=== Запуск C++20 тестів калібратора ===\n";
    test_cpp_basic();
    test_cpp_safety();
    test_cpp_optimizer();
    std::cout << "=== Усі C++20 тести успішно виконано! ===\n";
    return 0;
}
