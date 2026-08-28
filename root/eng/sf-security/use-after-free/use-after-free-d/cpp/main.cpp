#include <memory>
#include <iostream>

class ResourceSession {
public:
    void perform_work() {
        std::cout << "[+] Безпечне виконання операції над сесією.\n";
    }
};

void modern_safe_flow() {
    // 1. Монопольне володіння: автоматичне детерміноване звільнення
    auto unique_res = std::make_unique<ResourceSession>();
    unique_res->perform_work();
    // unique_res автоматично та безпечно знищується при виході з функції

    // 2. Спільне володіння через слабкі посилання (weak_ptr)
    std::weak_ptr<ResourceSession> observer;
    {
        auto shared_res = std::make_shared<ResourceSession>();
        observer = shared_res; // Створення спостерігача

        if (auto active = observer.lock()) {
            active->perform_work();
        }
    } // shared_res знищується тут, лічильник власників = 0

    // Спроба доступу після знищення
    if (auto active = observer.lock()) {
        active->perform_work();
    } else {
        std::cout << "[+] Ресурс безпечно відсутній: спробу UAF повністю усунуто.\n";
    }
}
