#include "mobius.hpp"
#include <iostream>
#include <vector>
#include <cmath>

void process_star_catalog(std::vector<mobius::Complex>& stars, double beta) {
    double psi = std::atanh(beta);
    mobius::Complex a = std::exp(-psi / 2.0);
    mobius::Complex d = std::exp(psi / 2.0);

    mobius::Transform boost(a, 0.0, 0.0, d);

    for (auto& star_coord : stars) {
        auto new_coord = boost(star_coord);
        if (new_coord) {
            star_coord = *new_coord;
        }
    }
}
