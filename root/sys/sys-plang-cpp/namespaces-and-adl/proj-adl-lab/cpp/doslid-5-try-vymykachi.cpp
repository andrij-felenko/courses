namespace guard {
inline constexpr struct TraceFn {
    void operator()(const lib::Widget&) const {
        std::cout << "guard::trace — це ОБ'ЄКТ, тому ADL не вмикається\n";
    }
} trace{};
}

void part_switches() {
    head("5. Три вимикачі ADL");

    lib::Widget w{7};

    ask("lib::onlyAdl(w) // кваліфіковано ");  lib::onlyAdl(w);
    ask("onlyAdl(w)      // голе ім'я     ");  onlyAdl(w);
    {
        using guard::trace;                    // ім'я в цій області — не функція
        ask("trace(w)        // trace — об'єкт");  trace(w);
    }
}
