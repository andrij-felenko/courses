#include <iostream>
#include <vector>
#include <memory>
#include <cmath>

extern "C" {
#include "nauty.h"
}

class NautyWrapper {
public:
    explicit NautyWrapper(int n)
        : n_(n), m_(SETWORDSNEEDED(n)),
          g_(m_ * n_), cg_(m_ * n_),
          lab_(n_), ptn_(n_), orbits_(n_) {
        nauty_check(WORDSIZE, m_, n_, NAUTYVERSION);
        EMPTYGRAPH(g_.data(), m_, n_);
    }

    void add_edge(int u, int v) {
        ADDONEEDGE(g_.data(), u, v, m_);
    }

    struct Result {
        double aut_group_size;
        int num_orbits;
        std::vector<int> canonical_labeling;
    };

    Result compute_canonical_form() {
        optionblk options;
        statsblk stats;
        DEFAULTOPTIONS_GRAPH(&options);
        options.getcanon = TRUE;

        std::vector<set> workspace(16 * m_);

        nauty(g_.data(), lab_.data(), ptn_.data(), nullptr,
              orbits_.data(), &options, &stats,
              workspace.data(), static_cast<int>(workspace.size()),
              m_, n_, cg_.data());

        return Result{
            stats.grpsize1 * std::pow(10.0, stats.grpsize2),
            stats.numorbits,
            lab_
        };
    }

private:
    int n_;
    int m_;
    std::vector<graph> g_;
    std::vector<graph> cg_;
    std::vector<int> lab_;
    std::vector<int> ptn_;
    std::vector<int> orbits_;
};

int main() {
    NautyWrapper g(5);
    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 4);
    g.add_edge(4, 0);

    auto res = g.compute_canonical_form();
    std::cout << "Розмір Aut(G): " << res.aut_group_size << "\n";
    std::cout << "Орбіти: " << res.num_orbits << "\n";
    std::cout << "Канонічний порядок: ";
    for (int v : res.canonical_labeling) {
        std::cout << v << " ";
    }
    std::cout << "\n";
    return 0;
}
