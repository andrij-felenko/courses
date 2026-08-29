#pragma once

#include <optional>
#include <string_view>
#include <type_traits>
#include <utility>
#include <variant>

namespace evse {

/*
 * Патерн «стан як самостійна сутність» у мові, де замість покажчика на функцію
 * є std::variant. Кожен стан — окремий тип із власними даними; поточний стан —
 * альтернатива варіанта. Що це дає понад покажчик на функцію:
 *
 *  - стан може мати ВЛАСНІ поля, і вони існують рівно доти, доки триває стан;
 *  - набір станів закритий, тож std::visit не має гілки «а раптом щось інше»;
 *  - «стан не обробляє цю подію» перевіряється під час компіляції концептом,
 *    а не гілкою default у switch.
 */

template <class S, class Ctx>
concept HasEnter = requires(S& s, Ctx& c) { s.onEnter(c); };

template <class S, class Ctx>
concept HasExit = requires(S& s, Ctx& c) { s.onExit(c); };

template <class S, class Ctx, class E>
concept Handles = requires(S& s, Ctx& c, const E& e) { s.on(c, e); };

template <class Ctx, class... States>
class StateMachine {
public:
    using StateVariant = std::variant<States...>;

    explicit StateMachine(Ctx& ctx) noexcept : ctx_{ctx} {}

    /* Дія входу початкового стану — саме вона приводить апаратуру у визначений
     * вигляд після скидання, тому виконується явним стартом, а не в
     * конструкторі: до кінця конструювання власника чіпати апаратуру рано. */
    void start()
    {
        enterCurrent();
        applyPending();
    }

    /*
     * Заявка на перехід. Стан НЕ міняється тут-таки: обробник, який її подав,
     * зараз виконується всередині std::visit — знищити його об'єкт означало б
     * повернутися у вже неіснуюче тіло функції. Тому нова альтернатива чекає
     * в pending_ і застосовується, коли обробник завершиться.
     */
    template <class S, class... Args>
    void transitionTo(Args&&... args)
    {
        pending_.emplace(std::in_place_type<S>, std::forward<Args>(args)...);
    }

    /*
     * Диспетчеризація однієї події за принципом Run-To-Completion. Тип події
     * відомий на етапі компіляції, тому вибір обробника — не пошук у таблиці,
     * а звичайне розв'язання перевантаження.
     */
    template <class E>
    void dispatch(const E& event)
    {
        std::visit(
            [&](auto& state) {
                using S = std::remove_reference_t<decltype(state)>;
                if constexpr (Handles<S, Ctx, E>) {
                    state.on(ctx_, event);
                } else if constexpr (requires { ctx_.onUnhandled(event); }) {
                    /* Подія, якої стан не знає, підіймається до власника —
                     * плоский відповідник поведінкового наслідування HSM. */
                    ctx_.onUnhandled(event);
                }
            },
            current_);

        applyPending();
    }

    template <class S>
    [[nodiscard]] bool isIn() const noexcept
    {
        return std::holds_alternative<S>(current_);
    }

    /* Доступ до даних поточного стану, якщо він саме той, про який питають. */
    template <class S>
    [[nodiscard]] S* stateIf() noexcept
    {
        return std::get_if<S>(&current_);
    }

    /* Застосувати заявку на перехід, подану поза диспетчеризацією. Усередині
     * обробника викликати не треба — dispatch() зробить це сам. */
    void commit() { applyPending(); }

    [[nodiscard]] std::string_view stateName() const
    {
        return std::visit([](const auto& s) { return s.name(); }, current_);
    }

private:
    void enterCurrent()
    {
        std::visit(
            [&](auto& state) {
                using S = std::remove_reference_t<decltype(state)>;
                if constexpr (HasEnter<S, Ctx>) {
                    state.onEnter(ctx_);
                }
            },
            current_);
    }

    void exitCurrent()
    {
        std::visit(
            [&](auto& state) {
                using S = std::remove_reference_t<decltype(state)>;
                if constexpr (HasExit<S, Ctx>) {
                    state.onExit(ctx_);
                }
            },
            current_);
    }

    /*
     * Порядок кроків переходу зафіксовано тут і ніде більше: дія виходу
     * старого стану, заміна альтернативи, дія входу нового. Цикл потрібен на
     * випадок, коли дія входу сама попросила наступний перехід.
     */
    void applyPending()
    {
        if (applying_) {
            return; /* уже застосовуємо: зовнішній цикл підбере заявку сам */
        }
        applying_ = true;
        while (pending_) {
            auto next = std::move(*pending_);
            pending_.reset();

            exitCurrent();
            current_ = std::move(next);
            enterCurrent();
        }
        applying_ = false;
    }

    Ctx&                        ctx_;
    StateVariant                current_{};
    std::optional<StateVariant> pending_{};
    bool                        applying_{false};
};

} // namespace evse
