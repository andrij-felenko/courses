class SubsystemRegistry {
private:
    std::atomic<SubsystemNode*> head_{nullptr};
    std::atomic<size_t> count_{0};

public:
    // Конструктор гарантує нульовий початковий стан на етапі компіляції
    constexpr SubsystemRegistry() noexcept
        : head_(nullptr), count_(0) {}

    SubsystemRegistry(const SubsystemRegistry&) = delete;
    SubsystemRegistry& operator=(const SubsystemRegistry&) = delete;

    // Безблокувальне додавання вузла до списку
    void register_subsystem(SubsystemNode* node) noexcept {
        if (!node) return;

        SubsystemNode* current_head = head_.load(std::memory_order_relaxed);
        do {
            node->next = current_head;
        } while (!head_.compare_exchange_weak(
            current_head, node,
            std::memory_order_release,
            std::memory_order_relaxed
        ));

        count_.fetch_add(1, std::memory_order_relaxed);
    }

    void start_all() const {
        SubsystemNode* curr = head_.load(std::memory_order_acquire);
        while (curr) {
            if (curr->initialize_fn) {
                curr->initialize_fn();
            }
            curr = curr->next;
        }
    }

    [[nodiscard]] size_t size() const noexcept {
        return count_.load(std::memory_order_relaxed);
    }
};

// Глобальний екземпляр реєстру в заголовковому файлі
inline constinit SubsystemRegistry g_registry{};
