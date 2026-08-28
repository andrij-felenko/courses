#include <cstdio>

struct Loud { ~Loud() { std::puts("  ~Loud"); } };

Loud make()                     { return Loud{}; }
const Loud& pass(const Loud& x) { return x; }        // ланцюг рветься тут

int main() {
    { std::puts("A:"); const Loud& r = make();       std::puts("  після крапки з комою"); }
    { std::puts("B:"); const Loud& r = pass(make()); std::puts("  після крапки з комою"); }
}
