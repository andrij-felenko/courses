#include <cstddef>
#include <new>

// Розтяжка: рівно один виняток на прогін, рівно на N-й події.
class Tripwire {
    long long left_  = 0;
    bool      armed_ = false;
public:
    void arm(long long n) { left_ = n; armed_ = true; }
    void disarm()         { armed_ = false; }

    void tick() {
        if (!armed_) return;
        if (--left_ == 0) { armed_ = false; throw std::bad_alloc{}; }
    }
};

inline Tripwire& wire() { static Tripwire w; return w; }
