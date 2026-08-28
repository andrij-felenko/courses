// Вартовий блока: виконує дію лише тоді, коли з блока виходять розкруткою.
template <class F>
class on_unwind {
public:
    explicit on_unwind(F f) : undo_(std::move(f)), depth_(std::uncaught_exceptions()) {}
    on_unwind(const on_unwind&)            = delete;
    on_unwind& operator=(const on_unwind&) = delete;

    ~on_unwind() {
        if (std::uncaught_exceptions() > depth_) {
            try { undo_(); } catch (...) {}   // з деструктора не кидають
        }
    }
private:
    F   undo_;
    int depth_;
};
template <class F> on_unwind(F) -> on_unwind<F>;   // виведення типу з C++17
