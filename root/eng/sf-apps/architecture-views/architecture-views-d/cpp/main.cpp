#include <array>
#include <iostream>

enum Kind { DEPENDS, CALLS, DEPLOYED };            // рід зв'язку = вимір в'ю

struct Edge {
    const char *from;
    const char *to;
    Kind kind;
};

// Одна модель — усі факти про систему разом, без поділу на діаграми.
static const std::array<Edge, 5> MODEL = {{
    { "orders",  "prices",  DEPENDS  },   // orders статично залежить від prices
    { "orders",  "prices",  CALLS    },   // і в часі його викликає
    { "orders",  "node-eu", DEPLOYED },   // а розгорнутий orders на вузлі EU
    { "prices",  "node-us", DEPLOYED },   // prices — на іншому вузлі, US!
    { "prices",  "cache",   DEPENDS  },
}};

// «Намалювати в'ю» = профільтрувати одну модель за родом зв'язку.
void render_view(const char *name, Kind k) {
    std::cout << "В'ю: " << name << '\n';
    for (const Edge &e : MODEL)
        if (e.kind == k)
            std::printf("  %-8s -> %-8s\n", e.from, e.to);
}

int main() {
    render_view("логічний (залежності)", DEPENDS);
    render_view("процесний (виклики)",   CALLS);
    render_view("розгортання (вузли)",   DEPLOYED);
    return 0;
}
