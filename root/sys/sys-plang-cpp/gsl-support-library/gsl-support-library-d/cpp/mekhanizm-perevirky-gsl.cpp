template <class Target, class Source>
constexpr Target narrow(Source u) {
    Target t = static_cast<Target>(u);
    // Перевірка 1: Чи повертає зворотне приведення вихідне значення?
    // Перевірка 2: Чи збігаються знаки вихідного та цільового чисел?
    if (static_cast<Source>(t) != u || ((t < Target{}) != (u < Source{}))) {
        throw narrowing_error{};
    }
    return t;
}
