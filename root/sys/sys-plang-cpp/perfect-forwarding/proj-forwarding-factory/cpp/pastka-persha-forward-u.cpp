class Receiver {
public:
    explicit Receiver(const char* tag) : tag_(tag) {}
    void add(Probe p) { std::printf("      %s отримав: %s\n", tag_, p.text()); }
private:
    const char* tag_;
};

template <class T>
void broadcastBroken(Receiver* rs, std::size_t n, T&& value) {
    for (std::size_t i = 0; i < n; ++i)
        rs[i].add(std::forward<T>(value));          // ← forward на кожній ітерації
}

template <class T>
void broadcastFixed(Receiver* rs, std::size_t n, T&& value) {
    if (n == 0) return;
    for (std::size_t i = 0; i + 1 < n; ++i)
        rs[i].add(value);                           // усім, крім останнього, — копія
    rs[n - 1].add(std::forward<T>(value));          // останньому можна віддати
}

void demoLoop() {
    std::puts("\n=== 4. Пастка: forward у циклі ===");
    Receiver rs[3] = { Receiver{"A"}, Receiver{"B"}, Receiver{"C"} };

    verbose = false;
    Probe named("вітання");
    verbose = true;

    std::puts("\n   зламана версія, аргумент lvalue — усе гаразд:");
    reset(); broadcastBroken(rs, 3, named); numbers();

    std::puts("\n   зламана версія, аргумент rvalue — вміст зникає:");
    reset(); broadcastBroken(rs, 3, Probe("вітання")); numbers();

    std::puts("\n   полагоджена версія, аргумент rvalue:");
    reset(); broadcastFixed(rs, 3, Probe("вітання")); numbers();
}
