#include <random>
#include <cstdint>

uint64_t generate_random_id() {
    // Кожен потік отримує власний екземпляр генератора,
    // ініціалізований унікальним зерном при першому виклику
    thread_local std::mt19937_64 engine([]() {
        std::random_device rd;
        return (static_cast<uint64_t>(rd()) << 32) ^ rd();
    }());
    
    std::uniform_int_distribution<uint64_t> dist;
    return dist(engine);
}
