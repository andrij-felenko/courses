// lab.cpp — g++ -std=c++20 lab.cpp   |   clang++ -std=c++20 lab.cpp
#include <cstdio>

// Мітки: за типом результату впізнаємо переможця.
struct AsInt    { static constexpr const char* who = "f(int)";    };
struct AsDouble { static constexpr const char* who = "f(double)"; };
struct AsBool   { static constexpr const char* who = "f(bool)";   };
struct AsMeters { static constexpr const char* who = "f(Meters)"; };
struct AsAny    { static constexpr const char* who = "f(...)";    };

struct Meters { double v; };
struct Feet   { double v; operator Meters() const { return { v * 0.3048 }; } };
struct Blob   { };                    // ні в що не перетворюється

AsInt    f(int)    { return {}; }
AsDouble f(double) { return {}; }
AsBool   f(bool)   { return {}; }
AsMeters f(Meters) { return {}; }
AsAny    f(...)    { return {}; }

#define SHOW(expr) std::printf("%-14s → %s\n", #expr, (expr).who)

int main() {
    short s = 7;
    float x = 1.5f;
    const char* text = "мс";

    SHOW( f(42)        );   // точний збіг
    SHOW( f(s)         );   // підвищення   short → int
    SHOW( f(x)         );   // підвищення   float → double
    SHOW( f('a')       );   // підвищення   char  → int
    SHOW( f(text)      );   // перетворення const char* → bool
    SHOW( f(Feet{1.0}) );   // користувацьке перетворення
    SHOW( f(Blob{})    );   // нікуди більше — багатокрапка
}
