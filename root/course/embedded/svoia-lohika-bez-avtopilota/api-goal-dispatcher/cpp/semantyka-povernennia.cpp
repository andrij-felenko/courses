enum class HsmResult : uint8_t {
    Handled,
    Ignored,
    Super,
    Transition
};

class Hsm;
using StateHandler = HsmResult (*)(Hsm& context, const Event& event);

class Hsm {
public:
    explicit Hsm(StateHandler initial_state, void* context = nullptr) noexcept;
    void dispatch(const Event& ev) noexcept;
    void transition_to(StateHandler target) noexcept;
    [[nodiscard]] StateHandler current_state() const noexcept;
    [[nodiscard]] void* context() noexcept;

private:
    StateHandler current_state_{nullptr};
    StateHandler next_state_{nullptr};
    void* user_context_{nullptr};
};
