#include <mutex>
#include <memory>

struct SessionContext {
    int auth_level;
};

void setup_session(std::unique_ptr<SessionContext> ctx) {
    // Володіння контекстом переходить сюди
}

void initialize(std::once_flag& flag, std::unique_ptr<SessionContext> ctx) {
    std::call_once(flag, setup_session, std::move(ctx));
}
