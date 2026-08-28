class MessageHandler {
public:
    virtual ~MessageHandler() = default;

    // Чистий метод із визначенням за межами класу
    virtual void log_event(const std::string& msg) = 0;
};

// Визначення базової поведінки
void MessageHandler::log_event(const std::string& msg) {
    std::cout << "[DEFAULT LOG]: " << msg << "\n";
}
