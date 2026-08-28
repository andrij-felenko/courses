class PtpPiServo {
public:
    constexpr explicit PtpPiServo(double kp = 0.7, double ki = 0.3, double max_drift_ppb = 100000.0)
        : kp_(kp), ki_(ki), max_drift_ppb_(max_drift_ppb) {}

    [[nodiscard]] double sample(int64_t offset_ns, int64_t local_ts_ns) noexcept {
        if (last_sync_ns_ == 0) {
            last_sync_ns_ = local_ts_ns;
            return 0.0;
        }

        double dt = static_cast<double>(local_ts_ns - last_sync_ns_) / 1e9;
        last_sync_ns_ = local_ts_ns;

        if (dt <= 0.0 || dt > 2.0) {
            dt = 1.0;
        }

        // Оновлення інтегрального стану
        drift_ppb_ += ki_ * static_cast<double>(offset_ns) * dt;
        drift_ppb_ = std::clamp(drift_ppb_, -max_drift_ppb_, max_drift_ppb_);

        // Пропорційно-інтегральний вплив
        double adj = kp_ * static_cast<double>(offset_ns) + drift_ppb_;
        return std::clamp(adj, -max_drift_ppb_, max_drift_ppb_);
    }

    void reset() noexcept {
        drift_ppb_ = 0.0;
        last_sync_ns_ = 0;
    }

private:
    double kp_{0.7};
    double ki_{0.3};
    double drift_ppb_{0.0};
    double max_drift_ppb_{100000.0};
    int64_t last_sync_ns_{0};
};
