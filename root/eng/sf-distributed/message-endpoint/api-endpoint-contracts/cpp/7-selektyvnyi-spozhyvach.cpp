class IMessageSelector {
public:
    virtual ~IMessageSelector() = default;

    // Повертає true, якщо повідомлення відповідає критеріям підписки
    virtual bool matches(const MessageHeaders& headers) const = 0;
    
    // Текстовий вираз селектора у форматі SQL-92 (наприклад: "country = 'UA' AND amount > 100")
    virtual std::string getExpression() const = 0;
};
