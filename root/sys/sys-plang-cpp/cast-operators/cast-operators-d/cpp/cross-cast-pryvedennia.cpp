struct ILogger { virtual void log() = 0; virtual ~ILogger() = default; };
struct ISerializable { virtual void serialize() = 0; virtual ~ISerializable() = default; };

class NetworkService : public ILogger, public ISerializable {
public:
    void log() override {}
    void serialize() override {}
};

void process_service(ILogger* logger) {
    // ILogger та ISerializable не пов'язані між собою спадкуванням.
    // dynamic_cast знаходить через vtable спільний Most Derived Object (NetworkService)
    // та обчислює точну адресу інтерфейсу ISerializable:
    if (auto* serializable = dynamic_cast<ISerializable*>(logger)) {
        serializable->serialize();
    }
}
