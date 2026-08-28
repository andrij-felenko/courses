#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

// Моном x^a * y^b
struct Monomial {
    int a{0}; // степінь x
    int b{0}; // степінь y

    int total_deg() const { return a + b; }

    // Graded reverse lexicographic (grevlex) order
    bool operator<(const Monomial& o) const {
        if (total_deg() != o.total_deg()) return total_deg() < o.total_deg();
        if (b != o.b) return b > o.b; // у grevlex менший степінь y виграє
        return a < o.a;
    }
    bool operator==(const Monomial& o) const { return a == o.a && b == o.b; }
};

Monomial lcm(const Monomial& m1, const Monomial& m2) {
    return {std::max(m1.a, m2.a), std::max(m1.b, m2.b)};
}

bool divides(const Monomial& div, const Monomial& target) {
    return div.a <= target.a && div.b <= target.b;
}

struct Term {
    Rational coeff;
    Monomial monom;
};

class Poly2D {
public:
    std::vector<Term> terms;

    void cleanup() {
        std::vector<Term> clean;
        for (const auto& t : terms) {
            if (!t.coeff.is_zero()) clean.push_back(t);
        }
        std::sort(clean.begin(), clean.end(), [](const Term& t1, const Term& t2) {
            return t2.monom < t1.monom; // за спаданням порядку
        });
        terms.clear();
        for (const auto& t : clean) {
            if (!terms.empty() && terms.back().monom == t.monom) {
                terms.back().coeff = terms.back().coeff + t.coeff;
                if (terms.back().coeff.is_zero()) terms.pop_back();
            } else {
                terms.push_back(t);
            }
        }
    }

    bool is_zero() const { return terms.empty(); }
    Term lt() const { return terms.empty() ? Term{Rational(0), {0, 0}} : terms[0]; }
};

// Редукція f відносно набору g_list
Poly2D reduce_poly(Poly2D f, const std::vector<Poly2D>& g_list) {
    f.cleanup();
    Poly2D rem;
    while (!f.is_zero()) {
        bool reduced = false;
        Term lt_f = f.lt();
        for (const auto& g : g_list) {
            Term lt_g = g.lt();
            if (divides(lt_g.monom, lt_f.monom)) {
                Rational factor = lt_f.coeff / lt_g.coeff;
                Monomial shift = {lt_f.monom.a - lt_g.monom.a, lt_f.monom.b - lt_g.monom.b};
                // Віднімаємо factor * shift * g
                for (const auto& gt : g.terms) {
                    f.terms.push_back({Rational(0) - (factor * gt.coeff),
                                      {gt.monom.a + shift.a, gt.monom.b + shift.b}});
                }
                f.cleanup();
                reduced = true;
                break;
            }
        }
        if (!reduced) {
            rem.terms.push_back(lt_f);
            f.terms.erase(f.terms.begin());
        }
    }
    rem.cleanup();
    return rem;
}

// Побудова S-многочлена для пари g1, g2
Poly2D s_polynomial(const Poly2D& g1, const Poly2D& g2) {
    Term lt1 = g1.lt();
    Term lt2 = g2.lt();
    Monomial L = lcm(lt1.monom, lt2.monom);

    Poly2D s;
    Monomial s1 = {L.a - lt1.monom.a, L.b - lt1.monom.b};
    Monomial s2 = {L.a - lt2.monom.a, L.b - lt2.monom.b};
    Rational c1 = Rational(1) / lt1.coeff;
    Rational c2 = Rational(1) / lt2.coeff;

    for (const auto& t : g1.terms) s.terms.push_back({t.coeff * c1, {t.monom.a + s1.a, t.monom.b + s1.b}});
    for (const auto& t : g2.terms) s.terms.push_back({Rational(0) - (t.coeff * c2), {t.monom.a + s2.a, t.monom.b + s2.b}});
    s.cleanup();
    return s;
}

// Алгоритм Бухбергера
std::vector<Poly2D> buchberger(std::vector<Poly2D> G) {
    for (auto& g : G) g.cleanup();
    std::vector<std::pair<size_t, size_t>> pairs;
    for (size_t i = 0; i < G.size(); ++i) {
        for (size_t j = i + 1; j < G.size(); ++j) pairs.emplace_back(i, j);
    }

    while (!pairs.empty()) {
        auto [i, j] = pairs.back();
        pairs.pop_back();

        Poly2D S = s_polynomial(G[i], G[j]);
        Poly2D rem = reduce_poly(S, G);

        if (!rem.is_zero()) {
            size_t new_idx = G.size();
            for (size_t k = 0; k < G.size(); ++k) pairs.emplace_back(k, new_idx);
            G.push_back(rem);
        }
    }
    return G;
}
