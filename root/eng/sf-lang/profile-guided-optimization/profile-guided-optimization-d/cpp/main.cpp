// Вихідний поліморфний виклик через інтерфейс (C++)
class IHandler {
public:
    virtual ~IHandler() = default;
    virtual uint64_t process(const void* data) const = 0;
};

class FastHandler final : public IHandler {
public:
    uint64_t process(const void* data) const override {
        return *reinterpret_cast<const uint64_t*>(data) * 42;
    }
};

uint64_t dispatch(const IHandler* h, const void* data) {
    // Віртуальний виклик у статичній збірці:
    // return h->process(data);

    // Трансформація компілятора після PGO (Спекулятивна девіртуалізація):
    if (typeid(*h) == typeid(FastHandler)) {
        // Прямий виклик + повний інлайнінг методу FastHandler::process
        return static_cast<const FastHandler*>(h)->FastHandler::process(data);
    } else {
        // Звичайний поліморфний виклик через vtable
        return h->process(data);
    }
}
