void part_operator() {
    head("1. Оператор, покладений не в той простір");

    lib::Point p{1, 2};
    lib::Pixel q{3, 4};

    {
        using namespace app;                        // діє лише в цих дужках
        ask("std::cout << p");  std::cout << p << '\n';
    }
    ask("std::cout << q");  std::cout << q << '\n';

    util::dump("util::dump(q) — крізь шаблон", q);
    // util::dump("util::dump(p)", p);              // НЕ збирається, див. -DSHOW_ERRORS
}
