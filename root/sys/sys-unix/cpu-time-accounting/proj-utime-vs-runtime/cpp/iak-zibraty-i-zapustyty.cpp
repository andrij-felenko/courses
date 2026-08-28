int main(int argc, char** argv)
{
    std::string_view mode = argc > 1 ? argv[1] : "mix";
    auto parse_double = [](const char* str) {
        try { return std::stod(str); } catch (...) { return 0.0; }
    };

    double a2 = argc > 2 ? parse_double(argv[2]) : 0.0;
    double a3 = argc > 3 ? parse_double(argv[3]) : 0.0;
    double a4 = argc > 4 ? parse_double(argv[4]) : 0.0;

    std::cout << std::unitbuf;

    if (mode == "mix")
        return mode_mix(a2 > 0 ? a2 : 3.0, argc > 3 ? a3 : 0.35,
                        (a4 > 0 ? a4 : 1.0) / 1000.0);
    if (mode == "spread")
        return mode_spread(argc > 2 ? static_cast<int>(a2) : 8, a3 > 0 ? a3 : 1.0,
                            argc > 4 ? a4 : 0.35, 0.001);
    if (mode == "short")
        return mode_short(a2 > 0 ? a2 : 3.0);
    if (mode == "phase")
        return mode_phase(a2 > 0 ? a2 : 1.0, argc > 3 ? a3 : 0.35);
    if (mode == "threads")
        return mode_threads(argc > 2 ? static_cast<int>(a2) : 4, a3 > 0 ? a3 : 1.0,
                            argc > 4 ? a4 : 0.35);

    std::cerr << "usage: cpulab mix     [с] [частка] [скибка_мс]\n"
              << "              spread  [прогонів] [с] [частка]\n"
              << "              short   [мс]\n"
              << "              phase   [с] [частка]\n"
              << "              threads [потоків] [с] [частка]\n";
    return 2;
}
