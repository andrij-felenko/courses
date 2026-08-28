void part_hidden() {
    head("4. Прихований друг і множина кандидатів");

    img::Buffer a("а", 8), b("б", 8);
    const int s = img::swapCount;
    swap(a, b);                       // жодного `swap` у видимості — і все одно працює
    std::cout << "    голий swap(a, b) у глобальній області  →  власний swap: "
              << img::swapCount - s << '\n';

    std::vector<lib::Widget> box(2);
    ask("trace(box) // box — std::vector<lib::Widget>");  trace(box);
}
