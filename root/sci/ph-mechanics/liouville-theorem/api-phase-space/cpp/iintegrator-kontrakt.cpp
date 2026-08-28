class IIntegrator {
public:
    virtual ~IIntegrator() = default;

    virtual void step(
        const IHamiltonianSystem& system,
        PhaseState& state,
        double dt
    ) = 0;

    [[nodiscard]] virtual bool is_symplectic() const noexcept = 0;
};
