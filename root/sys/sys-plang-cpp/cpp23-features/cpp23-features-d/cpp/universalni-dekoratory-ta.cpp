template <typename Target>
struct LoggingWrapper {
    Target inner;

    template <typename Self, typename... Args>
    auto execute(this Self&& self, Args&&... args) 
        -> decltype(auto) 
    {
        std::println("Початок виконання операції");
        return std::forward_like<Self>(self.inner).execute(std::forward<Args>(args)...);
    }
};
