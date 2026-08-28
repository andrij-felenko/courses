// Реалізація черги у C++23 без використання std::shared_ptr та без виділення пам'яті під лічильник посилань
std::queue<std::move_only_function<void()>> tasks_;

template<typename F, typename... Args>
auto enqueue(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
    using return_type = std::invoke_result_t<F, Args...>;
    
    std::packaged_task<return_type()> task(
        std::bind_front(std::forward<F>(f), std::forward<Args>(args)...)
    );
    
    std::future<return_type> res = task.get_future();

    {
        std::unique_lock<std::mutex> lock(queue_mutex_);
        if (stop_) throw std::runtime_error("TaskExecutor is stopped");
        
        // Пряме переміщення packaged_task у move_only_function без std::shared_ptr!
        tasks_.emplace([task = std::move(task)]() mutable { 
            task(); 
        });
    }
    cv_.notify_one();
    return res;
}
