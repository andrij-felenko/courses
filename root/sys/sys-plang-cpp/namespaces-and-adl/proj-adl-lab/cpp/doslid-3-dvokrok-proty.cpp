namespace img {

inline int moveCount = 0;
inline int swapCount = 0;

class Buffer {
public:
    Buffer(std::string tag, std::size_t n)
        : tag_(std::move(tag)), data_(new int[n]), size_(n) {}
    ~Buffer() { delete[] data_; }

    Buffer(const Buffer&)            = delete;
    Buffer& operator=(const Buffer&) = delete;

    Buffer(Buffer&& o) noexcept
        : tag_(std::move(o.tag_)), data_(o.data_), size_(o.size_) {
        o.data_ = nullptr; o.size_ = 0; ++moveCount;
    }
    Buffer& operator=(Buffer&& o) noexcept {
        if (this == &o) return *this;
        delete[] data_;
        tag_ = std::move(o.tag_); data_ = o.data_; size_ = o.size_;
        o.data_ = nullptr; o.size_ = 0; ++moveCount;
        return *this;
    }

    friend void swap(Buffer& a, Buffer& b) noexcept {      // прихований друг
        std::swap(a.tag_,  b.tag_);
        std::swap(a.data_, b.data_);
        std::swap(a.size_, b.size_);
        ++swapCount;
    }

    const std::string& tag() const { return tag_; }

private:
    std::string tag_;
    int*        data_ = nullptr;
    std::size_t size_ = 0;
};

}  // namespace img

template <class T> void twoStep  (T& a, T& b) { using std::swap; swap(a, b); }
template <class T> void qualified(T& a, T& b) { std::swap(a, b); }
template <class T> void viaCpo   (T& a, T& b) { std::ranges::swap(a, b); }

void report(std::string_view what, int m0, int s0) {
    std::cout << "    " << what << "  →  переміщень Buffer: " << img::moveCount - m0
              << ",  власний swap: " << img::swapCount - s0 << '\n';
}

void part_swap() {
    head("3. Двокрок проти кваліфікованого виклику");

    img::Buffer a("кадр-A", 1024), b("кадр-B", 1024);
    int m, s;

    m = img::moveCount; s = img::swapCount;
    twoStep(a, b);    report("using std::swap; swap(a, b)", m, s);

    m = img::moveCount; s = img::swapCount;
    qualified(a, b);  report("std::swap(a, b)            ", m, s);

    m = img::moveCount; s = img::swapCount;
    viaCpo(a, b);     report("std::ranges::swap(a, b)    ", m, s);

    std::cout << "    у a лежить «" << a.tag() << "», у b — «" << b.tag() << "»\n";
}
