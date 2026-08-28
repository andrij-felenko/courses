// growth.cpp
//   g++  -std=c++17 -O2 growth.cpp -o growth
//   cl   /std:c++17 /O2 /EHsc growth.cpp
#include <chrono>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <type_traits>
#include <utility>
#include <vector>

// ── Лічильники: кожна операція типу лишає слід ─────────────────────────────
struct Counters {
    long ctor = 0;   // побудова з параметра
    long copy = 0;   // конструктор копіювання
    long move = 0;   // конструктор переміщення
    long dtor = 0;
    void reset() { ctor = copy = move = dtor = 0; }
};

inline Counters g;   // C++17: inline-змінна, одна на всю програму

// ── Тип під вимір. NX — єдина відмінність між двома варіантами ─────────────
template <bool NX>
class Payload {
public:
    explicit Payload(std::size_t n) : data_(n, 1.0) { ++g.ctor; }

    Payload(const Payload& o) : data_(o.data_)                { ++g.copy; }
    Payload(Payload&& o) noexcept(NX) : data_(std::move(o.data_)) { ++g.move; }

    Payload& operator=(const Payload& o) {
        if (this != &o) { data_ = o.data_; ++g.copy; }
        return *this;
    }
    Payload& operator=(Payload&& o) noexcept(NX) {
        if (this != &o) { data_ = std::move(o.data_); ++g.move; }
        return *this;
    }
    ~Payload() { ++g.dtor; }

    double head() const { return data_.empty() ? 0.0 : data_[0]; }

private:
    std::vector<double> data_;
};

static_assert( std::is_nothrow_move_constructible_v<Payload<true>>);
static_assert(!std::is_nothrow_move_constructible_v<Payload<false>>);
