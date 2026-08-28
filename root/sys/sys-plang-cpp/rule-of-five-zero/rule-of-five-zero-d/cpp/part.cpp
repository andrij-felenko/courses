class Buffer {
    char*  data;
    size_t size;
public:
    explicit Buffer(size_t n) : data(new char[n]), size(n) {}
    ~Buffer() { delete[] data; }
};

void demo() {
    Buffer a(4);
    Buffer b = a;      // ← ось тут усе вирішується
}                      // ← ось тут усе падає
