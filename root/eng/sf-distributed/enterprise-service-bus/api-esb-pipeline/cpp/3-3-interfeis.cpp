class IContentBasedRouter {
public:
    virtual ~IContentBasedRouter() = default;
    
    // Оцінка правил та повернення списку цільових адрес (Unicast / Multicast)
    [[nodiscard]] virtual std::vector<std::string> route(const NormalizedMessage& message) const = 0;
    
    // Динамічна реєстрація правила маршрутизації без зупинки процесу
    virtual void register_rule(std::string_view rule_expression, std::string_view target_endpoint) = 0;
};
