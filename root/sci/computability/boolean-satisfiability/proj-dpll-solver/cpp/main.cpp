#include <vector>
#include <map>
#include <optional>
#include <algorithm>
#include <cstdlib>
#include <iostream>

using Clause  = std::vector<int>;          // літерали: +k істинний, −k хибний
using Formula = std::vector<Clause>;
using Model   = std::map<int, bool>;       // змінна → значення

// Призначити lit=істина: викинути вдоволені клаузи, вирізати -lit із решти.
Formula simplify(const Formula& f, int lit) {
    Formula out;
    for (const Clause& cl : f) {
        if (std::find(cl.begin(), cl.end(), lit) != cl.end())
            continue;                              // клауза вже істинна — геть
        Clause reduced;
        for (int x : cl)
            if (x != -lit) reduced.push_back(x);   // -lit хибний — вирізаємо
        out.push_back(std::move(reduced));
    }
    return out;
}

std::optional<int> find_unit(const Formula& f) {
    for (const Clause& cl : f)
        if (cl.size() == 1) return cl[0];
    return std::nullopt;
}

std::optional<int> find_pure(const Formula& f) {
    std::map<int, int> pol;                        // змінна → маска: 1=як +, 2=як −
    for (const Clause& cl : f)
        for (int x : cl)
            pol[std::abs(x)] |= (x > 0 ? 1 : 2);
    for (auto [v, mask] : pol)                     // std::map — ключі за зростанням
        if (mask != 3)                             // не обидві полярності → чистий
            return mask == 1 ? v : -v;
    return std::nullopt;
}

std::optional<Model> dpll(Formula f, Model m) {
    for (const Clause& cl : f)
        if (cl.empty()) return std::nullopt;       // порожня клауза — суперечність
    if (f.empty()) return m;                        // усе вдоволено

    if (auto u = find_unit(f)) {                    // 1. поширення одиничних клауз
        m[std::abs(*u)] = (*u > 0);
        return dpll(simplify(f, *u), std::move(m));
    }
    if (auto p = find_pure(f)) {                    // 2. вилучення чистих літералів
        m[std::abs(*p)] = (*p > 0);
        return dpll(simplify(f, *p), std::move(m));
    }
    int lit = f.front().front();                    // 3. вгадування + повернення
    for (int guess : {lit, -lit}) {
        Model m2 = m;
        m2[std::abs(guess)] = (guess > 0);
        if (auto r = dpll(simplify(f, guess), std::move(m2)))
            return r;
    }
    return std::nullopt;
}

int main() {
    Formula formula = {{1, -2}, {2, 3}, {-1, -3}};  // x₁=1..x₃=3
    if (auto m = dpll(formula, {})) {
        std::cout << "SAT:";
        for (auto [var, val] : *m) std::cout << ' ' << var << '=' << val;
        std::cout << '\n';                          // SAT: 1=1 2=1 3=0
    } else {
        std::cout << "UNSAT\n";
    }
}
