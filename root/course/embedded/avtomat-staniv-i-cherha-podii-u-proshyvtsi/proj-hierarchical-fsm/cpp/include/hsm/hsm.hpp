// hsm.hpp — рушій ієрархічного автомата станів (Statecharts) для прошивок.
//
// Автомат описується як клас, що успадковується від StateMachine<Себе>
// (CRTP): стани — приватні методи-обробники, ієрархія задається тим, що
// обробник у гілці default повертає parent(свій_суперстан).
//
// CRTP тут не прикраса. Він робить тип State вказівником на метод САМЕ
// похідного класу, тож жодного приведення вказівників на методи не
// потрібно — а такі приведення і є найтоншим місцем у сішному рушії.
// Розкладка станів, дерево й глибина перевіряються тим самим компілятором,
// що збирає прошивку.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace hsm {

enum class Signal : std::uint16_t {
    Empty = 0, // внутрішній зонд рушія: «назви свого суперстан»
    Entry = 1, // вхід у стан
    Exit  = 2, // вихід зі стану
    Init  = 3, // вибір типового підстану складеного стану
    User  = 4  // перший сигнал застосунку
};

// Сигнал застосунку за порядковим номером: userSignal(0) — перший вільний.
[[nodiscard]] constexpr Signal userSignal(std::uint16_t offset) noexcept {
    return static_cast<Signal>(static_cast<std::uint16_t>(Signal::User) + offset);
}

struct Event {
    Signal sig{Signal::Empty};
    std::uintptr_t param{0};
};

enum class Result : std::uint8_t {
    Handled,    // подію оброблено, підйом припиняється
    Ignored,    // подію свідомо проковтнуто, суперстанові не віддаємо
    Transition, // стан ініціював перехід
    Super       // логіки немає, подія йде до суперстану
};

enum class Fault : std::uint8_t {
    DepthExceeded,      // дерево станів глибше за kMaxDepth
    BadHandlerResult,   // обробник відповів не за протоколом
    NotAnAncestor,      // ціль переходу лежить поза гілкою предка
    NoInitialTransition // початковий псевдостан не назвав цілі
};

// Порушення контракту рушія. Реалізує застосунок; повертатися заборонено.
[[noreturn]] void onFault(Fault code, const char* where);

template <class Derived>
class StateMachine {
public:
    using State = Result (Derived::*)(const Event&);
    using Action = void (Derived::*)();

    // Глибина дерева станів. Визначає розмір масивів шляху на стеку і є
    // запобіжником: кожен обхід дерева обмежений цим числом ітерацій,
    // тож обробка події має сувору верхню межу часу.
    static constexpr std::size_t kMaxDepth = 8;

    explicit StateMachine(State initial) : state_{topState()}, temp_{initial} {}

    // Корінь ієрархії: подій не обробляє, суперстану не має.
    [[nodiscard]] static State topState() noexcept {
        return static_cast<State>(&StateMachine::rootState);
    }

    // Початковий перехід: спуск від кореня до цілі з Entry згори донизу
    // і подальшим ланцюжком типових підстанів.
    void init() {
        const State initial = temp_;
        if (initial == nullptr) {
            onFault(Fault::NoInitialTransition, "init");
        }
        temp_ = topState();
        pending_ = nullptr;
        if (invoke(initial, Event{Signal::Init}) != Result::Transition) {
            onFault(Fault::NoInitialTransition, "init");
        }
        const State target = temp_;
        const Action action = takePending();
        runAction(action);
        enterFrom(topState(), target);
        state_ = target;
        takeInitialTransitions();
    }

    // Обробка однієї події до повного завершення (run-to-completion).
    void dispatch(const Event& e) {
        State source = state_;
        for (std::size_t depth = 0;; ++depth) {
            if (depth > kMaxDepth) {
                onFault(Fault::DepthExceeded, "dispatch");
            }
            if (source == topState()) {
                return; // подію не забрав ніхто
            }
            temp_ = topState();
            pending_ = nullptr;

            const Result r = invoke(source, e);
            if (r == Result::Handled || r == Result::Ignored) {
                pending_ = nullptr;
                return;
            }
            if (r == Result::Transition) {
                break;
            }
            if (r != Result::Super) {
                onFault(Fault::BadHandlerResult, "dispatch");
            }
            source = temp_; // подія піднімається до суперстану
        }

        const State target = temp_;
        const Action action = takePending();
        performTransition(source, target, action);
    }

    // Чи перебуває автомат у цьому стані або в будь-якому його підстані.
    [[nodiscard]] bool isIn(State s) {
        State cur = state_;
        for (std::size_t depth = 0; cur != topState(); ++depth) {
            if (depth > kMaxDepth) {
                onFault(Fault::DepthExceeded, "isIn");
            }
            if (cur == s) {
                return true;
            }
            cur = parentOf(cur);
        }
        return s == topState();
    }

protected:
    // Відповіді обробника. transition() приймає ще й дію, прив'язану до
    // самого переходу: рушій виконає її МІЖ гілкою виходу і гілкою входу.
    [[nodiscard]] static constexpr Result handled() noexcept { return Result::Handled; }
    [[nodiscard]] static constexpr Result ignored() noexcept { return Result::Ignored; }

    [[nodiscard]] Result transition(State target, Action action = nullptr) noexcept {
        temp_ = target;
        pending_ = action;
        return Result::Transition;
    }

    [[nodiscard]] Result parent(State super) noexcept {
        temp_ = super;
        pending_ = nullptr;
        return Result::Super;
    }

private:
    Result rootState(const Event&) { return Result::Ignored; }

    [[nodiscard]] Derived& self() noexcept { return static_cast<Derived&>(*this); }

    Result invoke(State s, const Event& e) { return (self().*s)(e); }

    void runAction(Action a) {
        if (a != nullptr) {
            (self().*a)();
        }
    }

    // Дія переходу дійсна лише всередині одного кроку run-to-completion,
    // тож її забирають одразу: наступний виклик обробника її затре.
    Action takePending() noexcept {
        const Action a = pending_;
        pending_ = nullptr;
        return a;
    }

    // Питає стан про суперстан зондом Signal::Empty. Обробник зобов'язаний
    // провалити невідомий сигнал у default і відповісти parent(...).
    State parentOf(State s) {
        temp_ = topState();
        if (invoke(s, Event{Signal::Empty}) != Result::Super) {
            onFault(Fault::BadHandlerResult, "parentOf");
        }
        return temp_;
    }

    // Виклик Entry згори вниз: масив зберігає шлях знизу вгору, тож
    // розкручуємо його з кінця.
    void enterPath(std::span<const State> path) {
        for (auto it = path.rbegin(); it != path.rend(); ++it) {
            static_cast<void>(invoke(*it, Event{Signal::Entry}));
        }
    }

    // Спуск від lca (виключно) до target (включно).
    void enterFrom(State lca, State target) {
        std::array<State, kMaxDepth> path{};
        std::size_t depth = 0;
        for (State s = target; s != lca; s = parentOf(s)) {
            if (s == topState()) {
                onFault(Fault::NotAnAncestor, "enterFrom");
            }
            if (depth >= kMaxDepth) {
                onFault(Fault::DepthExceeded, "enterFrom");
            }
            path[depth++] = s;
        }
        enterPath(std::span<const State>{path.data(), depth});
    }

    // Складений стан має право оголосити типовий підстан, той — свій,
    // і так далі. Довжина ланцюжка обмежена глибиною дерева.
    void takeInitialTransitions() {
        for (std::size_t guard = 0; guard <= kMaxDepth; ++guard) {
            const State source = state_;
            temp_ = topState();
            pending_ = nullptr;
            if (invoke(source, Event{Signal::Init}) != Result::Transition) {
                pending_ = nullptr;
                return; // стан не складений або типового підстану не має
            }
            const State target = temp_;
            const Action action = takePending();
            runAction(action);
            enterFrom(source, target);
            state_ = target;
        }
        onFault(Fault::DepthExceeded, "takeInitialTransitions");
    }

    [[nodiscard]] static std::optional<std::size_t> indexOf(
        std::span<const State> path, State s) noexcept {
        for (std::size_t i = 0; i < path.size(); ++i) {
            if (path[i] == s) {
                return i;
            }
        }
        return std::nullopt;
    }

    // Чотири фази переходу: вихід до LCA, дія переходу, вхід до цілі,
    // ланцюжок типових підстанів.
    void performTransition(State source, State target, Action action) {
        // 1а. Стани, глибші за джерело, гинуть завжди: подія піднялася
        // повз них, отже жоден із них її не обробив.
        std::size_t depth = 0;
        for (State s = state_; s != source; s = parentOf(s)) {
            if (s == topState()) {
                onFault(Fault::NotAnAncestor, "performTransition");
            }
            if (depth++ >= kMaxDepth) {
                onFault(Fault::DepthExceeded, "performTransition");
            }
            static_cast<void>(invoke(s, Event{Signal::Exit}));
        }

        // Перехід у себе: стан гарантовано перезапускається.
        if (source == target) {
            static_cast<void>(invoke(source, Event{Signal::Exit}));
            runAction(action);
            static_cast<void>(invoke(source, Event{Signal::Entry}));
            state_ = target;
            takeInitialTransitions();
            return;
        }

        // 1б. Гілка цілі знизу вгору: [0] — сама ціль.
        std::array<State, kMaxDepth> branch{};
        std::size_t branchDepth = 0;
        for (State t = target; t != topState(); t = parentOf(t)) {
            if (branchDepth >= kMaxDepth) {
                onFault(Fault::DepthExceeded, "targetBranch");
            }
            branch[branchDepth++] = t;
        }
        const std::span<const State> targetBranch{branch.data(), branchDepth};

        // 1в. Підйом від джерела, доки не натрапимо на стан із гілки цілі —
        // це і є LCA. Усе пройдене покидаємо; сам LCA лишається активним.
        std::size_t enterCount = branchDepth; // LCA не знайшовся — ним буде корінь
        depth = 0;
        for (State a = source; a != topState(); a = parentOf(a)) {
            if (depth++ > kMaxDepth) {
                onFault(Fault::DepthExceeded, "lcaSearch");
            }
            if (const auto k = indexOf(targetBranch, a); k.has_value()) {
                enterCount = *k; // входимо лише в те, що лежить нижче LCA
                break;
            }
            static_cast<void>(invoke(a, Event{Signal::Exit}));
        }

        // 2. Дія переходу: старої гілки вже немає, нової ще немає.
        runAction(action);

        // 3. Вхід згори вниз до цілі.
        enterPath(targetBranch.first(enterCount));

        state_ = target;

        // 4. Якщо ціль складена — спускаємось у її типовий підстан.
        takeInitialTransitions();
    }

    State state_;
    State temp_{};
    Action pending_{nullptr};
};

} // namespace hsm
