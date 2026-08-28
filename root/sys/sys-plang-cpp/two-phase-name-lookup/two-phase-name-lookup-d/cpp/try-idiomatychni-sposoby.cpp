template <typename T>
class DerivedFixed : public Base<T> {
public:
    void reset_v1() {
        // Рішення 1: Явне використання вказівника this->
        // Вираз this->clear_cache() є залежним, бо this має тип DerivedFixed<T>*
        this->clear_cache();
        this->flags = 0;
    }

    void reset_v2() {
        // Рішення 2: Явна кваліфікація іменем базового класу
        // Перетворює ім'я на залежне кваліфіковане ім'я
        Base<T>::clear_cache();
        Base<T>::flags = 0;
    }

    // Рішення 3: Введення імен в область видимості класу через using (найкраща практика)
    using Base<T>::clear_cache;
    using Base<T>::flags;

    void reset_v3() {
        // Тепер виклики працюють без префіксів у будь-якому місці класу
        clear_cache();
        flags = 0;
    }
};
