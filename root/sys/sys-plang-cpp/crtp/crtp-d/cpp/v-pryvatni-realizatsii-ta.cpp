template <typename Derived>
class Base {
public:
    void run() {
        static_cast<Derived*>(this)->secret_impl(); // Помилка доступу!
    }
};

class Worker : public Base<Worker> {
private:
    // Потрібно надати доступ базовому шаблону:
    friend class Base<Worker>;

    void secret_impl() {
        // Приватна реалізація
    }
};
