// Побудова скінченної групи й перевірка Лагранжа.
// Рушій параметризовано шаблоном: тип елемента T + операція Op.
#include <iostream>
#include <vector>
#include <set>

template <class T, class Op>
std::set<T> closure(std::vector<T> gens, Op op) {
    std::set<T> G(gens.begin(), gens.end());
    std::vector<T> frontier = gens;
    while (!frontier.empty()) {
        std::vector<T> fresh;
        std::vector<T> snap(G.begin(), G.end());       // копія: G зростатиме
        for (const T& a : snap)
            for (const T& b : frontier)
                for (const T& x : { op(a, b), op(b, a) })
                    if (G.insert(x).second) fresh.push_back(x);
        frontier = std::move(fresh);
    }
    return G;
}

template <class T, class Op>
int order(T g, Op op, const T& e) {
    T x = g; int m = 1;
    while (x != e) { x = op(x, g); ++m; }
    return m;
}

template <class T, class Op>
std::vector<std::set<T>> left_cosets(const std::set<T>& G,
                                     const std::set<T>& H, Op op) {
    std::set<std::set<T>> seen;
    std::vector<std::set<T>> out;
    for (const T& g : G) {
        std::set<T> c;
        for (const T& h : H) c.insert(op(g, h));         // клас як множина
        if (seen.insert(c).second) out.push_back(c);
    }
    return out;
}

using Perm = std::vector<int>;
Perm pmul(const Perm& g, const Perm& h) {                // g після h
    Perm p(g.size());
    for (int i = 0; i < (int)g.size(); ++i) p[i] = g[h[i]];
    return p;
}

int main() {
    // група 1: D₃ як перестановки
    Perm e3{0,1,2}, r{1,2,0}, s1{0,2,1};
    auto D3 = closure<Perm>({r, s1}, pmul);
    auto H  = closure<Perm>({r}, pmul);
    auto cs = left_cosets(D3, H, pmul);
    std::cout << "D3: |G|=" << D3.size() << "  |H|=" << H.size()
              << "  [G:H]=" << cs.size()
              << "  Lagrange=" << (D3.size() == cs.size() * H.size()) << "\n";

    // група 2: Z₇* — той самий рушій, інша операція
    auto mul7 = [](int a, int b) { return (a * b) % 7; };
    auto Z7 = closure<int>({3}, mul7);
    auto H7 = closure<int>({2}, mul7);
    auto cz = left_cosets(Z7, H7, mul7);
    std::cout << "Z7*: |G|=" << Z7.size() << "  |H|=" << H7.size()
              << "  [G:H]=" << cz.size()
              << "  Lagrange=" << (Z7.size() == cz.size() * H7.size()) << "\n";
}
