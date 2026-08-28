namespace std {

template <typename R>
class promise {
public:
    // 1. Конструктори та деструктор
    promise();
    template <typename Alloc>
    promise(allocator_arg_t alloc, const Alloc& a);
    
    promise(const promise&) = delete;
    promise(promise&& rhs) noexcept;
    
    ~promise();

    // 2. Оператори присвоєння
    promise& operator=(const promise&) = delete;
    promise& operator=(promise&& rhs) noexcept;

    void swap(promise& other) noexcept;

    // 3. Отримання зв'язаного future
    future<R> get_future();

    // 4. Запис результату (для загальної форми R)
    void set_value(const R& value);
    void set_value(R&& value);
    void set_exception(exception_ptr p);

    // 5. Запис результату зі зсувом сповіщення до завершення потоку
    void set_value_at_thread_exit(const R& value);
    void set_value_at_thread_exit(R&& value);
    void set_exception_at_thread_exit(exception_ptr p);
};

// Спеціалізація для посилань
template <typename R>
class promise<R&> {
public:
    promise();
    ~promise();
    future<R&> get_future();
    void set_value(R& value);
    void set_exception(exception_ptr p);
    void set_value_at_thread_exit(R& value);
    void set_exception_at_thread_exit(exception_ptr p);
};

// Спеціалізація для void
template <>
class promise<void> {
public:
    promise();
    ~promise();
    future<void> get_future();
    void set_value();
    void set_exception(exception_ptr p);
    void set_value_at_thread_exit();
    void set_exception_at_thread_exit(exception_ptr p);
};

} // namespace std
