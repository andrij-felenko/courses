void take(const Loud& v) { std::cout << "    take(const Loud&)  ← #" << v.id() << '\n'; }
void take(Loud&& v)      { std::cout << "    take(Loud&&)       ← #" << v.id() << '\n'; }

static void part_overloads() {
    head("1. Яке перевантаження виграє");

    Loud       named("іменований");
    const Loud frozen("сталий");

    take(named);                   // змінне lvalue
    take(frozen);                  // const lvalue
    take(Loud("тимчасовий"));      // prvalue
    take(std::move(named));        // xvalue

    std::cout << "    після std::move #" << named.id()
              << " цілий, ім'я «" << named.name() << "»\n";
}
