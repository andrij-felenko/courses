#include <chrono>
using namespace std::chrono;

// настінний: system_clock прив'язаний до календаря, його переставляють
auto t0 = system_clock::now();
// ... робота ...                       // NTP крокнув годинник назад
auto d  = system_clock::now() - t0;     // duration може стати від'ємною

// монотонний: steady_clock лише росте
auto m0 = steady_clock::now();
// ... та сама робота ...
auto dm = steady_clock::now() - m0;     // завжди ≥ 0
