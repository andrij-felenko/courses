#include <cmath>
#include <format>
#include <numbers>
#include <string>
#include <utility>
#include <vector>

// НАЇВНО: клас на КОЖНУ пару «фігура × рушій»
class SvgStar {
    double cx, cy, outer, inner;
    int n;
public:
    SvgStar(double cx, double cy, double outer, double inner, int n = 5)
        : cx(cx), cy(cy), outer(outer), inner(inner), n(n) {}
    void draw(std::vector<std::string>& out) const {
        std::string d;
        for (int i = 0; i < n * 2; ++i) {                     // ← математика зірки, копія №1
            double rad = (i % 2 == 0) ? outer : inner;
            double t = std::numbers::pi * i / n - std::numbers::pi / 2;  // −π/2, щоб вістря дивилось угору
            d += std::format("{}{:.1f},{:.1f}", i ? " " : "",
                             cx + rad * std::cos(t), cy + rad * std::sin(t));
        }
        out.push_back(std::format("<polygon points=\"{}\" fill=\"none\" stroke=\"black\"/>", d));
    }
};

class AsciiStar {
    double cx, cy, outer, inner;
    int n;
public:
    AsciiStar(double cx, double cy, double outer, double inner, int n = 5)
        : cx(cx), cy(cy), outer(outer), inner(inner), n(n) {}
    void draw(std::vector<std::string>& grid) const {
        std::vector<std::pair<double, double>> pts;
        for (int i = 0; i < n * 2; ++i) {                     // ← ТА САМА математика, копія №2
            double rad = (i % 2 == 0) ? outer : inner;
            double t = std::numbers::pi * i / n - std::numbers::pi / 2;
            pts.push_back({cx + rad * std::cos(t), cy + rad * std::sin(t)});
        }
        for (std::size_t i = 0; i < pts.size(); ++i)
            plot_segment(grid, pts[i], pts[(i + 1) % pts.size()]);   // plot_segment — спільний помічник
    }
};

// class StatsStar  ← копія №3, з тим самим циклом і тим самим −π/2
