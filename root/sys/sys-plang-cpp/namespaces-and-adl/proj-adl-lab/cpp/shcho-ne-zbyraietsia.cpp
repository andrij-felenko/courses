#ifdef SHOW_ERRORS
// Збірка з -DSHOW_ERRORS має провалитися. Цікаво саме те, ЯК вона провалюється.
inline void broken() {
    lib::Point p{1, 2};
    std::cout << p;                     // (1)
    util::dump("p", p);                 // (2)

    img::Buffer a("а", 8), b("б", 8);
    img::swap(a, b);                    // (3)

    lib::Widget w{7};
    (onlyAdl)(w);                       // (4)
}
using img::swap;                        // (5)
#endif

int main() {
    part_operator();
    app::part_overload();
    part_swap();
    part_hidden();
    part_switches();
}
