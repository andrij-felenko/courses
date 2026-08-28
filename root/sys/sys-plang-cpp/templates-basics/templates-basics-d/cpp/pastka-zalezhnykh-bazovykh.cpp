template <typename T>
class Base {
public:
    void setup();
};

template <typename T>
class Derived : public Base<T> {
public:
    void init() {
        // setup(); // ПОМИЛКА: компілятор на Фазі 1 не бачить setup!
    }
};
