// Коректний C++ код: автоматичне керування через RAII-делетер
struct EngineDeleter {
    void operator()(engine_t* ptr) const noexcept {
        engine_destroy(ptr);
    }
};

using ScopedEngine = std::unique_ptr<engine_t, EngineDeleter>;

void run() {
    engine_t* raw = nullptr;
    engine_create(&raw, "AES");
    ScopedEngine handle(raw);
    // engine_destroy викличеться автоматично наприкінці області видимості
}
