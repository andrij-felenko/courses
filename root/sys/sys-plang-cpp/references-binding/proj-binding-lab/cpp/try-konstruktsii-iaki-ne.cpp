#ifdef SHOW_ERRORS
// Збірка з -DSHOW_ERRORS має провалитися. Дивимося, ЯК саме.

// (1) Змішування передачі за значенням і за посиланням.
void take(Loud v) { std::cout << "    take(Loud)  ← #" << v.id() << '\n'; }

inline void ambiguousCall() {
    Loud named("іменований");
    take(named);
    // error: call of overloaded 'take(Loud&)' is ambiguous
    //   note: candidate: 'void take(const Loud&)'
    //   note: candidate: 'void take(Loud)'
}

// (2) Тимчасовий прямо в списку ініціалізації конструктора.
class DirectKeeper {
public:
    DirectKeeper() : target_(Loud("прямо-в-списку")) {}
private:
    const Loud& target_;
};

// (3) Обгортання тимчасового в std::ref.
inline auto wrapTemporary() { return std::ref(Loud("тимчасовий")); }
// error: use of deleted function 'std::reference_wrapper<T> std::ref(const T&&)'
#endif
