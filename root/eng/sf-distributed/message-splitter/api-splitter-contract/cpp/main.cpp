// Контракт C++ SDK для інтеграції користувацьких обробників
class ISplitterEventHandler {
public:
    virtual ~ISplitterEventHandler() = default;
    
    // Викликається перед початком розбиття пакета
    virtual void on_batch_start(const std::string& correlation_id, uint64_t total_items) = 0;
    
    // Викликається для кожного успішно виділеного елемента
    virtual void on_item_emitted(const DiscreteMessageEnvelope& envelope) = 0;
    
    // Викликається при виявленні пошкодженого кадру
    virtual void on_item_error(const SplitErrorEvent& error_event) = 0;
    
    // Викликається після успішної емісії всіх елементів пакета
    virtual void on_batch_complete(const std::string& correlation_id, uint64_t emitted_count) = 0;
    
    // Викликається при виникненні фатального збою структури потоку
    virtual void on_batch_abort(const std::string& correlation_id, std::string_view reason) = 0;
};
