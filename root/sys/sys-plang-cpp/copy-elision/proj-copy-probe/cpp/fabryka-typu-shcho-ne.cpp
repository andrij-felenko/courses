struct Latch {
    Latch()  = default;
    ~Latch() = default;
    Latch(const Latch&) = delete;
    Latch(Latch&&)      = delete;
};

Latch make_latch() { return Latch(); }   // ← ось рядок, що вирішує все

int main() {
    Latch l = make_latch();
    (void)l;
}
