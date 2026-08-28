#include <random>

// Адаптивна обгортка для підключення C++ URBG до TestU01
template<typename Engine>
struct TestU01Adapter {
    static Engine engine;

    static unsigned long get_bits() {
        return static_cast<unsigned long>(engine());
    }
};

template<typename Engine>
Engine TestU01Adapter<Engine>::engine(42);
