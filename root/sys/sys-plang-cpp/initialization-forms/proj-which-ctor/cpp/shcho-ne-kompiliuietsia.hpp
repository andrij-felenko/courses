// errors.cpp — по одному спірному рядку на прогін (останній випадок правильний)
// g++ -std=c++17 -DERR=1 -c errors.cpp
#include <initializer_list>
#include <string>
#include <vector>

struct Probe {
    Probe();
    Probe(int, bool);
    Probe(std::initializer_list<int>);
    explicit Probe(double);
    Probe(const Probe&);
};

#if   ERR == 1
Probe p{2.5};                            // списочний обрано → звуження double → int
#elif ERR == 2
Probe p = 2.5;                           // explicit не потрапив у кандидати
#elif ERR == 3
double d = 2.5;
Probe p{d};                              // те саме звуження, але джерело — НЕ константа
#elif ERR == 4
int n = 10;
std::vector<std::string> v{n, "hi"};     // int → size_type, джерело — не константа
#elif ERR == 5
const int n = 10;
std::vector<std::string> v{n, "hi"};     // те саме, але константа — і все чисто
#elif ERR == 6
struct Rect { int w; int h; };
Rect r(3, 4);                            // круглі дужки для агрегату
#endif
