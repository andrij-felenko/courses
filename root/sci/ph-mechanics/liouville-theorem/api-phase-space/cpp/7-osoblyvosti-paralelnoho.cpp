// Приклад паралельного кроку ансамблю через OpenMP
void parallel_ensemble_step(
    const IHamiltonianSystem& system,
    IIntegrator& integrator,
    std::vector<PhaseState>& ensemble,
    double dt
) {
    const std::size_t n = ensemble.size();
    #pragma omp parallel for schedule(static)
    for (std::size_t i = 0; i < n; ++i) {
        integrator.step(system, ensemble[i], dt);
    }
}
