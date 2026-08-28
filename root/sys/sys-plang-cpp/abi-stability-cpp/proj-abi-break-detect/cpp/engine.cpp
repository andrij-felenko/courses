// engine.cpp — реалізація приватного стану
#define ENGINE_EXPORTS
#include "engine.hpp"
#include <string>
#include <vector>
#include <chrono>
#include <iostream>

namespace engine {
inline namespace v1 {

struct Engine::EngineImpl {
    std::string config_path_;
    std::vector<double> performance_history_;
    std::chrono::high_resolution_clock::time_point launch_timestamp_;
    uint64_t step_counter_ = 0;

    void configure(std::string_view path) {
        config_path_ = std::string(path);
        launch_timestamp_ = std::chrono::high_resolution_clock::now();
    }

    double run_simulation(double dt) {
        step_counter_++;
        performance_history_.push_back(dt);
        return dt * 2.0;
    }
};

Engine::Engine() : impl_(std::make_unique<EngineImpl>()) {}

// Деструктор генерується саме тут, де повне визначення EngineImpl відоме компілятору
Engine::~Engine() = default;

Engine::Engine(Engine&&) noexcept = default;
Engine& Engine::operator=(Engine&&) noexcept = default;

// Реалізація глибокого копіювання: викликає конструктор копіювання EngineImpl
Engine::Engine(const Engine& other)
    : impl_(other.impl_ ? std::make_unique<EngineImpl>(*other.impl_) : nullptr) {}

Engine& Engine::operator=(const Engine& other) {
    if (this != &other) {
        if (other.impl_) {
            impl_ = std::make_unique<EngineImpl>(*other.impl_);
        } else {
            impl_.reset();
        }
    }
    return *this;
}

void Engine::initialize(std::string_view config_path) {
    impl_->configure(config_path);
}

double Engine::execute_step(double delta_time) {
    return impl_->run_simulation(delta_time);
}

} // namespace v1
} // namespace engine
