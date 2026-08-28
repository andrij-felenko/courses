class IHamiltonianSystem {
public:
    virtual ~IHamiltonianSystem() = default;

    [[nodiscard]] virtual double compute_energy(const PhaseState& state) const = 0;
    
    virtual void compute_gradients(
        const PhaseState& state, 
        std::vector<double>& dq_dt, 
        std::vector<double>& dp_dt
    ) const = 0;

    virtual void compute_hessian(
        const PhaseState& state,
        std::vector<double>& hessian_2n_by_2n
    ) const = 0;
};
