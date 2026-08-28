namespace trs {

// Інтерфейс користувацького порядку редукції
class IReductionOrder {
public:
    virtual ~IReductionOrder() = default;

    // Повертає true, якщо s > t за заданим порядком
    virtual bool is_greater(TermPtr s, TermPtr t) const = 0;

    // Перевірка сумісності порядку з поточною сигнатурою
    virtual bool validate_signature(const std::unordered_map<std::string, Symbol>& sig) const = 0;
};

} // namespace trs
