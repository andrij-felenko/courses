// stage_timer.h — один вимірюваний шматок конвеєра.
// Монотонний годинник + кільцевий буфер останніх N часів.
#pragma once
#include <chrono>
#include <vector>
#include <algorithm>
#include <cstddef>

using clk = std::chrono::steady_clock;   // НІКОЛИ не стрибне назад

// Зведена статистика за вікном останніх вимірів (усе в мілісекундах).
struct Stats {
    double mean, p50, p95, p99, max;
    size_t count;
};

class StageTimer {
public:
    explicit StageTimer(size_t window = 512)
        : buf_(window, 0.0), cap_(window) {}

    // Обхопити шматок роботи: t0 — зараз, t1 — у stop().
    void start() { t0_ = clk::now(); }

    // Закрити вимір: рахуємо мс і кладемо в кільце.
    double stop() {
        double ms = std::chrono::duration<double, std::milli>(
                        clk::now() - t0_).count();
        buf_[head_] = ms;                 // пишемо в поточну комірку
        head_ = (head_ + 1) % cap_;       // вказівник по колу
        if (filled_ < cap_) ++filled_;    // поки буфер не повний — росте
        return ms;
    }

    // Зняти статистику за вікном. НЕ чіпає буфер: копіює й сортує копію.
    Stats snapshot() const {
        Stats s{};
        s.count = filled_;
        if (filled_ == 0) return s;

        std::vector<double> tmp(buf_.begin(), buf_.begin() + filled_);
        std::sort(tmp.begin(), tmp.end());

        double sum = 0;
        for (double v : tmp) sum += v;
        s.mean = sum / filled_;
        s.p50  = tmp[pct_index(50)];
        s.p95  = tmp[pct_index(95)];
        s.p99  = tmp[pct_index(99)];
        s.max  = tmp.back();
        return s;
    }

private:
    // Індекс перцентиля у відсортованому масиві довжини filled_.
    size_t pct_index(int p) const {
        // (p/100)*(n-1), округлене вниз — без виходу за межі.
        size_t idx = (size_t)((double)p / 100.0 * (filled_ - 1));
        return idx;
    }

    std::vector<double> buf_;   // кільце фіксованого розміру
    size_t cap_;                // місткість вікна
    size_t head_  = 0;          // куди писати наступний час
    size_t filled_ = 0;         // скільки реально заповнено (до cap_)
    clk::time_point t0_;
};
