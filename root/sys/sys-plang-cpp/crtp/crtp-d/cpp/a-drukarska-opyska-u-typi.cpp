template <typename Derived>
class SafeBase {
private:
    SafeBase() = default;
    friend Derived; // Лише справжній Derived може викликати конструктор!

public:
    void interface() {
        static_cast<Derived*>(this)->impl();
    }
};

class Correct : public SafeBase<Correct> {}; // OK
