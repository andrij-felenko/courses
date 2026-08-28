namespace std {

template <typename Signature>
class packaged_task; // Невизначений первинний шаблон

template <typename R, typename... Args>
class packaged_task<R(Args...)> {
public:
    // Конструктори
    packaged_task() noexcept;
    
    template <typename F>
    explicit packaged_task(F&& f);
    
    template <typename F, typename Alloc>
    packaged_task(allocator_arg_t alloc, const Alloc& a, F&& f);

    ~packaged_task();

    // Заборона копіювання, дозвіл переміщення
    packaged_task(const packaged_task&) = delete;
    packaged_task(packaged_task&& rhs) noexcept;
    
    packaged_task& operator=(const packaged_task&) = delete;
    packaged_task& operator=(packaged_task&& rhs) noexcept;

    void swap(packaged_task& other) noexcept;

    bool valid() const noexcept;

    // Отримання зв'язаного future
    future<R> get_future();

    // Виконання задачі
    void operator()(Args... args);
    void make_ready_at_thread_exit(Args... args);

    // Скидання стану для повторного використання
    void reset();
};

} // namespace std
