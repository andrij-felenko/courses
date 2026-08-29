#pragma once

#include <cstddef>
#include <span>
#include <vector>

namespace stats {

struct Table {
    int a{};  // фактор є + відмова
    int b{};  // фактор є + справна
    int c{};  // фактора немає + відмова
    int d{};  // фактора немає + справна
};

struct Effect {
    double odds_ratio{};
    double ci_low{};
    double ci_high{};
    bool haldane{false};   // довелося додати 0.5 до кожної клітинки
};

struct Stratified {
    double odds_ratio{};   // inf, коли в жодній страті немає b*c
    double chi2{};
    double p_value{};
    std::size_t strata{};
};

double log_factorial(int n);
double fisher_exact(const Table& t);          // двосторонній точний тест
Effect effect_size(const Table& t);
double chi2_tail_1df(double chi2);

// Поправка Беньяміні — Хохберга на множинність перевірок.
std::vector<double> benjamini_hochberg(std::span<const double> p);

// Стратифікований аналіз Мантеля — Гензеля.
Stratified mantel_haenszel(std::span<const Table> strata);

}  // namespace stats
