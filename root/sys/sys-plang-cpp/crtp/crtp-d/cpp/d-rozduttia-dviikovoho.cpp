// Загальна частина, що не залежить від шаблону (один примірник у бінарнику)
class NonTemplateBase {
protected:
    void log_internal(const char* msg);
    void allocate_buffer(size_t sz);
};

// CRTP-шаблон містить лише тонкі виклики з static_cast
template <typename Derived>
class CRTPBase : private NonTemplateBase {
public:
    void process() {
        log_internal("Starting process");
        static_cast<Derived*>(this)->process_impl();
    }
};
