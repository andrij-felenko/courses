// hsm_engine.hpp — Типобезпечний рушій HSM на C++20
#pragma once

#include <cstdint>
#include <array>
#include <utility>

enum class Signal : uint16_t {
    Empty = 0,
    Entry,
    Exit,
    Init,
    UserStart = 10
};

struct Event {
    Signal   sig{Signal::Empty};
    uint32_t param{0};
};

enum class Result : uint8_t {
    Handled,
    Ignored,
    Transition,
    Super
};

template <typename Derived>
class HierarchicalStateMachine {
public:
    using StateHandler = Result (Derived::*)(const Event&);

    void init(StateHandler initial) {
        temp_ = initial;
        Event init_evt{Signal::Init, 0};
        (static_cast<Derived*>(this)->*temp_)(init_evt);
        state_ = temp_;

        Event entry_evt{Signal::Entry, 0};
        (static_cast<Derived*>(this)->*state_)(entry_evt);
    }

    void dispatch(const Event& e) {
        StateHandler s = state_;
        Result res = Result::Super;

        // Спливання події від листового стану вгору по дереву
        while (s != nullptr && res == Result::Super) {
            temp_ = nullptr;
            res = (static_cast<Derived*>(this)->*s)(e);
            if (res == Result::Super) {
                s = temp_; // Отримано батьківський суперстан
            }
        }

        if (res == Result::Transition) {
            execute_transition(temp_);
        }
    }

    Result top_state(const Event&) {
        return Result::Ignored;
    }

protected:
    Result transition(StateHandler target) {
        temp_ = target;
        return Result::Transition;
    }

    Result super_state(StateHandler super_handler) {
        temp_ = super_handler;
        return Result::Super;
    }

    Result handled() { return Result::Handled; }
    Result ignored() { return Result::Ignored; }

private:
    void execute_transition(StateHandler target) {
        static constexpr size_t kMaxDepth = 8;
        std::array<StateHandler, kMaxDepth> exit_path{};
        std::array<StateHandler, kMaxDepth> entry_path{};

        size_t exit_count = 0;
        size_t entry_count = 0;

        StateHandler s = state_;
        StateHandler t = target;

        // 1. Трасування гілки джерела вгору
        StateHandler curr = s;
        while (curr != nullptr && exit_count < kMaxDepth) {
            exit_path[exit_count++] = curr;
            temp_ = nullptr;
            Event empty_evt{Signal::Empty, 0};
            (static_cast<Derived*>(this)->*curr)(empty_evt);
            curr = temp_;
        }

        // 2. Трасування гілки цілі вгору
        curr = t;
        while (curr != nullptr && entry_count < kMaxDepth) {
            entry_path[entry_count++] = curr;
            temp_ = nullptr;
            Event empty_evt{Signal::Empty, 0};
            (static_cast<Derived*>(this)->*curr)(empty_evt);
            curr = temp_;
        }

        // 3. Пошук найменшого спільного предка (LCA)
        size_t lca_src_idx = exit_count;
        size_t lca_dst_idx = entry_count;
        bool found_lca = false;

        for (size_t i = 0; i < exit_count && !found_lca; ++i) {
            for (size_t j = 0; j < entry_count; ++j) {
                if (exit_path[i] == entry_path[j]) {
                    lca_src_idx = i;
                    lca_dst_idx = j;
                    found_lca = true;
                    break;
                }
            }
        }

        // 4. Виконання Exit-дій знизу вгору до LCA
        Event exit_evt{Signal::Exit, 0};
        for (size_t i = 0; i < lca_src_idx; ++i) {
            (static_cast<Derived*>(this)->*exit_path[i])(exit_evt);
        }

        // 5. Виконання Entry-дій згори вниз від LCA до цілі
        Event entry_evt{Signal::Entry, 0};
        if (lca_dst_idx > 0) {
            for (size_t j = lca_dst_idx; j > 0; --j) {
                (static_cast<Derived*>(this)->*entry_path[j - 1])(entry_evt);
            }
        }

        state_ = target;

        // 6. Початковий перехід цільового стану
        Event init_evt{Signal::Init, 0};
        (static_cast<Derived*>(this)->*state_)(init_evt);
    }

    StateHandler state_{nullptr};
    StateHandler temp_{nullptr};
};
