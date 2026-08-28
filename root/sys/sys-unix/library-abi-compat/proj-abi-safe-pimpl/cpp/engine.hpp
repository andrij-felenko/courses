// ==================== C++ ABI (Pimpl з std::unique_ptr) ====================
// engine.hpp (Публічний API заголовка)
#ifndef ENGINE_HPP
#define ENGINE_HPP

#include <memory>
#include <string_view>
#include <span>

class NetworkEngine {
public:
    NetworkEngine(std::string_view host, int port);
    ~NetworkEngine(); // Оголошено в заголовку, визначено у .cpp!

    // Операції переміщення
    NetworkEngine(NetworkEngine&&) noexcept;
    NetworkEngine& operator=(NetworkEngine&&) noexcept;

    // Забороняємо копіювання для збереження єдиного володіння
    NetworkEngine(const NetworkEngine&) = delete;
    NetworkEngine& operator=(const NetworkEngine&) = delete;

    bool send(std::span<const std::byte> data);

private:
    struct Impl; // Випереджувальне оголошення (forward declaration)
    std::unique_ptr<Impl> impl_; // Фіксований розмір об'єкта (8 байтів)
};

#endif // ENGINE_HPP

// engine.cpp (Файл реалізації всередині бібліотеки)
#include "engine.hpp"
#include <string>
#include <iostream>

struct NetworkEngine::Impl {
    std::string host;
    int port;
    // Нові поля версії 2.0 додаються у цей struct без зміни розміру NetworkEngine!
    int timeout_ms{5000};
    uint64_t packets_sent{0};
};

NetworkEngine::NetworkEngine(std::string_view host, int port)
    : impl_(std::make_unique<Impl>(std::string(host), port)) {}

// Деструктор обов'язково визначено у .cpp, де тип Impl є повністю відомим для std::default_delete!
NetworkEngine::~NetworkEngine() = default;

NetworkEngine::NetworkEngine(NetworkEngine&&) noexcept = default;
NetworkEngine& NetworkEngine::operator=(NetworkEngine&&) noexcept = default;

bool NetworkEngine::send(std::span<const std::byte> data) {
    if (!impl_) return false;
    impl_->packets_sent++;
    std::cout << "Sent " << data.size() << " bytes to " << impl_->host << ":" << impl_->port << "\n";
    return true;
}
