// DuffingEngine.hpp — Об'єктно-орієнтована C++20 обгортка
#ifndef DUFFING_ENGINE_HPP
#define DUFFING_ENGINE_HPP

#include "duffing_engine.h"
#include <vector>
#include <span>
#include <expected>
#include <string>
#include <memory>

namespace duffing {

enum class ErrorCode {
    InvalidParam,
    NullPointer,
    NumericalDivergence,
    AllocationFailure
};

struct Config : public duffing_config_t {};
struct State  : public duffing_state_t {};

class Solver {
public:
    // RAII Створення: повертає std::expected з екземпляром розв'язувача або помилкою
    static std::expected<Solver, ErrorCode> create(
        const Config& config,
        State initialState,
        double stepSize) 
    {
        duffing_solver_t* rawSolver = nullptr;
        duffing_status_t st = duffing_solver_create(&config, initialState, stepSize, &rawSolver);
        if (st != DUFFING_SUCCESS) {
            return std::unexpected(mapStatus(st));
        }
        return Solver(rawSolver);
    }

    ~Solver() {
        if (handle_) {
            duffing_solver_destroy(handle_);
        }
    }

    Solver(const Solver&) = delete;
    Solver& operator=(const Solver&) = delete;

    Solver(Solver&& other) noexcept : handle_(other.handle_) {
        other.handle_ = nullptr;
    }

    Solver& operator=(Solver&& other) noexcept {
        if (this != &other) {
            if (handle_) duffing_solver_destroy(handle_);
            handle_ = other.handle_;
            other.handle_ = nullptr;
        }
        return *this;
    }

    // Виконання кроку
    std::expected<void, ErrorCode> step() noexcept {
        duffing_status_t st = duffing_solver_step(handle_);
        if (st != DUFFING_SUCCESS) return std::unexpected(mapStatus(st));
        return {};
    }

    // Відбір точок для перерізу Пуанкаре в std::vector
    std::expected<std::vector<State>, ErrorCode> generatePoincare(
        std::size_t numPoints,
        std::size_t stepsPerPeriod) 
    {
        std::vector<State> buffer(numPoints);
        duffing_status_t st = duffing_solver_sample_poincare(
            handle_,
            buffer.data(),
            numPoints,
            stepsPerPeriod
        );
        if (st != DUFFING_SUCCESS) {
            return std::unexpected(mapStatus(st));
        }
        return buffer;
    }

    [[nodiscard]] State getState() const noexcept {
        State s{};
        duffing_solver_get_state(handle_, &s);
        return s;
    }

private:
    explicit Solver(duffing_solver_t* handle) noexcept : handle_(handle) {}

    static ErrorCode mapStatus(duffing_status_t st) noexcept {
        switch (st) {
            case DUFFING_ERROR_INVALID_PARAM:     return ErrorCode::InvalidParam;
            case DUFFING_ERROR_NULL_POINTER:      return ErrorCode::NullPointer;
            case DUFFING_ERROR_NUMERICAL_DIVERGE: return ErrorCode::NumericalDivergence;
            default:                              return ErrorCode::AllocationFailure;
        }
    }

    duffing_solver_t* handle_{ nullptr };
};

} // namespace duffing

#endif // DUFFING_ENGINE_HPP
