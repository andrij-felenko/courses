#include <iostream>
#include <memory>
#include <string>
#include <chrono>

// Шаблонний базовий клас CRTP
template <typename Derived>
class ObservableMixin {
protected:
    // Захищений невіртуальний деструктор блокує небезпечне видалення
    ~ObservableMixin() = default;

public:
    void emit_event(const std::string& msg) {
        // Статична диспетчеризація часу компіляції (inline)
        static_cast<Derived*>(this)->handle_event(msg);
    }
};

// Конкретний сервіс
class TelemetryManager : public ObservableMixin<TelemetryManager> {
    int counter{0};
public:
    void handle_event(const std::string& msg) {
        ++counter;
        std::cout << "[Event #" << counter << "] " << msg << "\n";
    }

    ~TelemetryManager() {
        std::cout << "[~] TelemetryManager успішно очищено\n";
    }
};

int main() {
    std::cout << "=== Статичний поліморфізм CRTP ===\n";
    
    // 1. Створення на стеку
    {
        TelemetryManager manager;
        manager.emit_event("Ініціалізація датчиків");
    }

    // 2. Створення в купі через покажчик на конкретний тип
    {
        auto dynamic_mgr = std::make_unique<TelemetryManager>();
        dynamic_mgr->emit_event("Отримано кадр телеметрії");
    }

    // 3. Перевірка безпеки компіляції:
    /*
    ObservableMixin<TelemetryManager>* unsafe_ptr = new TelemetryManager();
    delete unsafe_ptr; // ПОМИЛКА КОМПІЛЯЦІЇ: деструктор захищений!
    */

    std::cout << "Розмір TelemetryManager: " << sizeof(TelemetryManager) << " байтів\n";
    return 0;
}
