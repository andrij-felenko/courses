namespace brownian {

struct MsdAnalysis {
    std::vector<double> time_lags;
    std::vector<double> msd_values;
    std::vector<double> std_errors;
    double estimated_D{0.0};
    double r_squared{0.0};
    double anomalous_exponent{1.0};
};

} // namespace brownian
