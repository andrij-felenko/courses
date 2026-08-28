#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <map>
#include <new>
#include <string>
#include <vector>

struct Counters {
    std::size_t ctor = 0, copy = 0, move = 0, dtor = 0;
    void reset() { ctor = copy = move = dtor = 0; }
};
inline Counters g_probe;

// Лічильник справжніх виділень: заміна глобального operator new.
inline std::size_t g_allocs = 0;

void* operator new(std::size_t n) {
    ++g_allocs;
    if (void* p = std::malloc(n)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept              { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

struct Probe {
    std::string id;                       // навмисно довгий рядок — див. «Пастки»

    explicit Probe(std::string s) : id(std::move(s))   { ++g_probe.ctor; }
    Probe(const Probe& o)         : id(o.id)           { ++g_probe.copy; }
    Probe(Probe&& o) noexcept     : id(std::move(o.id)) { ++g_probe.move; }

    Probe& operator=(const Probe& o) { id = o.id;            ++g_probe.copy; return *this; }
    Probe& operator=(Probe&& o) noexcept { id = std::move(o.id); ++g_probe.move; return *this; }

    ~Probe() { ++g_probe.dtor; }
};
