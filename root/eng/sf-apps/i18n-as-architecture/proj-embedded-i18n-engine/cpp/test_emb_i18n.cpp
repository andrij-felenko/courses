// ============================================================================
// test_emb_i18n.cpp — Повний набір верифікаційних тестів на C++20
// ============================================================================
#include <iostream>
#include <cassert>
#include "emb_i18n.hpp"

using namespace embedded::i18n;

void test_compile_time_hashes() {
    std::cout << "[C++20 TEST] Перевірка consteval хешів...\n";
    
    constexpr uint32_t h1 = const_hash("sensor.temp.alert");
    constexpr uint32_t h2 = const_hash("dialog.btn.cancel");
    
    static_assert(h1 != 0, "Hash must be non-zero");
    static_assert(h1 != h2, "Hashes must be unique");
    assert(h1 == runtime_hash("sensor.temp.alert"));
}

void test_static_buffer() {
    std::cout << "[C++20 TEST] Перевірка StaticBuffer без купи...\n";
    
    StaticBuffer<64> buffer;
    buffer.format_1i("Оновлено {0} записів", 15);
    assert(buffer.view() == "Оновлено 15 записів");
    assert(std::strlen(buffer.c_str()) == 26);
}

void test_plural_rules() {
    std::cout << "[C++20 TEST] Перевірка правил плюралізації C++20...\n";
    
    assert(Engine::evaluate_plural(2, 1)  == PluralCategory::One);
    assert(Engine::evaluate_plural(2, 2)  == PluralCategory::Few);
    assert(Engine::evaluate_plural(2, 5)  == PluralCategory::Many);
    assert(Engine::evaluate_plural(2, 21) == PluralCategory::One);
    assert(Engine::evaluate_plural(2, 22) == PluralCategory::Few);
}

int main() {
    test_compile_time_hashes();
    test_static_buffer();
    test_plural_rules();
    std::cout << "[C++20 TEST] Усі тести на C++20 завершено успішно!\n";
    return 0;
}
