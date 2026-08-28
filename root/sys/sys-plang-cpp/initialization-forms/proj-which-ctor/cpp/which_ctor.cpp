// which_ctor.cpp — хто саме викликається за кожної форми запису
// g++ -std=c++17 -Wall -Wextra which_ctor.cpp -o which_ctor
#include <cstdio>
#include <initializer_list>

struct Probe {
    Probe() {
        std::puts("Probe()                       типовий");
    }
    Probe(int n, bool flag) {
        std::printf("Probe(int, bool)              n=%d flag=%s\n",
                    n, flag ? "true" : "false");
    }
    Probe(std::initializer_list<int> xs) {
        std::printf("Probe(initializer_list<int>)  список (%u):", (unsigned)xs.size());
        for (int v : xs) std::printf(" %d", v);
        std::putchar('\n');
    }
    explicit Probe(double v) {
        std::printf("explicit Probe(double)        v=%g\n", v);
    }
    Probe(const Probe&) {
        std::puts("Probe(const Probe&)           копія");
    }
};

// друкує текст рядка й лишає курсор на місці — далі допише сам конструктор
static void form(const char* code) { std::printf("%-24s│ ", code); }

int main() {
    form("Probe a;");              Probe a;
    form("Probe b{};");            Probe b{};
    form("Probe c = {};");         Probe c = {};
    form("Probe d({});");          Probe d({});
    form("Probe e{{}};");          Probe e{{}};
    form("Probe f(1);");           Probe f(1);
    form("Probe g{1};");           Probe g{1};
    form("Probe h(10, true);");    Probe h(10, true);
    form("Probe i{10, true};");    Probe i{10, true};
    form("Probe j = {10, true};"); Probe j = {10, true};
    form("Probe k(2.5);");         Probe k(2.5);
    form("Probe l{1, 2, 3};");     Probe l{1, 2, 3};
    form("Probe m(a);");           Probe m(a);
    form("Probe n = a;");          Probe n = a;
    form("Probe o{a};");           Probe o{a};

    form("Probe w();");            Probe w();
    std::puts("(нічого — це оголошення функції)");
}
