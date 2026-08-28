inline std::size_t g_sink = 0;   // щоб цикл не викинули як марний

template <class Body>
void measure(const char* label, Body&& body) {
    g_probe.reset();
    const std::size_t before = g_allocs;
    body();
    const std::size_t allocs = g_allocs - before;
    std::cout << label
              << "  копій: "      << g_probe.copy
              << "\tпереміщень: " << g_probe.move
              << "\tвиділень: "   << allocs << '\n';
}
