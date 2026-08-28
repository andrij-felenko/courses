#include <chrono>
using namespace std::chrono;

static_assert(steady_clock::is_steady, "потрібен сталий годинник");

auto t0 = steady_clock::now();
// ... робота ...
auto ms = duration_cast<milliseconds>(steady_clock::now() - t0).count();

auto deadline = steady_clock::now() + 30s;      // дедлайн усередині процесу
bool expired  = steady_clock::now() >= deadline;

auto stamp = system_clock::now();               // а це — момент за календарем
