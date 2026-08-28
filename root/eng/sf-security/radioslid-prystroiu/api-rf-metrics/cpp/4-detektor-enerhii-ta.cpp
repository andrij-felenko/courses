namespace rf_metrics {

struct DetectionMetrics {
    double bandwidth_hz{0.0};
    double integration_time_s{0.0};
    double target_snr_db{0.0};
    double prob_false_alarm{1e-4};
    double prob_detection{0.0};
    double detection_margin_db{0.0};
};

} // namespace rf_metrics
