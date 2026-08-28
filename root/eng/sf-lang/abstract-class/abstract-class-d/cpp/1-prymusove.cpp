class NetworkHandler : public MessageHandler {
public:
    void log_event(const std::string& msg) override {
        // Явний виклик базової логіки предка
        MessageHandler::log_event(msg);
        // Додаткова специфічна дія
        send_to_remote_syslog(msg);
    }
private:
    void send_to_remote_syslog(const std::string& msg) { /* ... */ }
};
