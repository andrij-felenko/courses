struct HttpHeader {
    std::string_view key;
    std::string_view value;
};

struct HttpRequest {
    std::string_view method;
    std::string_view uri;
    HttpHeader* headers{nullptr};
    std::size_t header_count{0};
    std::byte* body{nullptr};
    std::size_t body_size{0};
};

// Обробка одного мережевого запиту в робочому потоці
void process_incoming_request(std::string_view raw_packet) {
    // 1. Отримуємо посилання на локальну арену поточного потоку
    auto& arena = g_per_thread_arena;

    // 2. Виділяємо структуру запиту з арени (0 викликів глобального malloc!)
    auto* req = arena.create<HttpRequest>();
    req->method = "POST";
    req->uri = "/api/v1/telemetry";

    // 3. Виділяємо масив заголовків у локальній пам'яті потоку
    constexpr std::size_t max_headers = 8;
    req->headers = static_cast<HttpHeader*>(
        arena.allocate(sizeof(HttpHeader) * max_headers, alignof(HttpHeader))
    );
    req->header_count = 2;
    req->headers[0] = {"Content-Type", "application/json"};
    req->headers[1] = {"X-Thread-ID", "worker-4"};

    // 4. Імітація обробки запиту
    // ... парсинг, перевірка авторизації, обчислення ...

    // 5. Миттєве очищення всієї пам'яті запиту за 1 такт CPU!
    arena.reset();
}
