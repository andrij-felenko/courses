// C++: реєстрація — статичний об'єкт, що сам себе вписує в список
struct TestCase { const char *promise; void (*body)(); };

inline std::vector<TestCase> &registry() {
    static std::vector<TestCase> r;   // народжується при першому зверненні
    return r;                         // — а не в невизначену мить старту
}

struct Registrar {
    Registrar(const char *promise, void (*body)()) {
        registry().push_back({promise, body});
    }
};

#define TEST(ident, promise)                          \
    static void ident();                              \
    static const Registrar reg_##ident{promise, ident}; \
    static void ident()

// обстава (англ. fixture — оснастка): свіжий стан у конструкторі,
// прибирання — у деструкторі, і тест про це не думає
struct Ring {
    rb_t rb;
    Ring()  { rb_init(&rb); }
    ~Ring() { /* тут звільняли б файл, сокет, пам'ять */ }
};

TEST(push_on_full_is_rejected, "push у повний буфер відмовляє") {
    Ring f;
    for (int i = 0; i < static_cast<int>(RB_CAP); ++i) rb_push(&f.rb, i);
    CHECK(rb_push(&f.rb, 99) == false);
    CHECK(rb_count(&f.rb) == RB_CAP);
}

// вихід із провалу — виняток: він розкручує стек і кличе ~Ring()
struct CheckFailed { const char *file; int line; std::string what; };

#define CHECK(cond) \
    do { if (!(cond)) throw CheckFailed{__FILE__, __LINE__, #cond}; } while (0)
