template <typename Derived>
class BaseProcessor {
public:
    void reset_state() {
        // Логіка скидання стану
    }
};

template <typename Derived>
class AdvancedProcessor : public BaseProcessor<Derived> {
public:
    void process() {
        // reset_state(); // ПОМИЛКА: ім'я не знайдене під час фази 1!
        this->reset_state(); // OK: тепер це залежне ім'я, пошук відкладено до фази 2
    }
};
