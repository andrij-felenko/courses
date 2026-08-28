class NetworkGateway {
public:
    std::future<std::string> request_async(const std::string& query) {
        auto p = std::make_shared<std::promise<std::string>>();
        std::future<std::string> f = p->get_future();

        // Реєструємо асинхронний зворотний виклик у мережевому рушії
        async_network_send(query, [p](std::string response, bool error) {
            if (error) {
                p->set_exception(std::make_exception_ptr(
                    std::runtime_error("Помилка мережі!")
                ));
            } else {
                p->set_value(response);
            }
        });

        return f;
    }
};
