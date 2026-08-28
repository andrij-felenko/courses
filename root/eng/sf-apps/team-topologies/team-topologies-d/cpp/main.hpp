// Командний API платформи = програмний API.
// Потокова команда бачить лише це — не знає ні черг, ні реплік, ні дата-центрів.
namespace platform {
    // «Ми надаємо публікацію події як сервіс. Виклик синхронний, доставка гарантована.»
    bool publish(const std::string& topic, const std::string& payload);

    // «Підписка — теж наш сервіс. Ви даєте обробник, решта — наша справа.»
    void subscribe(const std::string& topic,
                   std::function<void(const std::string&)> handler);
}
