class Person {
public:
    template <class S>
    explicit Person(S&& name) : name_(std::forward<S>(name)) {}

    Person(const Person&) = default;
    Person(Person&&)      = default;
private:
    std::string name_;
};

Person p{"Леся"};
const Person c = p;
Person q{p};        // ← помилка компіляції в тілі шаблонного конструктора
