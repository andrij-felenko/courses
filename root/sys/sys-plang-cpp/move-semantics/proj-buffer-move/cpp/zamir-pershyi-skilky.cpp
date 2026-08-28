void demo_vector() {
    std::vector<Buffer> v;
    for (int i = 1; i <= 4; ++i) {
        Stats before = g;
        std::size_t cap = v.capacity();
        v.push_back(Buffer(1u << 20));          // тимчасовий на 1 МіБ
        std::cout << "push_back #" << i << "  cap " << cap << " -> " << v.capacity();
        report("", before);
    }
}
