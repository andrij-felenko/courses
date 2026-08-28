#include <iostream>
#include <array>
#include <string_view>
#include <cstdint>
#include <cassert>

enum class FsmState : uint8_t {
    Idle   = 0b00,
    Purge  = 0b01,
    Ignite = 0b10,
    Run    = 0b11
};

struct FsmInputs {
    bool start{false};
    bool done{false};
    bool flame{false};
    bool abort{false};
};

struct FsmOutputs {
    bool fan{false};
    bool valve{false};
    bool spark{false};
    bool ok{false};

    [[nodiscard]] constexpr bool operator==(const FsmOutputs &other) const noexcept = default;
};

// -------------------------------------------------------------
// 1. Еталонна поведінкова модель (Golden Model)
// -------------------------------------------------------------
class GoldenFsm {
public:
    constexpr GoldenFsm() noexcept : state_{FsmState::Idle} {}

    [[nodiscard]] constexpr FsmState state() const noexcept { return state_; }

    [[nodiscard]] constexpr FsmOutputs outputs() const noexcept {
        switch (state_) {
            case FsmState::Idle:   return {.fan = false, .valve = false, .spark = false, .ok = false};
            case FsmState::Purge:  return {.fan = true,  .valve = false, .spark = false, .ok = false};
            case FsmState::Ignite: return {.fan = true,  .valve = true,  .spark = true,  .ok = false};
            case FsmState::Run:    return {.fan = true,  .valve = true,  .spark = false, .ok = true};
        }
        return {};
    }

    constexpr void tick(const FsmInputs &in) noexcept {
        if (in.abort) {
            state_ = FsmState::Idle;
            return;
        }
        switch (state_) {
            case FsmState::Idle:
                if (in.start) state_ = FsmState::Purge;
                break;
            case FsmState::Purge:
                if (in.done) state_ = FsmState::Ignite;
                break;
            case FsmState::Ignite:
                state_ = in.flame ? FsmState::Run : FsmState::Idle;
                break;
            case FsmState::Run:
                if (!in.flame) state_ = FsmState::Idle;
                break;
        }
    }

private:
    FsmState state_;
};

// -------------------------------------------------------------
// 2. Повентильний емулятор схеми 74HC
// -------------------------------------------------------------
class DiscreteLogicFsm {
public:
    constexpr DiscreteLogicFsm() noexcept : q1_{false}, q0_{false} {}

    [[nodiscard]] constexpr uint8_t raw_state() const noexcept {
        return static_cast<uint8_t>((q1_ ? 0b10 : 0b00) | (q0_ ? 0b01 : 0b00));
    }

    [[nodiscard]] constexpr FsmOutputs outputs() const noexcept {
        return {
            .fan   = q1_ || q0_,
            .valve = q1_,
            .spark = q1_ && !q0_,
            .ok    = q1_ && q0_
        };
    }

    constexpr void tick(const FsmInputs &in) noexcept {
        // Обчислення булевих функцій наступного стану
        const bool d1 = (!q1_ && q0_ && in.done && !in.abort) ||
                        (q1_ && in.flame && !in.abort);

        const bool d0 = (!q1_ && !q0_ && in.start && !in.abort) ||
                        (!q1_ && q0_ && !in.done && !in.abort) ||
                        (q1_ && !q0_ && in.flame && !in.abort);

        // Фіксація по тактовому фронту
        q1_ = d1;
        q0_ = d0;
    }

private:
    bool q1_;
    bool q0_;
};

// -------------------------------------------------------------
// 3. Тестова верифікація обох моделей
// -------------------------------------------------------------
int main() {
    GoldenFsm golden;
    DiscreteLogicFsm discrete;

    constexpr std::array<FsmInputs, 8> test_sequence{{
        {.start = false, .done = false, .flame = false, .abort = false},
        {.start = true,  .done = false, .flame = false, .abort = false},
        {.start = false, .done = false, .flame = false, .abort = false},
        {.start = false, .done = true,  .flame = false, .abort = false},
        {.start = false, .done = false, .flame = true,  .abort = false},
        {.start = false, .done = false, .flame = true,  .abort = false},
        {.start = false, .done = false, .flame = false, .abort = false},
        {.start = false, .done = false, .flame = false, .abort = false}
    }};

    for (const auto &inputs : test_sequence) {
        assert(static_cast<uint8_t>(golden.state()) == discrete.raw_state());
        assert(golden.outputs() == discrete.outputs());

        golden.tick(inputs);
        discrete.tick(inputs);
    }

    return 0;
}
