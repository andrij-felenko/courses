#include <cstdint>
#include <mutex>

// Спільний лічильник: його бачать УСІ потоки, що обробляють запити.
static std::uint64_t g_requests = 0;
static std::mutex g_lock;

void handle_request(const char *path) {
    route(path);                          // ← видно у ФУНКЦІЙНІЙ в'ю: що викликає що

    {
        std::lock_guard<std::mutex> guard(g_lock);  // ← видно у КОНКУРЕНТНІЙ в'ю: точка синхронізації
        g_requests++;                     //    спільний ресурс під замком
    }
}
