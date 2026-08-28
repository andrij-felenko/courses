/* ПОВНІСТЮ ПОТОКОБЕЗПЕЧНИЙ SINGLETON (C++11 Meyer's Singleton) */
class ModernSingleton {
public:
    static ModernSingleton& get_instance() {
        // Стандарт C++11 гарантує потокобезпечну ініціалізацію під час першого виклику
        static ModernSingleton instance;
        return instance;
    }
private:
    ModernSingleton() = default;
};
