#include <algorithm>
#include <cmath>
#include <format>
#include <iostream>
#include <memory>
#include <numbers>
#include <string>
#include <vector>

struct Point { double x, y; };

// ── Реалізація: ЯК виводимо (вісь 1) ──────────────────────────
struct Renderer {
    virtual void begin(int w, int h) = 0;
    virtual void polyline(const std::vector<Point>& pts, bool closed) = 0;
    virtual void ellipse(double cx, double cy, double rx, double ry) = 0;
    virtual std::string end() = 0;
    virtual ~Renderer() = default;
};


class SvgRenderer : public Renderer {
    std::vector<std::string> out;
public:
    void begin(int w, int h) override {
        out = {std::format(R"(<svg viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg">)", w, h)};
    }
    void polyline(const std::vector<Point>& pts, bool closed) override {
        std::string d;
        for (std::size_t i = 0; i < pts.size(); ++i)
            d += std::format("{}{:.1f},{:.1f}", i ? " " : "", pts[i].x, pts[i].y);
        out.push_back(std::format(R"(  <{} points="{}" fill="none" stroke="black"/>)",
                                  closed ? "polygon" : "polyline", d));
    }
    void ellipse(double cx, double cy, double rx, double ry) override {
        out.push_back(std::format(
            R"(  <ellipse cx="{:.1f}" cy="{:.1f}" rx="{:.1f}" ry="{:.1f}" fill="none" stroke="black"/>)",
            cx, cy, rx, ry));
    }
    std::string end() override {
        out.push_back("</svg>");
        std::string s;
        for (std::size_t i = 0; i < out.size(); ++i) s += (i ? "\n" : "") + out[i];
        return s;
    }
};


class AsciiRenderer : public Renderer {
    int w = 0, h = 0;
    std::vector<std::string> g;
    void plot(double x, double y) {
        int xi = static_cast<int>(std::lround(x)), yi = static_cast<int>(std::lround(y));
        if (xi >= 0 && xi < w && yi >= 0 && yi < h) g[yi][xi] = '#';
    }
    void segment(Point a, Point b) {
        int steps = std::max({static_cast<int>(std::abs(b.x - a.x)),
                              static_cast<int>(std::abs(b.y - a.y)), 1}) * 2;
        for (int i = 0; i <= steps; ++i) {
            double t = static_cast<double>(i) / steps;
            plot(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t);
        }
    }
public:
    void begin(int w, int h) override {
        this->w = w; this->h = h;
        g.assign(h, std::string(w, ' '));
    }
    void polyline(const std::vector<Point>& pts, bool closed) override {
        std::vector<Point> seq = pts;
        if (closed) seq.push_back(pts[0]);
        for (std::size_t i = 0; i + 1 < seq.size(); ++i) segment(seq[i], seq[i + 1]);
    }
    void ellipse(double cx, double cy, double rx, double ry) override {
        int steps = std::max(8, static_cast<int>(4 * (rx + ry)));
        for (int i = 0; i < steps; ++i) {
            double t = 2 * std::numbers::pi * i / steps;
            plot(cx + rx * std::cos(t), cy + ry * std::sin(t));
        }
    }
    std::string end() override {
        std::string s;
        for (std::size_t r = 0; r < g.size(); ++r) {
            std::string row = g[r];
            row.erase(row.find_last_not_of(' ') + 1);   // rstrip
            s += (r ? "\n" : "") + row;
        }
        return s;
    }
};


class StatsRenderer : public Renderer {
    int n = 0;
    bool has = false;
    double x1 = 0, y1 = 0, x2 = 0, y2 = 0;
    void grow(double x, double y) {
        if (!has) { x1 = x2 = x; y1 = y2 = y; has = true; return; }
        x1 = std::min(x1, x); y1 = std::min(y1, y);
        x2 = std::max(x2, x); y2 = std::max(y2, y);
    }
public:
    void begin(int, int) override { n = 0; has = false; }
    void polyline(const std::vector<Point>& pts, bool) override {
        ++n;
        for (const auto& p : pts) grow(p.x, p.y);
    }
    void ellipse(double cx, double cy, double rx, double ry) override {
        ++n;
        grow(cx - rx, cy - ry);
        grow(cx + rx, cy + ry);
    }
    std::string end() override {
        return std::format("примітивів: {}; рамка: ({:.1f},{:.1f})–({:.1f},{:.1f})",
                           n, x1, y1, x2, y2);
    }
};
