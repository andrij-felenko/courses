#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>

class CardiacGridCPP {
public:
    struct Params {
        double dt{0.04};
        double dx{0.5};
        double diffConst{1.0};
        double a{0.1};
        double eps{0.01};
        double gamma{0.5};
        double beta{0.0};
    };

    CardiacGridCPP(size_t width, size_t height, Params params = Params{})
        : m_width(width), m_height(height), m_params(params),
          m_v(height * width, 0.0), m_w(height * width, 0.0),
          m_vNext(height * width, 0.0), m_wNext(height * width, 0.0) {}

    void applyS1Stimulus() {
        for (size_t y = 0; y < m_height; ++y) {
            for (size_t x = 0; x < 5; ++x) {
                m_v[idx(x, y)] = 0.9;
            }
        }
    }

    void applyS2Stimulus() {
        for (size_t y = 0; y < m_height / 2; ++y) {
            for (size_t x = 0; x < m_width / 2; ++x) {
                m_v[idx(x, y)] = 0.9;
            }
        }
    }

    void step() {
        applyBoundaryConditions();

        const double idx2 = 1.0 / (m_params.dx * m_params.dx);
        for (size_t y = 1; y < m_height - 1; ++y) {
            for (size_t x = 1; x < m_width - 1; ++x) {
                const size_t i = idx(x, y);
                const double vVal = m_v[i];
                const double wVal = m_w[i];

                const double laplacian = (m_v[idx(x + 1, y)] + m_v[idx(x - 1, y)] +
                                          m_v[idx(x, y + 1)] + m_v[idx(x, y - 1)] -
                                          4.0 * vVal) * idx2;

                const double fV = vVal * (1.0 - vVal) * (vVal - m_params.a) - wVal;
                const double gV = m_params.gamma * vVal - m_params.beta - wVal;

                m_vNext[i] = vVal + m_params.dt * (m_params.diffConst * laplacian + fV);
                m_wNext[i] = wVal + m_params.dt * (m_params.eps * gV);
            }
        }

        std::copy(m_vNext.begin(), m_vNext.end(), m_v.begin());
        std::copy(m_wNext.begin(), m_wNext.end(), m_w.begin());
    }

    [[nodiscard]] double getV(size_t x, size_t y) const { return m_v[idx(x, y)]; }

    [[nodiscard]] size_t countPhaseSingularities() const {
        size_t count = 0;
        for (size_t y = 5; y < m_height - 5; y += 2) {
            for (size_t x = 5; x < m_width - 5; x += 2) {
                const double vVal = m_v[idx(x, y)];
                const double wVal = m_w[idx(x, y)];
                if (std::abs(vVal - 0.2) < 0.05 && std::abs(wVal - 0.05) < 0.02) {
                    ++count;
                }
            }
        }
        return count;
    }

private:
    [[nodiscard]] inline size_t idx(size_t x, size_t y) const noexcept {
        return y * m_width + x;
    }

    void applyBoundaryConditions() {
        for (size_t x = 0; x < m_width; ++x) {
            m_v[idx(x, 0)] = m_v[idx(x, 1)];
            m_v[idx(x, m_height - 1)] = m_v[idx(x, m_height - 2)];
        }
        for (size_t y = 0; y < m_width; ++y) {
            m_v[idx(0, y)] = m_v[idx(1, y)];
            m_v[idx(m_width - 1, y)] = m_v[idx(m_width - 2, y)];
        }
    }

    size_t m_width;
    size_t m_height;
    Params m_params;
    std::vector<double> m_v;
    std::vector<double> m_w;
    std::vector<double> m_vNext;
    std::vector<double> m_wNext;
};

int main() {
    constexpr size_t width = 150;
    constexpr size_t height = 150;

    auto grid = std::make_unique<CardiacGridCPP>(width, height);

    std::cout << "C++20 Симуляція автохвильових спіралей розпочата...\n";
    grid->applyS1Stimulus();

    for (size_t step = 0; step < 1000; ++step) {
        grid->step();

        if (step == 220) {
            std::cout << "Ініціація передчасного стимулу S2 (крок " << step << ")...\n";
            grid->applyS2Stimulus();
        }

        if (step % 200 == 0) {
            std::cout << "Крок " << step
                      << ": V[75][75] = " << grid->getV(75, 75)
                      << ", фазових роторів: " << grid->countPhaseSingularities() << '\n';
        }
    }

    std::cout << "Обчислення завершено успішно.\n";
    return 0;
}
