// Приблизна внутрішня концептуальна структура packaged_task
template<typename R, typename... Args>
class packaged_task<R(Args...)> {
    struct task_base {
        virtual ~task_base() = default;
        virtual void invoke(Args&&... args) = 0;
    };

    template<typename F>
    struct task_impl : task_base {
        F func_;
        std::promise<R> promise_;
        // ...
    };

    std::unique_ptr<task_base> ptr_;
};
