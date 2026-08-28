namespace dlog::api {
    class Context {
    public:
        explicit Context(const Config& config = {});
        ~Context();
        Context(const Context&) = delete;
        Context& operator=(const Context&) = delete;
        Context(Context&&) noexcept;
        Context& operator=(Context&&) noexcept;

        [[nodiscard]] void* get_native_handle() const noexcept;
    private:
        void* handle_ = nullptr;
    };
}
