struct VolumeMetrics {
    double initial_volume{0.0};
    double current_volume{0.0};
    double jacobian_determinant{1.0};
    double relative_volume_error{0.0};
};

class PhaseVolumeTracker {
public:
    explicit PhaseVolumeTracker(std::size_t num_particles)
        : m_particle_count(num_particles) {}

    [[nodiscard]] VolumeMetrics evaluate_metrics(
        const std::vector<PhaseState>& ensemble
    ) const {
        VolumeMetrics metrics;
        metrics.current_volume = calculate_hull_volume(ensemble);
        metrics.jacobian_determinant = calculate_avg_jacobian(ensemble);
        if (m_initial_volume > 0.0) {
            metrics.relative_volume_error = 
                std::abs(metrics.current_volume - m_initial_volume) / m_initial_volume;
        } else {
            metrics.initial_volume = metrics.current_volume;
        }
        return metrics;
    }

    [[nodiscard]] bool verify_liouville_theorem(
        double jacobian_det, 
        double tolerance = 1e-6
    ) const noexcept {
        return std::abs(jacobian_det - 1.0) <= tolerance;
    }

private:
    std::size_t m_particle_count{0};
    mutable double m_initial_volume{0.0};

    double calculate_hull_volume(const std::vector<PhaseState>& ensemble) const;
    double calculate_avg_jacobian(const std::vector<PhaseState>& ensemble) const;
};
