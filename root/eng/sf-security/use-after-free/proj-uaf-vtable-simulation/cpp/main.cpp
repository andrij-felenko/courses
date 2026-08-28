#include <iostream>
#include <memory>
#include <string>
#include <cstdint>

/* Базовий поліморфний інтерфейс сервісу */
class IAuthHandler {
public:
    virtual ~IAuthHandler() = default;
    virtual void verify_token(int user_id) = 0;
};

class StandardAuth : public IAuthHandler {
public:
    void verify_token(int user_id) override {
        std::cout << "[+] Стандартна авторизація: користувача " << user_id << " підтверджено як гостя.\n";
    }
};

/* Клас імітації шкідливого навантаження з сумісною структурою vtable */
class ExploitPayload : public IAuthHandler {
public:
    void verify_token(int user_id) override {
        std::cout << "[!] ПЕРЕХОПЛЕННЯ VTABLE: Виконано привілейований метод для UID " << user_id << "!\n";
    }
};

/* Безпечна реалізація з використанням RAII та розумних вказівників */
void demonstrate_safe_cpp_lifecycle() {
    std::cout << "\n=== Безпечна C++ альтернатива (std::shared_ptr + std::weak_ptr) ===\n";

    std::weak_ptr<IAuthHandler> weak_session;

    {
        auto shared_session = std::make_shared<StandardAuth>();
        weak_session = shared_session;

        if (auto locked = weak_session.lock()) {
            locked->verify_token(1001);
        }
    } // shared_session знищується тут, пам'ять коректно вивільняється

    // Спроба використати ресурс після завершення його життєвого циклу
    if (auto locked = weak_session.lock()) {
        locked->verify_token(1001);
    } else {
        std::cout << "[+] weak_ptr успішно запобіг UAF: ресурс своєчасно вивільнено, доступ заблоковано.\n";
    }
}

int main() {
    std::cout << "=== Симуляція Use-After-Free у C++ із віртуальними таблицями ===\n\n";

    // 1. Створення об'єкта через сирий вказівник (небезпечний підхід)
    IAuthHandler* volatile dangling_ptr = new StandardAuth();
    std::cout << "[1] Створено StandardAuth за адресою: " << dangling_ptr << "\n";
    dangling_ptr->verify_token(42);

    // 2. Звільнення об'єкта
    delete dangling_ptr;
    std::cout << "[2] Об'єкт видалено через delete. Вказівник став завислим.\n";

    // 3. Перевикористання пам'яті новим об'єктом іншого підтипу
    IAuthHandler* payload = new ExploitPayload();
    std::cout << "[3] Створено ExploitPayload за адресою: " << payload << "\n";

    // 4. Розіменування старого вказівника (виклик віртуального методу через підмінену vtable)
    std::cout << "[4] Звернення через завислий вказівник dangling_ptr->verify_token():\n";
    dangling_ptr->verify_token(42);

    delete payload;

    // Демонстрація ідіоматичного безпечного керування ресурсами
    demonstrate_safe_cpp_lifecycle();

    return 0;
}
