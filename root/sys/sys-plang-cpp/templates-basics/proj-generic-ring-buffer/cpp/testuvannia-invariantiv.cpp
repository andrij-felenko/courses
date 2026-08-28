struct InstanceTracker {
    static inline int live_instances = 0;
    static inline int constructor_calls = 0;
    static inline int destructor_calls = 0;

    int id;

    explicit InstanceTracker(int val) : id(val) {
        ++live_instances;
        ++constructor_calls;
    }

    InstanceTracker(const InstanceTracker& other) : id(other.id) {
        ++live_instances;
        ++constructor_calls;
    }

    InstanceTracker(InstanceTracker&& other) noexcept : id(other.id) {
        ++live_instances;
        ++constructor_calls;
    }

    ~InstanceTracker() {
        --live_instances;
        ++destructor_calls;
    }
};

void run_memory_lifecycle_test() {
    {
        RingBuffer<InstanceTracker, 4> tracker_buffer;
        tracker_buffer.emplace(1);
        tracker_buffer.emplace(2);
        tracker_buffer.emplace(3);

        std::cout << "Створено об'єктів: " << InstanceTracker::live_instances << " (очікується 3)\n";

        auto item = tracker_buffer.pop(); // Вилучаємо один елемент
        std::cout << "Після pop(): живих " << InstanceTracker::live_instances << " (очікується 3: 2 в буфері + 1 у змінній item)\n";
    }
    // При виході з блоку знищується tracker_buffer та item
    std::cout << "Після завершення області видимості: живих " << InstanceTracker::live_instances << " (очікується 0)\n";
}
