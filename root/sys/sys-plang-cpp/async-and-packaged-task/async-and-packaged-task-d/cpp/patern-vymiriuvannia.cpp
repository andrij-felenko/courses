template<typename Func>
auto make_measured_task(Func&& f) {
    using return_type = std::invoke_result_t<Func>;
    
    return std::packaged_task<return_type()>([f = std::forward<Func>(f)]() mutable {
        auto start = std::chrono::high_resolution_clock::now();
        
        if constexpr (std::is_same_v<return_type, void>) {
            f();
            auto elapsed = std::chrono::high_resolution_clock::now() - start;
            std::cout << "[Телеметрія] Час виконання: " 
                      << std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count() 
                      << " мкс" << std::endl;
        } else {
            auto res = f();
            auto elapsed = std::chrono::high_resolution_clock::now() - start;
            std::cout << "[Телеметрія] Час виконання: " 
                      << std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count() 
                      << " мкс" << std::endl;
            return res;
        }
    });
}
